"""RAG Knowledge Specialist Agent.

Retrieves verified repair and diagnostic guidelines grounded in safety standards.
Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 11.1 & Section 12.
"""

from __future__ import annotations

from agents.state import InspectionGraphState
from rag.retrieval import RAGKnowledgeEngine


class RAGAgent:
    """Specialist agent wrapping RAG knowledge retrieval."""

    def __init__(self, top_k: int = 5):
        self.engine = RAGKnowledgeEngine(top_k=top_k)

    def run(self, state: InspectionGraphState) -> InspectionGraphState:
        """Formulate query from visual findings & DTCs, then retrieve source passages."""
        try:
            damage_classes = []
            if state.vision_result:
                damage_classes = state.vision_result.primary_damage_classes

            dtc_codes = []
            if state.obd_result and state.obd_result.dtcs:
                dtc_codes = [d.code for d in state.obd_result.dtcs]

            retrieval = self.engine.retrieve(
                damage_classes=damage_classes,
                dtc_codes=dtc_codes,
                vehicle_make=state.vehicle_info.make,
                vehicle_model=state.vehicle_info.model,
            )

            state.rag_result = retrieval
            state.completed_stages.append("knowledge_retrieval")
        except Exception as e:
            state.errors.append(f"RAG Agent execution failed: {e}")
            state.warnings.append("Knowledge retrieval failed; no external repair citations attached.")
        return state
