"""Stage 2: Damage Taxonomy Classification.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 8.1 & Section 8.3.
Classifies confirmed damage into the taxonomy:
  scratch, dent, glass_crack, bumper_smash, flat_tire, broken_light

Active backend: labels are assigned by ClassicalDamageEngine from measured
region geometry (elongation, brightness, area, position) per response channel.
"""

from __future__ import annotations

import logging
import time
from typing import Dict, List, Optional, Tuple

from PIL import Image

from ml.vision.classical_engine import ClassicalDamageEngine
from ml.vision.schemas import ClassificationItem, StageStatus

logger = logging.getLogger(__name__)

CLASS_ID_TO_LABEL: Dict[int, str] = {
    0: "scratch",
    1: "dent",
    2: "glass_crack",
    3: "bumper_smash",
    4: "flat_tire",
    5: "broken_light",
}

LABEL_TO_CLASS_ID: Dict[str, int] = {v: k for k, v in CLASS_ID_TO_LABEL.items()}

CANONICAL_CLASSES = tuple(LABEL_TO_CLASS_ID.keys())


class Stage2DamageClassifier:
    """Stage 2 damage taxonomy classifier."""

    def __init__(self, engine: Optional[ClassicalDamageEngine] = None):
        self._engine = engine if engine is not None else ClassicalDamageEngine()

    @staticmethod
    def decode_class_id(class_id: int) -> str:
        if class_id not in CLASS_ID_TO_LABEL:
            raise ValueError(f"Unknown class ID: {class_id}")
        return CLASS_ID_TO_LABEL[class_id]

    def predict(self, image: Image.Image) -> Tuple[List[ClassificationItem], StageStatus, float]:
        """Classify damage types present in the image.

        Returns (classifications, status, latency_ms). Empty list with COMPLETED
        means the engine found no damage region — a valid outcome the pipeline
        reconciles against the stage-1 probability.
        """
        start_time = time.perf_counter()
        try:
            analysis = self._engine.analyze(image)
        except Exception as exc:  # degenerate input or engine failure
            logger.error("Stage 2 inference failed: %s", exc)
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return [], StageStatus.FAILED, round(latency_ms, 2)

        best: Dict[str, float] = {}
        for region in analysis.regions:
            if region.label not in LABEL_TO_CLASS_ID:
                continue
            best[region.label] = max(best.get(region.label, 0.0), region.confidence)

        items = [
            ClassificationItem(label=label, confidence=round(conf, 4))
            for label, conf in sorted(best.items(), key=lambda kv: kv[1], reverse=True)
        ]
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        return items, StageStatus.COMPLETED, round(latency_ms, 2)
