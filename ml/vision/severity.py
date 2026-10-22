"""Severity Calculation Module.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 8.5 and Master Prompt Step 6.
Implements:
  r = A_mask / A_veh (relative damage ratio)
  S = sum(w_c * r_c) (weighted severity score)
Categorizes severity into Low, Medium, High levels based on calibrated cutoffs.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

from ml.vision.schemas import DamageSeverityLevel, DetectionItem, SeverityAssessment


DEFAULT_CLASS_WEIGHTS: Dict[str, float] = {
    "bumper_smash": 0.35,
    "glass_crack": 0.25,
    # CarDD labels (explicit, reviewed — no silent fallback):
    # glass_shatter (CarDD "glass shatter") == shattered glazing, same safety
    # relevance as glass_crack. crack (CarDD "crack") == body/paint crack,
    # cosmetic-to-moderate: between scratch and dent. flat_tire canonical is
    # "flat_tire"; "tire_flat" kept as alias for raw CarDD outputs.
    "glass_shatter": 0.25,
    "crack": 0.10,
    "tire_flat": 0.20,
    "broken_mirror": 0.22,
    "flat_tire": 0.20,
    "broken_light": 0.15,
    "dent": 0.12,
    "scratch": 0.08,
}

# Thresholds for severity levels
LOW_SEVERITY_MAX = 0.05
MEDIUM_SEVERITY_MAX = 0.20


def calculate_polygon_area(points: List[List[float]]) -> float:
    """Calculate the area of a 2D polygon using the Shoelace formula."""
    if len(points) < 3:
        return 0.0
    n = len(points)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += points[i][0] * points[j][1]
        area -= points[j][0] * points[i][1]
    return abs(area) / 2.0


def calculate_box_area(box_xyxy: List[float]) -> float:
    """Compute area of bounding box [xmin, ymin, xmax, ymax]."""
    xmin, ymin, xmax, ymax = box_xyxy
    w = max(0.0, xmax - xmin)
    h = max(0.0, ymax - ymin)
    return w * h


def estimate_instance_area(item: DetectionItem) -> float:
    """Compute the pixel area for a detection instance using mask if present, otherwise box."""
    if item.mask and len(item.mask) >= 3:
        return calculate_polygon_area(item.mask)
    if item.mask_pixel_area is not None and item.mask_pixel_area > 0:
        return item.mask_pixel_area
    return calculate_box_area(item.bbox_xyxy)


def calculate_severity(
    detections: List[DetectionItem],
    image_width: int,
    image_height: int,
    vehicle_pixel_area: Optional[float] = None,
    class_weights: Optional[Dict[str, float]] = None,
) -> SeverityAssessment:
    """Calculate relative damage ratio and calibrated severity score S."""
    if not detections:
        return SeverityAssessment(
            score=0.0,
            level=DamageSeverityLevel.LOW,
            method="calibrated_composite_severity",
            calibrated=False,
            affected_pixel_area_total=0.0,
            vehicle_pixel_area=vehicle_pixel_area or float(image_width * image_height),
            relative_damage_ratio=0.0,
        )

    weights = class_weights or DEFAULT_CLASS_WEIGHTS
    total_image_pixels = float(max(1, image_width * image_height))

    if vehicle_pixel_area and vehicle_pixel_area > 0:
        denominator = vehicle_pixel_area
    else:
        denominator = total_image_pixels
    is_calibrated = vehicle_pixel_area is not None and vehicle_pixel_area > 0

    total_damage_pixels = 0.0
    weighted_score = 0.0

    for det in detections:
        area_c = estimate_instance_area(det)
        total_damage_pixels += area_c

        # Relative ratio for this instance: r_c = A_mask_c / A_veh
        r_c = min(1.0, area_c / denominator)
        w_c = weights.get(det.label, 0.10)
        weighted_score += w_c * r_c

    # Aggregate relative ratio
    overall_ratio = min(1.0, total_damage_pixels / denominator)

    # Normalize S so it is bounded [0.0, 1.0].
    score = min(1.0, weighted_score)

    # Map to Low / Medium / High
    if score < LOW_SEVERITY_MAX:
        level = DamageSeverityLevel.LOW
    elif score < MEDIUM_SEVERITY_MAX:
        level = DamageSeverityLevel.MEDIUM
    else:
        level = DamageSeverityLevel.HIGH

    return SeverityAssessment(
        score=round(score, 4),
        level=level,
        method="relative_area_weighted_by_class",
        calibrated=is_calibrated,
        affected_pixel_area_total=round(total_damage_pixels, 1),
        vehicle_pixel_area=round(denominator, 1),
        relative_damage_ratio=round(overall_ratio, 4),
        formula_citation="S = Σ(w_c * r_c)",
    )
