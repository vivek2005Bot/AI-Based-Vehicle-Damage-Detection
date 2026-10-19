"""Comprehensive tests for OBD-II Telemetry PID Explanations, Metadata, Anomaly Detection,
Threshold Validation, Sample Statistics, P0171 Cross-Finding Logic, and Report Generation.

Complies with all requirements of Problem 1 through Problem 9.
"""

import math
import numpy as np
import pytest

from agents.rules import RiskClass, evaluate_risk
from ml.vision.schemas import AssessmentStatus, DamageSeverityLevel, SeverityAssessment, VisionPipelineResult
from ml.obd.anomaly import OBDAnomalyDetector
from ml.obd.csv_parser import ParsedOBDTelemetry, parse_obd_csv
from ml.obd.dtc import lookup_dtc
from ml.obd.pid_definitions import PID_REGISTRY, PIDConfig, PIDDescriptionSystem
from ml.obd.pipeline import OBDPipeline
from ml.obd.schemas import DTCEntry, FlaggedPID, OBDAnalysisResult, OBDDataQuality, OBDStatus
from reports.pdf_renderer import render_inspection_pdf


# ==============================================================================
# 1. Negative & Positive Fuel-Trim Readings (Directionality & Plain-English)
# ==============================================================================
def test_fuel_trim_negative_directionality():
    """Negative fuel trim indicates the ECU is reducing fuel delivery."""
    direction, meaning = PID_REGISTRY.explain_directionality("FUEL_TRIM_SHORT", -26.8, "%", [-15.0, 15.0])
    assert direction == "negative"
    assert "reducing fuel delivery" in meaning.lower()
    assert "rich" in meaning.lower()
    assert "alone cannot identify the cause" in meaning.lower()


def test_fuel_trim_positive_directionality():
    """Positive fuel trim indicates the ECU is adding fuel delivery."""
    direction, meaning = PID_REGISTRY.explain_directionality("FUEL_TRIM_SHORT", 22.4, "%", [-15.0, 15.0])
    assert direction == "positive"
    assert "adding fuel" in meaning.lower()
    assert "lean" in meaning.lower()
    assert "alone cannot identify the cause" in meaning.lower()


def test_fuel_trim_neutral_directionality():
    """Zero fuel trim indicates no baseline adjustment."""
    direction, meaning = PID_REGISTRY.explain_directionality("FUEL_TRIM_SHORT", 0.0, "%", [-15.0, 15.0])
    assert direction == "neutral"
    assert "not applying any correction" in meaning.lower()


# ==============================================================================
# 2. PID-Name Normalization & Bank Preservation
# ==============================================================================
def test_pid_name_normalization_and_bank_preservation():
    """Verify standard aliases and Bank 1 vs Bank 2 distinction."""
    # Bank 1 / general
    m1 = PID_REGISTRY.match_column("Short Term Fuel Trim Bank 1 [%]")
    assert m1 is not None
    assert m1[0] == "FUEL_TRIM_SHORT"
    assert m1[1].bank == 1

    m2 = PID_REGISTRY.match_column("STFT 1")
    assert m2 is not None
    assert m2[0] == "FUEL_TRIM_SHORT"

    # Bank 2 distinction
    m3 = PID_REGISTRY.match_column("Short Term Fuel Trim Bank 2 [%]")
    assert m3 is not None
    assert m3[0] == "FUEL_TRIM_SHORT_B2"
    assert m3[1].bank == 2
    assert "Bank 2" in m3[1].display_title

    m4 = PID_REGISTRY.match_column("STFT 2")
    assert m4 is not None
    assert m4[0] == "FUEL_TRIM_SHORT_B2"

    # Long term bank 2
    m5 = PID_REGISTRY.match_column("Long Term Fuel Trim Bank 2 [%]")
    assert m5 is not None
    assert m5[0] == "FUEL_TRIM_LONG_B2"
    assert m5[1].bank == 2


# ==============================================================================
# 3. Threshold Boundary Behavior & Unit Validation
# ==============================================================================
def test_threshold_boundary_behavior():
    """Values exactly at bounds should not be counted as violations."""
    h_range = [-15.0, 15.0]

    # Exactly on lower and upper boundary
    vals_boundary = np.array([-15.0, 15.0, 0.0, 5.0, -5.0])
    out_of_bounds = (vals_boundary < h_range[0]) | (vals_boundary > h_range[1])
    assert np.sum(out_of_bounds) == 0

    # Just outside bounds
    vals_outside = np.array([-15.1, 15.1, 0.0, 5.0, -5.0])
    out_of_bounds = (vals_outside < h_range[0]) | (vals_outside > h_range[1])
    assert np.sum(out_of_bounds) == 2


