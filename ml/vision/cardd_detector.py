"""CarDD Mask R-CNN detector adapter (optional, disabled by default).

Optional CarDD-fine-tuned Mask R-CNN (MMDetection 2.x) behind a feature flag.
ClassicalDamageEngine stays the active default; this adapter never overrides
safety rules and never converts a load/inference failure into NO_DAMAGE.

Checkpoint provenance: the repo-root mask_rcnn_r50_fpn_2x_coco_*.pth is
COCO-pretrained init weights, NOT a CarDD damage model. Provenance gate below
rejects it so it can never be misrepresented as production weights.
"""

from __future__ import annotations

import logging
import os
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Official CarDD class order — DO NOT REORDER without updating config +
# annotations + category-ID mapping together.
CARDD_CLASSES: Tuple[str, ...] = (
    "dent",
    "scratch",
    "crack",
    "glass shatter",
    "lamp broken",
    "tire flat",
)

CARDD_CLASS_TO_ID: Dict[str, int] = {c: i for i, c in enumerate(CARDD_CLASSES)}
CARDD_ID_TO_CLASS: Dict[int, str] = {i: c for c, i in CARDD_CLASS_TO_ID.items()}

# Conservative mapping into canonical taxonomy. `crack`/`glass shatter` are
# preserved as explicit labels (never coerced to bumper_smash); rules.py is
# untouched so no new label can escalate risk without a tested rule change.
CARDD_TO_CANONICAL: Dict[str, str] = {
    "dent": "dent",
    "scratch": "scratch",
    "crack": "crack",
    "glass shatter": "glass_shatter",
    "lamp broken": "broken_light",
    "tire flat": "flat_tire",
}

MODEL_NAME = "cardd_mask_rcnn_r50_fpn_2x"
MODEL_VERSION = "unverified-no-finetuned-checkpoint"

_COCO_INIT_MARKERS = (
    "coco",
    "bbox_map",
    "segm_map",
    "3e542a40",
    "d4b0c5d6",
    "1efe0ed5",
    "14b391c7",
)


def decode_cardd_class_id(class_id: int) -> str:
    if class_id not in CARDD_ID_TO_CLASS:
        raise ValueError(f"Unknown CarDD class ID: {class_id}")
    return CARDD_ID_TO_CLASS[class_id]


def map_cardd_label(source_label: str) -> str:
    if source_label not in CARDD_TO_CANONICAL:
        raise ValueError(f"Unknown CarDD source label: {source_label!r}")
    return CARDD_TO_CANONICAL[source_label]


def clamp_box_xyxy(box: List[float], image_width: int, image_height: int) -> Optional[List[float]]:
    if len(box) != 4:
        return None
    try:
        x1, y1, x2, y2 = (float(v) for v in box)
    except (TypeError, ValueError):
        return None
    x1 = max(0.0, min(float(image_width), x1))
    y1 = max(0.0, min(float(image_height), y1))
    x2 = max(0.0, min(float(image_width), x2))
    y2 = max(0.0, min(float(image_height), y2))
    if not (x2 > x1 and y2 > y1):
        return None
    return [round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)]


def is_cardd_finetuned_checkpoint(checkpoint_path: str | os.PathLike) -> bool:
    """Provenance gate: reject COCO-init weights as production models."""
    name = Path(str(checkpoint_path)).name.lower()
    path_str = str(checkpoint_path).lower()
    if any(m in name for m in _COCO_INIT_MARKERS):
        return False
    if "coco" in path_str and "cardd" not in path_str:
        return False
    if any(m in path_str for m in ("work_dirs/cardd", "checkpoints/cardd")):
        return True
    return False


def resolve_cardd_device(requested_device: Optional[str] = None) -> str:
    """Resolve an execution device safely on the current host.

    On macOS or environments without CUDA, requests for 'cuda' or 'cuda:*'
    are safely sanitized to 'cpu' so execution does not crash with a
    PyTorch/CUDA runtime error.
    """
    dev = (requested_device or "cpu").strip().lower()
    if dev.startswith("cuda"):
        try:
            import torch
            if not torch.cuda.is_available():
                logger.warning(
                    "CUDA device requested (%s), but CUDA is not available on this host (macOS / no NVIDIA GPU). "
                    "Safely falling back to CPU.",
                    dev,
                )
                return "cpu"
        except Exception:
            logger.warning(
                "CUDA device requested (%s), but CUDA cannot be initialized on this host (e.g. macOS). "
                "Safely falling back to CPU.",
                dev,
            )
            return "cpu"
    return dev


