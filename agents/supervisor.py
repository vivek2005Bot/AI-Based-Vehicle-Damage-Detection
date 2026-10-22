"""LangGraph Supervisor & Agent Workflow Orchestration.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 11 and Master Prompt Step 8.
Coordinates the 4 specialist agents:
  1. Vision Agent (images -> structured damage findings)
  2. OBD Analytics Agent (CSV -> anomalies & DTCs)
  3. RAG Knowledge Agent (findings -> grounded citations)
  4. Risk Engine Agent (multimodal fusion -> Safe/Caution/Unsafe)
Compiles final structured report payload.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from PIL import Image

from agents.obd_agent import OBDAgent
from agents.rag_agent import RAGAgent
from agents.risk_agent import RiskAgent
from agents.rules import RiskClass
from agents.state import InspectionGraphState
from agents.vision_agent import VisionAgent
from ml.cost_estimation import (
    ComponentDamageSummary,
    ComponentIdentificationMethod,
    VehicleCostContext,
    calculate_extent_category,
    get_component_metadata,
    infer_damage_summary_from_detections,
    repair_cost_estimator,
)
from ml.vision.schemas import AssessmentStatus, DamageSeverityLevel


class InspectionSupervisor:
    """Orchestrator coordinating inspection agents and compiling final reports."""

    def __init__(self, filter_threshold: float = 0.85, top_k_rag: int = 5):
        self.vision_agent = VisionAgent(filter_threshold=filter_threshold)
        self.obd_agent = OBDAgent()
        self.rag_agent = RAGAgent(top_k=top_k_rag)
        self.risk_agent = RiskAgent()

    def run_workflow(
        self,
        state: InspectionGraphState,
        image_objects: List[Union[str, bytes, Image.Image]],
        csv_bytes: Optional[Union[bytes, str]] = None,
    ) -> InspectionGraphState:
        """Execute complete inspection graph with error boundary and auditability."""
        start_time = time.perf_counter()
        state.status = "processing"
        state.current_stage = "starting"

        # 1. Vision Analysis (Required)
        state.current_stage = "vision_analysis"
        state = self.vision_agent.run(state, image_objects)

        # 2. OBD Telemetry Analysis (Optional)
        state.current_stage = "obd_analysis"
        state = self.obd_agent.run(state, csv_bytes)

        # 3. RAG Knowledge Retrieval
        state.current_stage = "knowledge_retrieval"
        state = self.rag_agent.run(state)

        # 4. Multimodal Risk Assessment
        state.current_stage = "risk_assessment"
        state = self.risk_agent.run(state)

        # 5. Compile Final Report Payload
        state.current_stage = "report_generation"
        state.report_payload = self._compile_report(state, round((time.perf_counter() - start_time) * 1000.0, 2))
        state.completed_stages.append("report_generation")

        state.status = "completed_with_warnings" if state.warnings else "completed"
        state.current_stage = "finished"
        return state

    def _compile_report(self, state: InspectionGraphState, total_duration_ms: float) -> Dict[str, Any]:
        """Assemble structured report JSON compliant with reports/json_schema.json."""
        timestamp = datetime.now(timezone.utc).isoformat()

        # Overall damage detected
        dmg_detected = False
        summary_text = "Inspection complete."
        overall_assessment = AssessmentStatus.INCONCLUSIVE.value
        overall_reason: Optional[str] = None
        # De-duplicate limitations and never repeat the overall_reason text
        # (it is already surfaced via assessment_reason/summary).
        overall_limitations: List[str] = []
        for w in list(state.warnings):
            if w and w not in overall_limitations:
                overall_limitations.append(w)
        if state.vision_result:
            for w in (state.vision_result.warnings or []):
                if w and w not in overall_limitations:
                    overall_limitations.append(w)
            dmg_detected = state.vision_result.overall_damage_detected
            overall_assessment = getattr(
                state.vision_result, "overall_assessment", AssessmentStatus.INCONCLUSIVE
            ).value
            overall_reason = getattr(state.vision_result, "overall_reason", None)
            if overall_reason:
                overall_limitations = [
                    lim for lim in overall_limitations if lim != overall_reason
                ]
            classes_str = ", ".join(state.vision_result.primary_damage_classes)
            if overall_assessment == AssessmentStatus.DAMAGED.value or dmg_detected:
                summary_text = f"Exterior vehicle damage detected: {classes_str or 'structural blemishes'}."
            elif overall_assessment == AssessmentStatus.NO_DAMAGE.value:
                summary_text = "No exterior vehicle damage detected by computer vision filter."
            else:
                summary_text = (
                    "Unable to determine damage status from images — manual review required."
                )

        # Severity
        sev_dict = {
            "score": None,
            "level": "unavailable",
            "method": "mask_area_ratio_weighted_by_class",
            "calibrated": False,
        }
        if state.vision_result:
            base_score = state.vision_result.overall_severity.score
            base_level = state.vision_result.overall_severity.level.value
            method = state.vision_result.overall_severity.method
            calibrated = state.vision_result.overall_severity.calibrated

            # Harmonize severity score & level with deterministic risk assessment:
            # If vehicle is classified as UNSAFE (critical structural damage, shattered glass, flat tire, critical DTC),
            # vehicle severity must reflect HIGH severity (>= 75 / 100), never contradictory LOW (4-10 / 100).
            # If vehicle is CAUTION (dent, crack, broken lighting/mirrors), severity reflects MEDIUM (35 / 100).
            # If vehicle is SAFE (intact), severity reflects LOW (0 / 100).
            if state.risk_result and state.risk_result.risk_class == RiskClass.UNSAFE:
                harmonized_level = "high"
                harmonized_score = round(max(base_score or 0.0, 0.75), 4)
            elif state.risk_result and state.risk_result.risk_class == RiskClass.CAUTION:
                harmonized_level = "medium"
                harmonized_score = round(min(0.60, max(base_score or 0.0, 0.35)), 4)
            elif not state.vision_result.overall_damage_detected and (not state.obd_result or not state.obd_result.anomaly_detected):
                harmonized_level = "low"
                harmonized_score = 0.0
            else:
                harmonized_level = base_level
                harmonized_score = base_score

            sev_dict = {
                "score": harmonized_score,
                "level": harmonized_level,
                "method": method,
                "calibrated": calibrated,
            }

        # Images
        images_list = []
        if state.vision_result:
            file_ids = list(state.image_file_ids or [])
            for idx, img in enumerate(state.vision_result.images):
                fid = file_ids[idx] if idx < len(file_ids) else None
                w = img.transforms.original_width if img.transforms else None
                h = img.transforms.original_height if img.transforms else None
                images_list.append({
                    "image_id": img.image_id,
                    "file_id": fid,
                    "image_url": f"/api/v1/inspections/{state.inspection_id}/images/{fid}/content" if fid else None,
                    "filename": img.filename,
                    "original_width": w,
                    "original_height": h,
                    "damage_detected": img.damage_detected,
                    "assessment": getattr(img, "assessment", AssessmentStatus.INCONCLUSIVE).value,
                    "assessment_reason": getattr(img, "assessment_reason", None),
                    "damage_probability": img.damage_probability,
                    "classifications": [c.model_dump() for c in img.classifications],
                    "detections": [d.model_dump() for d in img.detections],
                    "severity": img.severity.model_dump(),
                    "stage_status": {k: v.value for k, v in img.stage_status.items()},
                    # warnings must not repeat assessment_reason verbatim —
                    # clients render both fields and would show it twice.
                    "warnings": [
                        w for w in (img.warnings or [])
                        if w and w != getattr(img, "assessment_reason", None)
                    ],
                })

        # OBD
        obd_dict: Dict[str, Any] = {
            "status": "not_provided",
            "anomaly_detected": None,
            "anomaly_score": None,
            "flagged_pids": [],
            "dtcs": [],
            "data_quality": {"warnings": []},
            "diagnostic_limitations": [],
        }
        if state.obd_result:
            obd_dict = {
                "status": state.obd_result.status.value,
                "anomaly_detected": state.obd_result.anomaly_detected,
                "anomaly_score": state.obd_result.anomaly_score,
                "flagged_pids": [p.model_dump() for p in state.obd_result.flagged_pids],
                "dtcs": [d.model_dump() for d in state.obd_result.dtcs],
                "data_quality": state.obd_result.data_quality.model_dump(),
                "diagnostic_limitations": state.obd_result.diagnostic_limitations,
            }

        # Risk
        risk_dict: Dict[str, Any] = {
            "class": "unavailable",
            "summary": "Risk evaluation incomplete.",
            "reason_codes": [],
            "review_required": True,
            "review_reason": "Incomplete evaluation.",
            "limitations": [],
        }
        if state.risk_result:
            risk_dict = {
                "class": state.risk_result.risk_class.value,
                "summary": state.risk_result.summary,
                "reason_codes": state.risk_result.reason_codes,
                "review_required": state.risk_result.review_required,
                "review_reason": state.risk_result.review_reason,
                "limitations": state.risk_result.limitations,
                "triggered_rules": [r.model_dump() for r in state.risk_result.triggered_rules],
            }

        # Knowledge / RAG
        rag_dict: Dict[str, Any] = {
            "status": "no_sources_available",
            "citations": [],
            "passages": [],
            "summary_guidance": "No verified guidance available.",
        }
        if state.rag_result:
            rag_dict = {
                "status": state.rag_result.status,
                "citations": [c.model_dump() for c in state.rag_result.citations],
                "passages": [p.model_dump() for p in state.rag_result.passages],
                "summary_guidance": state.rag_result.summary_guidance,
            }

        # 5. Vehicle Repair Cost Estimate (Only for damaged vehicles)
        estimate_dict: Optional[Dict[str, Any]] = None
        if dmg_detected:
            try:
                images = state.vision_result.images if (state.vision_result and state.vision_result.images) else []
                (
                    primary_comp,
                    primary_dmg,
                    extent_cat,
                    rel_area,
                    distinct_cnt,
                    top_finding_id,
                    dmg_conf,
                    comp_conf,
                ) = infer_damage_summary_from_detections(images)

                comp_meta = get_component_metadata(primary_comp)
                damage_summary = ComponentDamageSummary(
                    component_id=primary_comp,
                    component_display_name=comp_meta.get("display_name", primary_comp.replace("_", " ").title()),
                    component_confidence=comp_conf,
                    damage_type=primary_dmg,
                    damage_confidence=dmg_conf,
                    component_identification_method=ComponentIdentificationMethod.POSITIONAL_HEURISTIC,
                    component_verification_required=True,
                    extent_category=extent_cat,
                    damage_area_ratio=rel_area,
                    distinct_regions_count=distinct_cnt,
                )

                v_ctx = VehicleCostContext(
                    make=state.vehicle_info.make,
                    model=state.vehicle_info.model,
                    year=state.vehicle_info.year,
                )

                est_resp = repair_cost_estimator.estimate_cost(
                    inspection_id=state.inspection_id,
                    damage_summary=damage_summary,
                    vehicle_context=v_ctx,
                    finding_id=top_finding_id,
                )
                estimate_dict = est_resp.model_dump()
            except Exception as est_err:
                pass

        return {
            "schema_version": "1.0.0",
            "inspection_id": state.inspection_id,
            "job_id": state.job_id,
            "generated_at": timestamp,
            "overall": {
                "damage_detected": dmg_detected,
                "assessment": overall_assessment,
                "assessment_reason": overall_reason,
                "status": "completed",
                "summary": summary_text,
                "limitations": overall_limitations,
            },
            "vehicle": state.vehicle_info.model_dump(),
            "images": images_list,
            "severity": sev_dict,
            "obd": obd_dict,
            "risk": risk_dict,
            "knowledge": rag_dict,
            "estimate": estimate_dict,
            "model_metadata": {
                "vision_pipeline_version": "1.2.0",
                "filter_model": "classical_cv_v1",
                "classifier_model": "classical_cv_v1",
                "detector_model": "classical_cv_v1",
                "segmenter_model": "classical_cv_contour_v1",
                "obd_model": "isolation_forest",
                "cardd_enabled": bool(getattr(state.vision_result, "cardd_enabled", False)),
                "cardd_available": bool(getattr(state.vision_result, "cardd_available", False)),
                "cardd_model": getattr(state.vision_result, "cardd_model", None),
            },
            "processing": {
                "total_duration_ms": total_duration_ms,
                "completed_stages": state.completed_stages,
            },
            "warnings": state.warnings,
            "errors": state.errors,
            "disclaimer": (
                "AI-assisted decision support only. This report does not certify roadworthiness "
                "or replace a professional mechanical inspection."
            ),
        }