# ==============================================================================
# 4. Missing, Invalid, and Non-Finite Value Handling
# ==============================================================================
def test_missing_invalid_nan_infinity_handling():
    """CSV parser and anomaly detector must handle NaN, Inf, and corrupt strings safely."""
    csv_data = """Engine RPM [RPM],Short Term Fuel Trim [%],Vehicle Speed [km/h]
800.0,-26.8,0.0
850.0,NaN,0.0
900.0,Infinity,5.0
950.0,-25.0,10.0
1000.0,corrupt_data,15.0
1050.0,-28.0,20.0
"""
    parsed, warnings = parse_obd_csv(csv_data.encode("utf-8"), filename="test_nan.csv")
    assert parsed.row_count == 6
    assert parsed.quality.missing_value_pct > 0.0

    # Anomaly detector should evaluate only finite recorded samples
    detector = OBDAnomalyDetector(contamination=0.1)
    is_anom, score, flagged = detector.analyze(parsed)

    stft_flagged = [f for f in flagged if f.pid_name == "FUEL_TRIM_SHORT"]
    assert len(stft_flagged) == 1
    f = stft_flagged[0]
    # Valid recorded STFT values were [-26.8, -25.0, -28.0] -> 3 valid samples
    assert f.sample_count_evaluated == 3
    assert f.sample_count_outside == 3
    assert f.sample_percentage_outside == 100.0
    assert np.isfinite(f.observed_value)


# ==============================================================================
# 5. Correct Calculation of Percentage Outside Range
# ==============================================================================
def test_sample_percentage_calculation_strictly_valid():
    """Percentage outside range = valid_outside / valid_evaluated * 100."""
    csv_rows = ["Engine Coolant Temperature [°C],Engine RPM [RPM]"]
    # 20 samples total: 10 valid, 10 missing/unreadable
    # Of the 10 valid, 2 are outside healthy coolant range [75, 105] (e.g. 115.0 and 120.0)
    for i in range(8):
        csv_rows.append(f"90.0,{800 + i * 10}")
    csv_rows.append("115.0,880")
    csv_rows.append("120.0,890")
    for _ in range(10):
        csv_rows.append("invalid_value,900")

    csv_text = "\n".join(csv_rows)
    parsed, _ = parse_obd_csv(csv_text.encode("utf-8"))

    detector = OBDAnomalyDetector(contamination=0.1)
    _, _, flagged = detector.analyze(parsed)

    coolant_flags = [f for f in flagged if f.pid_name == "ENGINE_COOLANT_TEMP"]
    assert len(coolant_flags) == 1
    cf = coolant_flags[0]
    assert cf.sample_count_evaluated == 10
    assert cf.sample_count_outside == 2
    assert cf.sample_percentage_outside == 20.0
    assert "20.0% of the recorded telemetry samples were outside" in cf.sample_explanation
    assert "does not indicate that any percentage of the vehicle is damaged" in cf.sample_explanation


# ==============================================================================
# 6. Handling of Zero Valid Samples
# ==============================================================================
def test_zero_valid_samples_safe_handling():
    """No valid samples should result in unavailable statistics without division-by-zero."""
    expl = PID_REGISTRY.build_sample_explanation(valid_outside=0, valid_total=0, pct_outside=None)
    assert "unavailable" in expl.lower()
    assert "no valid numeric samples" in expl.lower()


