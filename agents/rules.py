"""Deterministic Automotive Risk Assessment Engine.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 13 and Master Prompt Step 10.
Evaluates:
  1. Visual severity level and structural damage classes
  2. OBD-II telemetry anomaly scores and flagged PIDs
  3. Diagnostic Trouble Code (DTC) severity ratings
Outputs exactly one primary risk class: SAFE, CAUTION, or UNSAFE.
Critical telemetry anomalies escalate risk independently of visual damage.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ml.obd.schemas import OBDAnalysisResult, OBDStatus
from ml.vision.schemas import AssessmentStatus, DamageSeverityLevel, VisionPipelineResult


class RiskClass(str, Enum):
    SAFE = "safe"
    CAUTION = "caution"
    UNSAFE = "unsafe"
    UNAVAILABLE = "unavailable"


class RiskRuleEffect(BaseModel):
    rule_id: str
    rule_name: str
    condition_matched: bool
    escalation_applied: Optional[RiskClass] = None
    reason: str


class RiskAssessment(BaseModel):
    risk_class: RiskClass
    summary: str
    reason_codes: List[str] = Field(default_factory=list)
    evidence_refs: List[Dict[str, Any]] = Field(default_factory=list)
    triggered_rules: List[RiskRuleEffect] = Field(default_factory=list)
    review_required: bool = False
    review_reason: Optional[str] = None
    limitations: List[str] = Field(default_factory=list)
    safety_disclaimer: str = (
        "AI-assisted decision support only. This classification is not a guarantee "
        "of roadworthiness or vehicle safety. Seek qualified technician inspection if concerned."
    )


def evaluate_risk(
    vision_result: Optional[VisionPipelineResult],
    obd_result: Optional[OBDAnalysisResult],
) -> RiskAssessment:
    """Evaluate multimodal evidence and assign deterministic risk classification."""
    triggered_rules: List[RiskRuleEffect] = []
    reason_codes: List[str] = []
    evidence_refs: List[Dict[str, Any]] = []
    limitations: List[str] = []
    review_required = False
    review_reasons: List[str] = []

    current_risk = RiskClass.SAFE

    # 1. Evaluate Visual Findings
    if vision_result is None:
        limitations.append("Visual analysis was not supplied.")
        current_risk = RiskClass.UNAVAILABLE
        review_required = True
        review_reasons.append("Missing visual inspection results.")
    else:
        vis_assessment = getattr(vision_result, "overall_assessment", None)
        vis_sev = vision_result.overall_severity.level
        has_dmg = vision_result.overall_damage_detected
        classes = set(vision_result.primary_damage_classes)
        if vis_assessment == AssessmentStatus.INCONCLUSIVE:
            limitations.append(
                getattr(vision_result, "overall_reason", None) or "Visual assessment inconclusive.")
            current_risk = RiskClass.UNAVAILABLE
            review_required = True
            review_reasons.append("Visual damage assessment inconclusive; manual review required.")
            triggered_rules.append(
                RiskRuleEffect(
                    rule_id="RULE_V0_VISION_INCONCLUSIVE",
                    rule_name="Vision Assessment Inconclusive",
                    condition_matched=True,
                    escalation_applied=RiskClass.UNAVAILABLE,
                    reason="Exterior visual assessment inconclusive; safety cannot be inferred.",
                )
            )
            reason_codes.append("VISUAL_ASSESSMENT_INCONCLUSIVE")
            evidence_refs.append({"source": "vision", "type": "inconclusive",
                                  "reason": getattr(vision_result, "overall_reason", None)})
            # Neutralize downstream visual rules: no safety inference from an inconclusive verdict.
            vis_sev = DamageSeverityLevel.UNAVAILABLE
            has_dmg = False
            classes = set()

        # Rule V1: Critical structural damage -> UNSAFE
        critical_visual_classes = {"bumper_smash", "flat_tire"}
        matched_crit_classes = classes.intersection(critical_visual_classes)
        if matched_crit_classes:
            triggered_rules.append(
                RiskRuleEffect(
                    rule_id="RULE_V1_CRITICAL_COMPONENT_DAMAGE",
                    rule_name="Critical Component / Structural Damage",
                    condition_matched=True,
                    escalation_applied=RiskClass.UNSAFE,
                    reason=f"Detected critical exterior damage: {', '.join(sorted(list(matched_crit_classes)))}.",
                )
            )
            reason_codes.append("VISUAL_CRITICAL_STRUCTURAL_DAMAGE")
            current_risk = RiskClass.UNSAFE
            evidence_refs.append({"source": "vision", "type": "critical_class", "classes": list(matched_crit_classes)})

        # Rule V2: High Severity -> UNSAFE
        elif vis_sev == DamageSeverityLevel.HIGH:
            triggered_rules.append(
                RiskRuleEffect(
                    rule_id="RULE_V2_HIGH_SEVERITY_AREA",
                    rule_name="High Area Damage Severity",
                    condition_matched=True,
                    escalation_applied=RiskClass.UNSAFE,
                    reason=f"Calculated damage severity score ({vision_result.overall_severity.score}) is categorized as HIGH.",
                )
            )
            reason_codes.append("VISUAL_HIGH_SEVERITY_SCORE")
            current_risk = RiskClass.UNSAFE
            evidence_refs.append({"source": "vision", "type": "severity", "score": vision_result.overall_severity.score})

        # Rule V3: Moderate Severity or safety-impacting components -> CAUTION
        elif vis_assessment == AssessmentStatus.DAMAGED and (
                vis_sev == DamageSeverityLevel.MEDIUM or ("broken_light" in classes) or ("glass_crack" in classes)):
            triggered_rules.append(
                RiskRuleEffect(
                    rule_id="RULE_V3_MODERATE_SEVERITY",
                    rule_name="Moderate Exterior Damage or Impaired Visibility",
                    condition_matched=True,
                    escalation_applied=RiskClass.CAUTION,
                    reason="Detected moderate bodywork damage, broken lighting, or windshield crack affecting driving conditions.",
                )
            )
            reason_codes.append("VISUAL_MODERATE_DAMAGE")
            if current_risk != RiskClass.UNSAFE:
                current_risk = RiskClass.CAUTION
            evidence_refs.append({"source": "vision", "type": "moderate_damage", "classes": list(classes)})

        elif has_dmg:
            reason_codes.append("VISUAL_SURFACE_BLEMISHES_ONLY")
            evidence_refs.append({"source": "vision", "type": "minor_damage", "classes": list(classes)})

    # 2. Evaluate OBD-II Telemetry
    if obd_result is None or obd_result.status == OBDStatus.NOT_PROVIDED:
        limitations.append("No OBD-II telemetry log provided. Powertrain and electronic subsystem health unverified.")
        if current_risk == RiskClass.SAFE:
            # Note: Do not declare vehicle completely clear without telemetry
            limitations.append("Risk classification reflects exterior visual appearance only.")
    elif obd_result.status == OBDStatus.COMPLETED:
        # Check active DTCs
        critical_dtcs = [d for d in obd_result.dtcs if d.escalate_risk or d.severity == "critical"]
        major_dtcs = [d for d in obd_result.dtcs if d.severity in ("major", "moderate") and not d.escalate_risk]

        # Rule O1: Critical Safety DTCs (Airbag, ABS, Misfire, Overtemp) -> Mandatory UNSAFE
        if critical_dtcs:
            dtc_codes = [d.code for d in critical_dtcs]
            triggered_rules.append(
                RiskRuleEffect(
                    rule_id="RULE_O1_CRITICAL_DTC_ESCALATION",
                    rule_name="Critical Diagnostic Trouble Code Escalation",
                    condition_matched=True,
                    escalation_applied=RiskClass.UNSAFE,
                    reason=f"Active critical DTCs detected: {', '.join(dtc_codes)} ({critical_dtcs[0].description}).",
                )
            )
            reason_codes.append("OBD_CRITICAL_DTC_ACTIVE")
            current_risk = RiskClass.UNSAFE
            review_required = True
            review_reasons.append(f"Immediate mechanical review required for diagnostic codes: {', '.join(dtc_codes)}.")
            evidence_refs.append({"source": "obd", "type": "critical_dtcs", "codes": dtc_codes})

        elif major_dtcs:
            dtc_codes = [d.code for d in major_dtcs]
            triggered_rules.append(
                RiskRuleEffect(
                    rule_id="RULE_O2_MAJOR_DTC_WARNING",
                    rule_name="Powertrain DTC Advisory",
                    condition_matched=True,
                    escalation_applied=RiskClass.CAUTION,
                    reason=f"Active advisory DTCs detected: {', '.join(dtc_codes)}.",
                )
            )
            reason_codes.append("OBD_ADVISORY_DTC_ACTIVE")
            if current_risk != RiskClass.UNSAFE:
                current_risk = RiskClass.CAUTION
            evidence_refs.append({"source": "obd", "type": "advisory_dtcs", "codes": dtc_codes})

        # Rule O3: Statistical Telemetry Anomaly from Isolation Forest -> CAUTION or UNSAFE
        if obd_result.anomaly_detected and not critical_dtcs:
            flagged_names = [f.pid_name for f in obd_result.flagged_pids]
            triggered_rules.append(
                RiskRuleEffect(
                    rule_id="RULE_O3_TELEMETRY_ANOMALY_ESCALATION",
                    rule_name="Isolation Forest Telemetry Outlier Escalation",
                    condition_matched=True,
                    escalation_applied=RiskClass.CAUTION,
                    reason=f"Unsupervised telemetry anomaly flagged across PIDs: {', '.join(flagged_names[:3])}.",
                )
            )
            reason_codes.append("OBD_TELEMETRY_ANOMALY_FLAGGED")
            if current_risk != RiskClass.UNSAFE:
                current_risk = RiskClass.CAUTION
            review_required = True
            review_reasons.append("Unusual sensor readings flagged by anomaly detector.")
            evidence_refs.append({"source": "obd", "type": "anomaly_pids", "pids": flagged_names})

    # Formulate User-Facing Summary
    if current_risk == RiskClass.UNSAFE:
        summary = (
            "VEHICLE CLASSIFIED AS UNSAFE. Significant driving or mechanical hazards detected. "
            + "; ".join([r.reason for r in triggered_rules if r.escalation_applied == RiskClass.UNSAFE])
        )
    elif current_risk == RiskClass.CAUTION:
        summary = (
            "VEHICLE CLASSIFIED AS CAUTION. Moderate damage or telemetry irregularities observed. "
            + "; ".join([r.reason for r in triggered_rules if r.escalation_applied == RiskClass.CAUTION])
        )
    elif current_risk == RiskClass.SAFE:
        summary = (
            "VEHICLE CLASSIFIED AS SAFE FOR TYPICAL CONDITIONS. No high-risk structural defects or "
            "critical powertrain faults were detected by configured checks."
        )
    else:
        summary = "RISK ASSESSMENT UNAVAILABLE. Key diagnostic inputs were incomplete."

    return RiskAssessment(
        risk_class=current_risk,
        summary=summary,
        reason_codes=reason_codes,
        evidence_refs=evidence_refs,
        triggered_rules=triggered_rules,
        review_required=review_required,
        review_reason="; ".join(review_reasons) if review_reasons else None,
        limitations=limitations,
    )
