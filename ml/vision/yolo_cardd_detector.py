"""YOLOv8 / YOLOv11 Instance Segmentation Detector Adapter for CarDD.

Runs natively on macOS with Apple Silicon GPU acceleration (device='mps')
or on CUDA / CPU. Provides fast, highly accurate damage localization and
fine-grained polygon contours for vehicle damage assessment.
"""

from __future__ import annotations

import logging
import os
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from PIL import Image

logger = logging.getLogger(__name__)

# CarDD classes
CARDD_CLASSES: Tuple[str, ...] = (
    "dent",
    "scratch",
    "crack",
    "glass shatter",
    "lamp broken",
    "tire flat",
)

CARDD_TO_CANONICAL: Dict[str, str] = {
    "dent": "dent",
    "scratch": "scratch",
    "crack": "crack",
    "glass shatter": "glass_shatter",
    "lamp broken": "broken_light",
    "tire flat": "flat_tire",
}

MODEL_NAME = "cardd_yolov8_seg"


def get_default_yolo_device() -> str:
    """Detect the best device on the current machine (MPS on Apple Silicon, CUDA on Linux, CPU fallback)."""
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
    except Exception:
        pass
    return "cpu"


@dataclass
class YoloDetectorConfig:
    enabled: bool = False
    model_path: str = "work_dirs/cardd_yolo/cardd_seg_v1/weights/best.pt"
    device: str = "mps"
    score_threshold: float = 0.35

    @classmethod
    def from_env(cls) -> "YoloDetectorConfig":
        def _bool(name: str, default: bool) -> bool:
            raw = os.getenv(name)
            if raw is None:
                return default
            return raw.strip().lower() in ("1", "true", "yes", "on")

        def _float(name: str, default: float) -> float:
            try:
                return float(os.getenv(name, str(default)))
            except ValueError:
                return default

        return cls(
            enabled=_bool("CARDD_YOLO_ENABLED", False),
            model_path=os.getenv("CARDD_YOLO_MODEL_PATH", "work_dirs/cardd_yolo/cardd_seg_v1/weights/best.pt"),
            device=os.getenv("CARDD_YOLO_DEVICE", get_default_yolo_device()),
            score_threshold=_float("CARDD_YOLO_SCORE_THRESHOLD", 0.50),
        )


class YoloCarddDetector:
    """YOLOv8/v11 Instance Segmentation adapter for CarDD damage detection."""

    def __init__(self, config: Optional[YoloDetectorConfig] = None) -> None:
        self.config = config or YoloDetectorConfig.from_env()
        self._lock = threading.Lock()
        self._model: Any = None
        self._is_available = False
        self._reason = ""
        self._validate_model()

    @property
    def is_available(self) -> bool:
        return self._is_available

    def status_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.config.enabled,
            "available": self._is_available,
            "reason": self._reason,
            "backend": "yolo",
            "device": self.config.device,
            "model": MODEL_NAME,
        }

    def _validate_model(self) -> None:
        if not self.config.enabled:
            self._reason = "YOLO CarDD detector disabled (CARDD_YOLO_ENABLED=false)."
            self._is_available = False
            return

        p = Path(self.config.model_path)
        if not p.is_file():
            self._reason = f"YOLO model weights not found at {p}. Train or specify CARDD_YOLO_MODEL_PATH."
            self._is_available = False
            return

        try:
            from ultralytics import YOLO
            self._is_available = True
            self._reason = f"YOLO CarDD detector ready ({p.name}) on {self.config.device}."
        except ImportError as exc:
            self._reason = f"ultralytics not installed: {exc}"
            self._is_available = False

    def _ensure_model(self) -> Any:
        if self._model is not None:
            return self._model
        with self._lock:
            if self._model is not None:
                return self._model
            if not self.is_available:
                raise RuntimeError(self._reason)
            from ultralytics import YOLO
            self._model = YOLO(self.config.model_path)
            return self._model

    def predict_detections(
        self,
        image: Any,
        image_width: int,
        image_height: int,
    ) -> Tuple[List[Dict[str, Any]], str, float]:
        """Run YOLO segmentation inference and map predictions to schema format."""
        from ml.vision.schemas import DetectionItem

        t0 = time.perf_counter()
        model = self._ensure_model()

        # Run inference
        results = model.predict(
            source=image,
            conf=self.config.score_threshold,
            device=self.config.device,
            verbose=False,
        )

        detections: List[Dict[str, Any]] = []
        if not results:
            latency = round((time.perf_counter() - t0) * 1000.0, 2)
            return detections, MODEL_NAME, latency

        res = results[0]
        boxes = res.boxes
        masks = res.masks

        if boxes is None or len(boxes) == 0:
            latency = round((time.perf_counter() - t0) * 1000.0, 2)
            return detections, MODEL_NAME, latency

        for idx in range(len(boxes)):
            cls_id = int(boxes.cls[idx].item())
            conf = float(boxes.conf[idx].item())
            xyxy = boxes.xyxy[idx].tolist()

            # Class name
            if cls_id < len(CARDD_CLASSES):
                source_label = CARDD_CLASSES[cls_id]
            else:
                source_label = model.names.get(cls_id, f"class_{cls_id}")
            canonical = CARDD_TO_CANONICAL.get(source_label, source_label)

            # Clamp bounding box
            x1 = max(0.0, min(float(image_width), xyxy[0]))
            y1 = max(0.0, min(float(image_height), xyxy[1]))
            x2 = max(0.0, min(float(image_width), xyxy[2]))
            y2 = max(0.0, min(float(image_height), xyxy[3]))
            if not (x2 > x1 and y2 > y1):
                continue
            clamped_box = [round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)]

            # Extract polygon mask points
            mask_poly = None
            if masks is not None and len(masks.xy) > idx:
                pts = masks.xy[idx]
                if len(pts) >= 3:
                    mask_poly = [
                        [round(max(0.0, min(float(image_width), float(p[0]))), 2),
                         round(max(0.0, min(float(image_height), float(p[1]))), 2)]
                        for p in pts
                    ]

            item = DetectionItem(
                instance_id=f"yolo_{idx:03d}",
                label=canonical,
                confidence=round(conf, 4),
                bbox_xyxy=clamped_box,
                coordinate_space="original_image_pixels",
                mask=mask_poly,
                source_label=source_label,
            )
            detections.append(item.model_dump())

        latency = round((time.perf_counter() - t0) * 1000.0, 2)
        return detections, MODEL_NAME, latency