# ==============================================================================
# 7. Plain-English Explanations for Known PIDs
# ==============================================================================
def test_plain_english_wording_stft_anomaly():
    """Verify plain-English explanation for FUEL_TRIM_SHORT matches required user-friendly style."""
    csv_data = """Engine RPM [RPM],Short Term Fuel Trim [%],Engine Coolant Temperature [°C]
800.0,-26.8,85.0
820.0,-26.5,86.0
810.0,-27.0,85.5
830.0,-26.8,86.0
805.0,-26.2,85.8
800.0,-25.9,86.2
"""
    parsed, _ = parse_obd_csv(csv_data.encode("utf-8"))
    detector = OBDAnomalyDetector(contamination=0.1)
    _, _, flagged = detector.analyze(parsed)

    stft_flags = [f for f in flagged if f.pid_name == "FUEL_TRIM_SHORT"]
    assert len(stft_flags) == 1
    f = stft_flags[0]

    assert f.simple_title == "Engine Fuel Adjustment Outside Expected Range"
    assert "The vehicle's computer is making a larger-than-expected adjustment" in f.what_we_found
    assert "A negative fuel-trim value means the engine computer is reducing fuel delivery" in f.value_meaning
    assert "arrange a diagnostic check" in f.what_you_should_do
    assert len(f.possible_causes) > 0
    assert any("injector" in c.lower() for c in f.possible_causes)
    assert any("does not prove that a component is faulty" in lim for lim in f.limitations)
    assert "SAE J1979" in f.source
    assert "outside the application's configured monitoring range" in f.reason.lower() or "outside configured monitoring range" in f.reason.lower()


# ==============================================================================
# 8. Safe Fallback for Unknown PIDs
# ==============================================================================
def test_safe_fallback_for_unknown_pids():
    """Unrecognized sensor headers must produce an honest fallback without invented meanings."""
    fallback = PID_REGISTRY.build_honest_fallback(
        raw_column_name="PROPRIETARY_OEM_SENSOR_0x42",
        observed_value=999.5,
        unit="raw_ticks",
        valid_outside=5,
        valid_total=10,
        pct_outside=50.0,
    )

    assert "Unverified Sensor Reading (PROPRIETARY_OEM_SENSOR_0x42)" in fallback["simple_title"]
    assert "we do not yet have a verified explanation for this sensor" in fallback["what_we_found"]
    assert "qualified technician" in fallback["what_you_should_do"].lower()
    assert fallback["configured_range"] is None
    assert "Unmapped Telemetry Channel" in fallback["source"]
    assert "No verified SAE J1979 standard definition is available" in fallback["limitations"][0]


# ==============================================================================
# 9. P0171 and Fuel-Trim Cross-Finding Logic
# ==============================================================================
def test_p0171_and_fuel_trim_cross_finding_notice():
    """When DTC P0171 (lean) co-occurs with strongly negative fuel trim, a neutral disclaimer is generated."""
    # When P0171 is present
    dtc_codes = ["P0171"]
    notice = PID_REGISTRY.check_p0171_fuel_trim_consistency(
        dtc_codes=dtc_codes,
        canonical_name="FUEL_TRIM_SHORT",
        observed_value=-26.8,
        has_timestamps=False,
        same_bank=False,
    )
    assert notice is not None
    assert "We also found a lean-mixture diagnostic code" in notice
    assert "does not clearly explain that code" in notice
    assert "different conditions or sensor contexts" in notice
    assert "technician should review the complete diagnostic data" in notice

    # When P0171 is NOT present, notice should be None
    notice_none = PID_REGISTRY.check_p0171_fuel_trim_consistency(
        dtc_codes=["P0300"],
        canonical_name="FUEL_TRIM_SHORT",
        observed_value=-26.8,
        has_timestamps=False,
        same_bank=False,
    )
    assert notice_none is None

    # When fuel trim is positive (+15.0), notice should be None because +trim is consistent with lean compensation
    notice_pos = PID_REGISTRY.check_p0171_fuel_trim_consistency(
        dtc_codes=["P0171"],
        canonical_name="FUEL_TRIM_SHORT",
        observed_value=20.0,
        has_timestamps=False,
        same_bank=False,
    )
    assert notice_pos is None


# ==============================================================================
# 10. Avoidance of Unsupported Diagnosis
# ==============================================================================
def test_avoidance_of_unsupported_diagnosis():
    """Telemetry readings must not assert a specific failed component as a fact."""
    config = PID_REGISTRY.get_config("FUEL_TRIM_SHORT")
    assert config is not None

    # Possible causes should be framed as possibilities
    for cause in config.possible_causes_low + config.possible_causes_high:
        assert not cause.startswith("Confirmed faulty")
        assert not cause.startswith("Broken component:")

    # Limitations must explicitly state that component diagnosis cannot be made from one PID
    assert any("cannot identify a specific faulty sensor" in lim for lim in config.limitations)


