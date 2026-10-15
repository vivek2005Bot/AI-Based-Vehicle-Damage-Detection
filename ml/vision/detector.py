"""Stage 3: Damage Instance Detector.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 8.1 & Section 8.2.
Produces localized bounding boxes [xmin, ymin, xmax, ymax] in original image space.

Active backend: ClassicalDamageEngine regions (measured anomaly blobs) mapped
back to original image pixels. Two input modes are supported:

  * Letterboxed input (image size == preprocessing target size): work ->
    letterbox space (uniform scale) -> original space (subtract pad, clip).
    Kept for standalone/legacy callers that pass `letterbox_resize()` output.
  * Original-image input (pipeline default): the engine analyzes the unpadded
    source image directly, so no pad seam can contaminate the response maps.
    Work -> original is then a plain uniform scale with no offset.

Each DetectionItem carries the real pixel contour of its region as the mask
polygon (Stage 4 computes pixel areas).
"""

from __future__ import annotations

import logging
import time
from typing import List, Optional, Tuple

from PIL import Image

from ml.vision.classical_engine import ClassicalDamageEngine
from ml.vision.preprocessing import (
    PreprocessingTransformMetadata,
    model_to_original_box,
    model_to_original_polygon,
)
from ml.vision.schemas import DetectionItem, StageStatus

logger = logging.getLogger(__name__)



def _iou(a: List[float], b: List[float]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    aa = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    bb = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = aa + bb - inter
    return inter / union if union > 0 else 0.0


def nms(dets: List[DetectionItem], iou_thresh: float = 0.45) -> List[DetectionItem]:
    """Class-aware NMS: keep highest confidence, drop same-label IoU>thresh."""
    kept: List[DetectionItem] = []
    for det in sorted(dets, key=lambda d: d.confidence, reverse=True):
        dup = any(d.label == det.label and _iou(d.bbox_xyxy, det.bbox_xyxy) > iou_thresh for d in kept)
        if not dup:
            kept.append(det)
    return kept


def nms_cross_class(dets: List[DetectionItem], iou_thresh: float = 0.70) -> List[DetectionItem]:
    """Cross-class NMS: suppress different-label detections with very high IoU.
    
    If two detections of different classes overlap almost completely (IoU > 0.70),
    they likely represent the same physical damage. Keep the higher-confidence one.
    """
    kept: List[DetectionItem] = []
    for det in sorted(dets, key=lambda d: d.confidence, reverse=True):
        # Check same-class overlap (standard NMS)
        same_class_dup = any(
            d.label == det.label and _iou(d.bbox_xyxy, det.bbox_xyxy) > 0.45
            for d in kept
        )
        # Check cross-class overlap (very high IoU)
        cross_class_dup = any(
            d.label != det.label and _iou(d.bbox_xyxy, det.bbox_xyxy) > iou_thresh
            for d in kept
        )
        if not same_class_dup and not cross_class_dup:
            kept.append(det)
    return kept


class Stage3DamageDetector:
    """Stage 3 object detector for vehicle damage instances."""

    def __init__(
        self,
        architecture: str = "classical_cv_v1",
        weights_path: Optional[str] = None,
        confidence_threshold: float = 0.55,
        iou_threshold: float = 0.45,
        engine: Optional[ClassicalDamageEngine] = None,
    ):
        self.architecture = architecture
        self.weights_path = weights_path  # reserved for future neural weights
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self._engine = engine if engine is not None else ClassicalDamageEngine()

    def predict(
        self,
        image: Image.Image,
        transforms: PreprocessingTransformMetadata,
    ) -> Tuple[List[DetectionItem], StageStatus, float]:
        start_time = time.perf_counter()
        try:
            analysis = self._engine.analyze(image)
        except Exception as exc:
            logger.error("Stage 3 inference failed: %s", exc)
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return [], StageStatus.FAILED, round(latency_ms, 2)

        # The engine analyzed `image` itself. Work space always shares the
        # aspect ratio of that input; determine which space it was in.
        if analysis.work_width <= 0 or analysis.work_height <= 0:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return [], StageStatus.FAILED, round(latency_ms, 2)

        received_w, received_h = image.size
        letterboxed_input = (
            (received_w, received_h) == (transforms.target_width, transforms.target_height)
            and (received_w, received_h) != (transforms.original_width, transforms.original_height)
        )

        if letterboxed_input:
            # work -> letterbox (uniform scale, no offset) -> original pixels.
            lb_scale_x = float(transforms.target_width) / float(analysis.work_width)
            lb_scale_y = float(transforms.target_height) / float(analysis.work_height)

            def to_original_box(box):
                return model_to_original_box(
                    [box[0] * lb_scale_x, box[1] * lb_scale_y,
                     box[2] * lb_scale_x, box[3] * lb_scale_y],
                    transforms,
                )

            def to_original_poly(poly):
                lb_poly = [[px * lb_scale_x, py * lb_scale_y] for px, py in poly]
                return model_to_original_polygon(lb_poly, transforms) if len(lb_poly) >= 3 else None
        else:
            # work -> original directly (no letterbox pad exists in between).
            orig_w = float(transforms.original_width)
            orig_h = float(transforms.original_height)
            sx = orig_w / float(analysis.work_width)
            sy = orig_h / float(analysis.work_height)

            def to_original_box(box):
                return [
                    round(max(0.0, min(orig_w, box[0] * sx)), 2),
                    round(max(0.0, min(orig_h, box[1] * sy)), 2),
                    round(max(0.0, min(orig_w, box[2] * sx)), 2),
                    round(max(0.0, min(orig_h, box[3] * sy)), 2),
                ]

            def to_original_poly(poly):
                if len(poly) < 3:
                    return None
                return [
                    [round(max(0.0, min(orig_w, px * sx)), 2),
                     round(max(0.0, min(orig_h, py * sy)), 2)]
                    for px, py in poly
                ]

        detections: List[DetectionItem] = []
        for i, region in enumerate(analysis.regions):
            orig_box = to_original_box(region.bbox_xyxy)
            orig_poly = to_original_poly(region.polygon)

            detections.append(
                DetectionItem(
                    instance_id=f"det_{i:03d}",
                    label=region.label,
                    confidence=region.confidence,
                    bbox_xyxy=orig_box,
                    coordinate_space="original_image_pixels",
                    mask=orig_poly,
                )
            )

        # Single suppression stage lives in ClassicalDamageEngine._dedupe()
        # (class-agnostic IoU/IoM). Do NOT apply a second NMS pass here:
        # duplicate NMS stages disagree and drop correct boxes.
        # The pipeline applies only the confidence gate downstream.

        latency_ms = (time.perf_counter() - start_time) * 1000.0
        return detections, StageStatus.COMPLETED, round(latency_ms, 2)

