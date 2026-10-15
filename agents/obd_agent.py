"""OBD Analytics Specialist Agent.

Executes telemetry validation, Isolation Forest anomaly scoring, and DTC parsing.
Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 11.1.
"""

from __future__ import annotations

from typing import Optional, Union

from agents.state import InspectionGraphState
from ml.obd.pipeline import OBDPipeline
from ml.obd.schemas import OBDAnalysisResult, OBDStatus


class OBDAgent:
    """Specialist agent wrapping the OBD-II telemetry pipeline."""

    def __init__(self, contamination: float = 0.05):
        self.pipeline = OBDPipeline(contamination=contamination)

    def run(
        self,
        state: InspectionGraphState,
        csv_bytes: Optional[Union[bytes, str]] = None,
    ) -> InspectionGraphState:
        """Run OBD pipeline and attach results to state."""
        try:
            if not csv_bytes:
                result = self.pipeline.analyze(None)
            else:
                result = self.pipeline.analyze(csv_bytes, filename=state.obd_filename)

            state.obd_result = result
            state.completed_stages.append("obd_analysis")
        except Exception as e:
            state.errors.append(f"OBD Agent execution failed: {e}")
            state.warnings.append("OBD telemetry analysis encountered an error.")
            state.obd_result = OBDAnalysisResult(status=OBDStatus.FAILED)
        return state
