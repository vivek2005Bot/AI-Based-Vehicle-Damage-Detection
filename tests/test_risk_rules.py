"""Unit tests for deterministic Risk Engine rules."""

import pytest
from agents.rules import RiskClass, evaluate_risk
from ml.obd.schemas import DTCEntry, OBDAnalysisResult, OBDStatus
from ml.vision.schemas import (
    AssessmentStatus,
    DamageSeverityLevel,
    SeverityAssessment,
    VisionPipelineResult,
)


def test_obd_critical_dtc_escalates_to_unsafe():
    # Intact exterior (no damage, valid model negative)
    vision = VisionPipelineResult(
        inspection_id="insp_1",
        overall_damage_detected=False,
        overall_assessment=AssessmentStatus.NO_DAMAGE,
        overall_severity=SeverityAssessment(score=0.0, level=DamageSeverityLevel.LOW),
        primary_damage_classes=[],
    )

    # Telemetry has critical cylinder misfire DTC P0300
    obd = OBDAnalysisResult(
        status=OBDStatus.COMPLETED,
        anomaly_detected=True,
        dtcs=[
            DTCEntry(
                code="P0300",
                system="Powertrain",
                description="Random/Multiple Cylinder Misfire Detected",
                severity="critical",
                escalate_risk=True,
            )
        ],
    )

    risk = evaluate_risk(vision_result=vision, obd_result=obd)
    assert risk.risk_class == RiskClass.UNSAFE
    assert "OBD_CRITICAL_DTC_ACTIVE" in risk.reason_codes
    assert risk.review_required is True


def test_critical_visual_damage_escalates_to_unsafe():
    # Severe bumper smash
    vision = VisionPipelineResult(
        inspection_id="insp_2",
        overall_damage_detected=True,
        overall_assessment=AssessmentStatus.DAMAGED,
        overall_severity=SeverityAssessment(score=0.35, level=DamageSeverityLevel.HIGH),
        primary_damage_classes=["bumper_smash"],
    )

    risk = evaluate_risk(vision_result=vision, obd_result=None)
    assert risk.risk_class == RiskClass.UNSAFE
    assert "VISUAL_CRITICAL_STRUCTURAL_DAMAGE" in risk.reason_codes


def test_intact_vehicle_safe_with_disclaimer():
    vision = VisionPipelineResult(
        inspection_id="insp_3",
        overall_damage_detected=False,
        overall_assessment=AssessmentStatus.NO_DAMAGE,
        overall_severity=SeverityAssessment(score=0.0, level=DamageSeverityLevel.LOW),
        primary_damage_classes=[],
    )
    risk = evaluate_risk(vision_result=vision, obd_result=None)
    assert risk.risk_class == RiskClass.SAFE
    assert len(risk.safety_disclaimer) > 0


def test_inconclusive_vision_is_not_safe():
    """INCONCLUSIVE must map to UNAVAILABLE + review required, never SAFE."""
    vision = VisionPipelineResult(
        inspection_id="insp_4",
        overall_damage_detected=False,
        overall_assessment=AssessmentStatus.INCONCLUSIVE,
        overall_reason="Damage detector unavailable; manual review required.",
        overall_severity=SeverityAssessment(score=None, level=DamageSeverityLevel.UNAVAILABLE),
        primary_damage_classes=[],
    )
    risk = evaluate_risk(vision_result=vision, obd_result=None)
    assert risk.risk_class == RiskClass.UNAVAILABLE
    assert risk.risk_class != RiskClass.SAFE
    assert risk.review_required is True
    assert "VISUAL_ASSESSMENT_INCONCLUSIVE" in risk.reason_codes
    assert "RULE_V0_VISION_INCONCLUSIVE" in [r.rule_id for r in risk.triggered_rules]
