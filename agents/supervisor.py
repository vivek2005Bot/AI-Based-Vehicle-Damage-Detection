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
from agents.state import InspectionGraphState
from agents.vision_agent import VisionAgent
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
            sev_dict = {
                "score": state.vision_result.overall_severity.score,
                "level": state.vision_result.overall_severity.level.value,
                "method": state.vision_result.overall_severity.method,
                "calibrated": state.vision_result.overall_severity.calibrated,
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
            "model_metadata": {
                "vision_pipeline_version": "1.1.0",
                "filter_model": "classical_cv_v1",
                "classifier_model": "classical_cv_v1",
                "detector_model": "classical_cv_v1",
                "segmenter_model": "classical_cv_contour_v1",
                "obd_model": "isolation_forest",
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
