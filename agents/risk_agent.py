"""Risk Engine Specialist Agent.

Evaluates multimodal findings and applies deterministic safety rules.
Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 11.1 & Section 13.
"""

from __future__ import annotations

from agents.rules import evaluate_risk
from agents.state import InspectionGraphState


class RiskAgent:
    """Specialist agent wrapping the deterministic Risk Engine."""

    def run(self, state: InspectionGraphState) -> InspectionGraphState:
        """Evaluate multimodal inputs and assign Safe/Caution/Unsafe status."""
        try:
            assessment = evaluate_risk(
                vision_result=state.vision_result,
                obd_result=state.obd_result,
            )
            state.risk_result = assessment
            state.completed_stages.append("risk_assessment")
        except Exception as e:
            state.errors.append(f"Risk Agent execution failed: {e}")
            state.warnings.append("Risk assessment failed; human review mandated.")
        return state
