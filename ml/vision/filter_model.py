"""Stage 1: Damaged vs. Undamaged Binary Filter.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 8.1 & Section 8.2.
Performs lightweight binary classification.
If p_damage < threshold, downstream expensive stages are bypassed,
saving computational overhead.

Active backend: ClassicalDamageEngine (OpenCV, local, no network). The
probability is a saturating function of measured anomaly mass on the actual
pixels — a valid negative below threshold is a real completed inference,
never an abstention.
"""

from __future__ import annotations

import logging
import time
from typing import Optional, Tuple

from PIL import Image

from ml.vision.classical_engine import ClassicalDamageEngine
from ml.vision.schemas import StageStatus

logger = logging.getLogger(__name__)


class Stage1FilterModel:
    """Stage 1 binary damaged/undamaged classifier."""

    def __init__(
        self,
        model_name: str = "classical_cv_v1",
        threshold: float = 0.85,
        weights_path: Optional[str] = None,
    ):
        self.model_name = model_name
        self.threshold = threshold
        self.weights_path = weights_path  # reserved for future neural weights
        self._engine: Optional[ClassicalDamageEngine] = None
        self._is_loaded = False
        self._init_model()

    def _init_model(self) -> None:
        """Initialize the local inference engine. Failure => MODEL_UNAVAILABLE."""
        try:
            self._engine = ClassicalDamageEngine()
            self._is_loaded = True
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Stage 1 engine initialization failed: %s", exc)
            self._engine = None
            self._is_loaded = False

    def predict(self, image: Image.Image) -> Tuple[bool, float, StageStatus, float]:
        """Predict whether the image shows vehicle damage.

        Returns (is_damaged, probability, status, latency_ms).
        """
        start_time = time.perf_counter()
        if not self._is_loaded or self._engine is None:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return False, 0.0, StageStatus.MODEL_UNAVAILABLE, round(latency_ms, 2)

        try:
            analysis = self._engine.analyze(image)
            prob = float(analysis.probability)
            is_damaged = prob >= self.threshold
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return is_damaged, round(prob, 4), StageStatus.COMPLETED, round(latency_ms, 2)
        except ValueError as exc:
            # Degenerate image input (e.g. tiny) — inference cannot run.
            logger.warning("Stage 1 could not run on image: %s", exc)
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return False, 0.0, StageStatus.FAILED, round(latency_ms, 2)
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Stage 1 inference failed: %s", exc)
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return False, 0.0, StageStatus.FAILED, round(latency_ms, 2)