@dataclass
class CarddDetectorConfig:
    enabled: bool = False
    config_path: Optional[str] = None
    checkpoint_path: Optional[str] = None
    device: str = "cpu"
    score_threshold: float = 0.50
    backend: str = "mmdet2"

    @classmethod
    def from_env(cls) -> "CarddDetectorConfig":
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
            enabled=_bool("CARDD_MODEL_ENABLED", False),
            config_path=os.getenv("CARDD_MODEL_CONFIG"),
            checkpoint_path=os.getenv("CARDD_MODEL_CHECKPOINT"),
            device=resolve_cardd_device(os.getenv("CARDD_MODEL_DEVICE", "cpu")),
            score_threshold=_float("CARDD_MODEL_SCORE_THRESHOLD", 0.50),
            backend=os.getenv("CARDD_MODEL_BACKEND", "mmdet2"),
        )


@dataclass
class CarddStatus:
    enabled: bool = False
    available: bool = False
    reason: str = "CarDD detector disabled (CARDD_MODEL_ENABLED=false)."
    backend: str = "mmdet2"
    device: str = "cpu"


class CarddDamageDetector:
    """Optional CarDD Mask R-CNN adapter. Load once, reuse across requests."""

    def __init__(self, config: Optional[CarddDetectorConfig] = None) -> None:
        self.config = config or CarddDetectorConfig.from_env()
        self.config.device = resolve_cardd_device(self.config.device)
        self._lock = threading.Lock()
        self._model: Any = None
        self._status = CarddStatus(
            enabled=self.config.enabled,
            backend=self.config.backend,
            device=self.config.device,
        )
        if self.config.enabled:
            self._validate_startup()
        logger.info(
            "CarDD detector status: enabled=%s available=%s reason=%s",
            self._status.enabled, self._status.available, self._status.reason,
        )

    @property
    def status(self) -> CarddStatus:
        return self._status

    @property
    def is_available(self) -> bool:
        return bool(self._status.enabled and self._status.available)

    def status_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self._status.enabled,
            "available": self._status.available,
            "reason": self._status.reason,
            "backend": self._status.backend,
            "device": self._status.device,
            "model": MODEL_NAME,
            "version": MODEL_VERSION,
        }

    def _validate_startup(self) -> None:
        cfg = self.config
        if not cfg.config_path or not Path(cfg.config_path).exists():
            self._status.reason = (
                f"CarDD unavailable: config not found ({cfg.config_path!r}). "
                "Set CARDD_MODEL_CONFIG."
            )
            return
        if not cfg.checkpoint_path or not Path(cfg.checkpoint_path).exists():
            self._status.reason = (
                f"CarDD unavailable: checkpoint not found ({cfg.checkpoint_path!r}). "
                "Set CARDD_MODEL_CHECKPOINT."
            )
            return
        if not is_cardd_finetuned_checkpoint(cfg.checkpoint_path):
            self._status.reason = (
                "CarDD unavailable: checkpoint provenance unverified — "
                f"{Path(cfg.checkpoint_path).name!r} looks like COCO-pretrained "
                "init weights, not a CarDD-fine-tuned model. "
                "See docs/cardd_training.md."
            )
            return
        try:
            import importlib.util as _u
            if _u.find_spec("mmdet") is None or _u.find_spec("mmcv") is None:
                self._status.reason = (
                    "CarDD unavailable: mmdet/mmcv not installed here. Use the "
                    "isolated MMDetection 2.x env/service (docs/cardd_training.md)."
                )
                return
        except Exception as exc:
            self._status.reason = f"CarDD unavailable: backend check failed ({exc})."
            return
        self._status.available = True
        self._status.reason = "CarDD configured (lazy load on first use)."

    def _ensure_model(self) -> Any:
        if self._model is not None:
            return self._model
        with self._lock:
            if self._model is not None:
                return self._model
            if not self.is_available:
                raise RuntimeError(f"CarDD detector not available: {self._status.reason}")
            from mmdet.apis import init_detector  # type: ignore  # legacy stack only
            self._model = init_detector(
                str(self.config.config_path),
                str(self.config.checkpoint_path),
                device=self.config.device,
            )
            return self._model

    def parse_raw_result(self, raw_result: Any, image_width: int, image_height: int) -> List[Dict[str, Any]]:
        """Convert MMDet 2.x Mask R-CNN raw output to typed dicts.

        Expected: (bbox_results, segm_results); bbox per-class Nx5
        (x1,y1,x2,y2,score). Handles empty/missing masks, bad boxes.
        """
        from ml.vision.schemas import DetectionItem

        parsed: List[Dict[str, Any]] = []
        if not raw_result:
            return parsed
        try:
            bbox_results, segm_results = raw_result
        except (TypeError, ValueError):
            logger.warning("CarDD raw result unexpected structure; ignoring.")
            return parsed
        idx = 0
        try:
            iterator = enumerate(bbox_results or [])
            seq = list(iterator)
        except TypeError:
            logger.warning("CarDD raw result unexpected structure; ignoring.")
            return parsed
        for class_id, per_class in seq:
            try:
                source_label = decode_cardd_class_id(class_id)
            except ValueError:
                continue
            canonical = map_cardd_label(source_label)
            try:
                dets = list(per_class) if per_class is not None else []
            except TypeError:
                continue
            if segm_results and class_id < len(segm_results) and segm_results[class_id] is not None:
                masks = segm_results[class_id]
            else:
                masks = [None] * len(dets)
            for j, det in enumerate(dets):
                try:
                    x1, y1, x2, y2, score = (float(v) for v in list(det)[:5])
                except (TypeError, ValueError):
                    continue
                if float(score) < float(self.config.score_threshold):
                    continue
                box = clamp_box_xyxy([x1, y1, x2, y2], image_width, image_height)
                if box is None:
                    continue
                try:
                    raw_mask = masks[j] if j < len(masks) else None
                    mask_poly = self._mask_to_polygon(raw_mask, image_width, image_height)
                except Exception:
                    mask_poly = None
                item = DetectionItem(
                    instance_id=f"cardd_{idx:03d}",
                    label=canonical,
                    confidence=round(min(1.0, max(0.0, float(score))), 4),
                    bbox_xyxy=box,
                    coordinate_space="original_image_pixels",
                    mask=mask_poly,
                    source_label=source_label,
                )
                parsed.append(item.model_dump())
                idx += 1
        return parsed

    @staticmethod
    def _mask_to_polygon(raw_mask: Any, image_width: int, image_height: int) -> Optional[List[List[float]]]:
        """Binary mask array -> exterior contour polygon; None keeps box-only."""
        if raw_mask is None:
            return None
        try:
            import numpy as np
            arr = np.asarray(raw_mask)
        except Exception:
            return None
        if arr.size == 0 or float(arr.max(initial=0)) <= 0:
            return None
        try:
            import cv2
            bin_mask = (arr > 0.5).astype("uint8")
            contours, _ = cv2.findContours(bin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                return None
            cnt = max(contours, key=cv2.contourArea)
            if cv2.contourArea(cnt) < 1.0:
                return None
            poly = [
                [round(max(0.0, min(float(image_width), float(p[0][0]))), 2),
                 round(max(0.0, min(float(image_height), float(p[0][1]))), 2)]
                for p in cnt
            ]
            return poly if len(poly) >= 3 else None
        except Exception:
            return None

    def predict_detections(self, image: Any, image_width: int, image_height: int) -> Tuple[List[Dict[str, Any]], str, float]:
        """Run inference; on ANY failure raise (caller must fallback, not NO_DAMAGE)."""
        t0 = time.perf_counter()
        model = self._ensure_model()
        from mmdet.apis import inference_detector  # type: ignore  # legacy stack only
        import numpy as np
        from PIL import Image as _Image
        img_arr = np.asarray(image.convert("RGB")) if isinstance(image, _Image.Image) else image
        raw = inference_detector(model, img_arr)
        parsed = self.parse_raw_result(raw, image_width, image_height)
        return parsed, MODEL_NAME, round((time.perf_counter() - t0) * 1000.0, 2)
