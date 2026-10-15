"""Vision Specialist Agent.

Executes the 4-stage Computer Vision pipeline on uploaded vehicle images.
Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 11.1.
"""

from __future__ import annotations

from typing import List, Union
from PIL import Image

from agents.state import InspectionGraphState
from ml.vision.pipeline import VisionPipeline
from ml.vision.schemas import VisionPipelineResult


class VisionAgent:
    """Specialist agent wrapping the 4-stage vision pipeline."""

    def __init__(self, filter_threshold: float = 0.85):
        self.pipeline = VisionPipeline(filter_threshold=filter_threshold)

    def run(
        self,
        state: InspectionGraphState,
        image_objects: List[Union[str, bytes, Image.Image]],
    ) -> InspectionGraphState:
        """Run vision pipeline and attach findings to state."""
        try:
            result = self.pipeline.process_inspection(
                images=image_objects,
                filenames=state.image_filenames,
                inspection_id=state.inspection_id,
            )
            state.vision_result = result
            state.completed_stages.append("vision_analysis")
        except Exception as e:
            state.errors.append(f"Vision Agent execution failed: {e}")
            state.warnings.append("Vision analysis failed; proceeding with fallback report.")
        return state
