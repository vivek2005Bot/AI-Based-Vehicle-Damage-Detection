"""Unit tests for OBD-II telemetry parsing, anomaly detection, and DTC extraction."""

import pytest
from ml.obd.anomaly import OBDAnomalyDetector
from ml.obd.csv_parser import parse_obd_csv
from ml.obd.dtc import extract_dtcs_from_text, lookup_dtc
from ml.obd.pipeline import OBDPipeline
from ml.obd.schemas import OBDStatus


def test_dtc_extraction_and_lookup():
    text = "Vehicle stored active trouble code P0300 and secondary code C0035 in ABS module."
    dtcs = extract_dtcs_from_text(text)

    codes = [d.code for d in dtcs]
    assert "P0300" in codes
    assert "C0035" in codes

    entry = lookup_dtc("P0300")
    assert entry.escalate_risk is True
    assert entry.system == "Powertrain"


def test_parse_synthetic_seat_leon_csv():
    csv_content = """Time,Engine Coolant Temperature [°C],Engine RPM [RPM],Vehicle Speed Sensor [km/h]
08:00:01,85.0,2100.0,45.0
08:00:02,86.0,2150.0,47.0
08:00:03,87.0,2200.0,50.0
08:00:04,87.5,2250.0,52.0
08:00:05,88.0,2300.0,55.0
08:00:06,125.0,2300.0,55.0
"""
    parsed, warnings = parse_obd_csv(csv_content.encode("utf-8"), filename="test_seat.csv")
    assert parsed.row_count == 6
    assert "ENGINE_COOLANT_TEMP" in parsed.canonical_data
    assert "ENGINE_RPM" in parsed.canonical_data
    assert "VEHICLE_SPEED" in parsed.canonical_data

    # Run anomaly detector
    detector = OBDAnomalyDetector(contamination=0.1)
    is_anom, score, flagged = detector.analyze(parsed)

    # 125°C coolant temp exceeds 105°C limit
    flagged_pids = [f.pid_name for f in flagged]
    assert "ENGINE_COOLANT_TEMP" in flagged_pids


def test_obd_pipeline_not_provided_state():
    pipeline = OBDPipeline()
    res = pipeline.analyze(None)
    assert res.status == OBDStatus.NOT_PROVIDED
    assert res.anomaly_detected is None
    assert len(res.diagnostic_limitations) > 0
