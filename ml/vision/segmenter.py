"""Stage 4: Instance Segmentation for Damage Regions.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 8.1 & Section 8.2.
Candidate architectures: Mask R-CNN, SAM 2 (box-prompted).
Generates polygon masks and calculates affected pixel areas.
"""

from __future__ import annotations

import time
from typing import List, Optional, Tuple

from ml.vision.preprocessing import PreprocessingTransformMetadata
from ml.vision.schemas import DetectionItem, StageStatus
from ml.vision.severity import calculate_polygon_area


class Stage4DamageSegmenter:
    """Stage 4 instance segmentation adapter.

    Active backend: detection masks produced by ClassicalDamageEngine are real
    pixel contours of the measured anomaly regions (mapped to original image
    coordinates by Stage 3). This stage clips them to the frame and computes
    affected pixel areas / relative areas for severity scoring. It never
    synthesizes geometry that did not come from image evidence.
    """

    def __init__(
        self,
        architecture: str = "classical_cv_contour_v1",
        weights_path: Optional[str] = None,
    ):
        self.architecture = architecture
        self.weights_path = weights_path  # reserved for future neural mask models
        self._is_loaded = True

    def segment_instances(
        self,
        detections: List[DetectionItem],
        transforms: PreprocessingTransformMetadata,
    ) -> Tuple[List[DetectionItem], StageStatus, float]:
        """Generate polygon masks for detected damage instances."""
        start_time = time.perf_counter()

        if not detections:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return [], StageStatus.SKIPPED_INTACT, round(latency_ms, 2)

        segmented_items: List[DetectionItem] = []

        # Real contour path: masks come from measured image regions. A
        # detection without a decoded contour stays box-only (zero mask area) —
        # we never synthesize a polygon from the box.
        for det in detections:
            if det.mask is None or len(det.mask) < 3:
                # No contour -> keep detection box-only, zero mask area.
                segmented_items.append(det)
                continue
            xmin, ymin, xmax, ymax = det.bbox_xyxy
            max_w = float(transforms.original_width)
            max_h = float(transforms.original_height)
            clipped = [
                [max(0.0, min(max_w, float(x))), max(0.0, min(max_h, float(y)))]
                for x, y in det.mask
            ]

            polygon = [[round(float(x), 2), round(float(y), 2)] for x, y in clipped]
            area = calculate_polygon_area(polygon)
            total_img_pixels = float(transforms.original_width * transforms.original_height)
            rel_area = min(1.0, area / max(1.0, total_img_pixels))

            updated_det = det.model_copy(update={
                "mask": polygon,
                "mask_pixel_area": round(area, 1),
                "relative_area": round(rel_area, 4),
            })
            segmented_items.append(updated_det)

        latency_ms = (time.perf_counter() - start_time) * 1000.0
        return segmented_items, StageStatus.COMPLETED, round(latency_ms, 2)