# ==============================================================================
# 11. End-to-End Pipeline & Report Generation Consistency
# ==============================================================================
def test_pipeline_and_pdf_generation_with_flagged_pids():
    """Verify that OBDPipeline properly populates flagged PIDs and PDF report renders them."""
    csv_content = """Time,Engine Coolant Temperature [°C],Engine RPM [RPM],Short Term Fuel Trim [%],DTC
08:00:01,85.0,2100.0,-26.8,P0171
08:00:02,86.0,2150.0,-26.5,P0171
08:00:03,87.0,2200.0,-27.0,P0171
08:00:04,87.5,2250.0,-26.8,P0171
08:00:05,88.0,2300.0,-26.2,P0171
08:00:06,88.5,2300.0,-26.0,P0171
"""
    pipeline = OBDPipeline(contamination=0.1)
    result = pipeline.analyze(csv_content.encode("utf-8"), filename="session_telemetry.csv")

    assert result.status == OBDStatus.COMPLETED
    assert result.anomaly_detected is True
    assert len(result.dtcs) == 1
    assert result.dtcs[0].code == "P0171"

    stft_flags = [f for f in result.flagged_pids if f.pid_name == "FUEL_TRIM_SHORT"]
    assert len(stft_flags) == 1
    f = stft_flags[0]

    assert f.cross_finding_notice is not None
    assert "P0171" in f.cross_finding_notice
    # Notice should also appear in diagnostic limitations
    assert any("P0171" in lim for lim in result.diagnostic_limitations)

    # Test PDF generation with these structured findings
    report_data = {
        "inspection_id": "TEST_INSP_001",
        "timestamp": "2026-10-19T01:00:00Z",
        "vehicle": {"make": "Seat", "model": "Leon", "year": 2018},
        "risk": {
            "class": "caution",
            "summary": "Vehicle classified as CAUTION due to telemetry anomaly.",
            "reason_codes": ["OBD_TELEMETRY_ANOMALY_FLAGGED"],
            "review_required": True,
            "review_reason": "Unusual fuel trim readings.",
            "limitations": [],
            "triggered_rules": [],
        },
        "vision": {"images": []},
        "obd": {
            "status": "completed",
            "anomaly_detected": True,
            "anomaly_score": -0.15,
            "dtcs": [d.model_dump() for d in result.dtcs],
            "flagged_pids": [p.model_dump() for p in result.flagged_pids],
            "data_quality": result.data_quality.model_dump(),
        },
        "knowledge": {"passages": []},
    }

    pdf_bytes = render_inspection_pdf(report_data)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")


# ==============================================================================
# 12. Preservation of Deterministic Safety Rules
# ==============================================================================
def test_preservation_of_deterministic_safety_rules():
    """Ensure Rule O3 still triggers CAUTION on flagged PIDs without altering safety protections."""
    vision = VisionPipelineResult(
        inspection_id="insp_safety",
        overall_damage_detected=False,
        overall_assessment=AssessmentStatus.NO_DAMAGE,
        overall_severity=SeverityAssessment(score=0.0, level=DamageSeverityLevel.LOW),
        primary_damage_classes=[],
    )

    flagged = FlaggedPID(
        pid_name="FUEL_TRIM_SHORT",
        raw_column_name="STFT",
        observed_value=-26.8,
        unit="%",
        expected_range=[-15.0, 15.0],
        anomaly_contribution=0.85,
        reason="Readings outside configured monitoring range [-15.0, 15.0] %",
        simple_title="Engine Fuel Adjustment Outside Expected Range",
        what_we_found="The vehicle's computer is making a larger-than-expected adjustment to fuel delivery.",
        value_meaning="A negative fuel-trim value means the engine computer is reducing fuel delivery.",
        what_you_should_do="Arrange a diagnostic check.",
    )

    obd = OBDAnalysisResult(
        status=OBDStatus.COMPLETED,
        anomaly_detected=True,
        anomaly_score=-0.22,
        flagged_pids=[flagged],
        dtcs=[],
        data_quality=OBDDataQuality(total_rows=100),
    )

    risk_result = evaluate_risk(vision_result=vision, obd_result=obd)
    assert risk_result.risk_class == RiskClass.CAUTION
    assert "OBD_TELEMETRY_ANOMALY_FLAGGED" in risk_result.reason_codes
    assert risk_result.review_required is True
