"""Damage prioritization: primary vs secondary + component association.

Complies with the major-collision fix: the final results must distinguish the
most prominent, consequential damage (PRIMARY) from other distinct supported
defects (SECONDARY), using validated evidence — damage category, localization
quality, confidence, and estimated extent — never confidence or box size alone.

Ranking evidence (all measured, none invented):
  * class weight w_c   — structural classes (bumper_smash, broken_light,
                         glass_crack) outrank cosmetic ones (dent, scratch),
                         reusing the validated severity weights.
  * extent             — sqrt(relative mask/box area): larger genuine damage
                         outranks tiny fragments.
  * confidence         — measured anomaly strength (monotone, uncalibrated).
  * localization       — tiny slivers and edge-hugging boxes are down-weighted.

Component association is a documented POSITIONAL heuristic (frontal/rear view
agnostic): it maps a box's normalized position to the most plausible vehicle
component. It is clearly marked as estimated ("component" is advisory, not a
trained part-segmentation output). A neural part-segmentation stage remains
the correct long-term fix (see docs/model-limitations-and-retraining.md).
"""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

from ml.vision.schemas import DetectionItem
from ml.vision.severity import DEFAULT_CLASS_WEIGHTS, estimate_instance_area


def priority_score(det: DetectionItem, image_width: int, image_height: int) -> float:
    """Composite evidence score (higher = more important). Not a probability."""
    w_c = DEFAULT_CLASS_WEIGHTS.get(det.label, 0.10)
    area = estimate_instance_area(det)
    denom = float(max(1, image_width * image_height))
    extent = math.sqrt(min(1.0, area / denom))
    x1, y1, x2, y2 = det.bbox_xyxy
    bw, bh = max(0.0, x2 - x1), max(0.0, y2 - y1)
    # Localization quality: penalize slivers and boxes glued to frame edges.
    thinness = min(bw, bh) / max(1.0, max(bw, bh))
    edge_hug = 1.0
    if image_width > 0 and image_height > 0:
        if x1 <= 2 or y1 <= 2 or x2 >= image_width - 2 or y2 >= image_height - 2:
            edge_hug = 0.85
    loc = (0.5 + 0.5 * min(1.0, thinness * 3.0)) * edge_hug
    return round(w_c * extent * float(det.confidence) * loc, 6)


def infer_component(
    det: DetectionItem,
    image_width: int,
    image_height: int,
    rear_view: bool = False,
    mirror_boxes: Optional[List[List[float]]] = None,
    roof_boxes: Optional[List[List[float]]] = None,
) -> str:
    """Infer the affected vehicle component from bounding box and view context.

    Broken components with distinct appearance map directly (e.g. broken_mirror
    is always side_mirror; flat_tire is wheel_tire; broken_light on rear_view is
    taillight, else headlight; glass_crack high in frame is windshield).
    If mirror_boxes are provided and the detection lies adjacent to a broken mirror
    (e.g. broken mirror shell or integrated mirror turn indicator), it is attributed
    to side_mirror.
    If roof_boxes are provided (overhead or roof damage present), adjacent defects
    on the upper passenger compartment are mapped to roof.
    """
    x1, y1, x2, y2 = det.bbox_xyxy
    cx = (x1 + x2) / 2.0 / max(1.0, image_width)
    cy = (y1 + y2) / 2.0 / max(1.0, image_height)
    bw_rel = (x2 - x1) / max(1.0, image_width)
    label = (det.label or "").lower()

    if label == "broken_mirror":
        return "side_mirror"

    # Adjacent to a broken mirror assembly -> side_mirror (housing or turn indicator)
    if mirror_boxes:
        def box_gap(a, b) -> float:
            ax1, ay1, ax2, ay2 = a
            bx1, by1, bx2, by2 = b
            dx = max(0.0, max(bx1 - ax2, ax1 - bx2))
            dy = max(0.0, max(by1 - ay2, ay1 - by2))
            return math.hypot(dx, dy)

        max_dim = max(image_width, image_height)
        if any(box_gap(det.bbox_xyxy, mbox) <= 0.16 * max_dim for mbox in mirror_boxes):
            return "side_mirror"

    if label == "broken_light":
        comp = "taillight" if rear_view else "headlight"
    elif label == "glass_crack":
        comp = "windshield" if cy < 0.55 else "glass"
    elif label == "flat_tire":
        return "wheel_tire"  # viewpoint-independent
    elif cy < 0.38:
        # Upper vehicle structure above window line: roof
        comp = "roof"
    elif roof_boxes and cy < 0.52:
        def rbox_gap(a, b) -> float:
            ax1, ay1, ax2, ay2 = a
            bx1, by1, bx2, by2 = b
            dx = max(0.0, max(bx1 - ax2, ax1 - bx2))
            dy = max(0.0, max(by1 - ay2, ay1 - by2))
            return math.hypot(dx, dy)

        max_dim = max(image_width, image_height)
        if any(rbox_gap(det.bbox_xyxy, rbox) <= 0.20 * max_dim for rbox in roof_boxes):
            comp = "roof"
        else:
            comp = "roof_pillar" if (cx < 0.35 or cx > 0.65) else "windshield"
    elif label == "bumper_smash":
        # Bumper smash physically occurs on the lower front or rear bumper fascia
        if cy >= 0.58:
            comp = "front_bumper"
        elif cy < 0.45:
            comp = "roof" if (0.15 < cx < 0.85 and bw_rel < 0.45) else "hood"
        else:
            comp = "front_fender"
    elif cy < 0.50:
        if bw_rel > 0.45:
            comp = "hood"
        else:
            comp = "front_fender" if (cx < 0.25 or cx > 0.75) else "hood"
    elif cy < 0.68:
        if roof_boxes:
            comp = "windshield" if (0.25 < cx < 0.75) else "roof_pillar"
        elif 0.30 < cx < 0.72 and bw_rel > 0.25:
            comp = "grille_fascia"
        elif cx < 0.30:
            comp = "front_fender"
        elif cx > 0.70:
            comp = "headlight_area"
        else:
            comp = "grille_fascia"
    elif cx < 0.35 or cx > 0.65:
        comp = "front_fender" if cy < 0.85 else "wheel_area"
    else:
        comp = "front_bumper"

    if rear_view:
        comp = {
            "front_bumper": "rear_bumper",
            "headlight": "taillight",
            "headlight_area": "taillight_area",
            "hood": "trunk_lid",
            "front_fender": "rear_quarter_panel",
            "grille_fascia": "rear_fascia",
        }.get(comp, comp)
    return comp


def prioritize_detections(
    detections: List[DetectionItem],
    image_width: int,
    image_height: int,
    rear_view: bool = False,
) -> List[DetectionItem]:
    """Rank primary-first, stamping component/priority/score on copies.

    The top-ranked detection becomes PRIMARY; all others SECONDARY. Ordering
    is deterministic (score desc, then confidence, then area, then id) so the
    overlay, chips, and PDF report always agree. Input list is not mutated.
    """
    if not detections:
        return []

    mirror_boxes = [d.bbox_xyxy for d in detections if d.label == "broken_mirror"]
    roof_boxes = [
        d.bbox_xyxy for d in detections
        if (d.bbox_xyxy[1] + d.bbox_xyxy[3]) / 2.0 / max(1.0, image_height) < 0.38
        and d.label in ("dent", "scratch", "structural_damage")
    ]

    scored: List[Tuple[float, DetectionItem]] = []
    for det in detections:
        score = priority_score(det, image_width, image_height)
        component = infer_component(det, image_width, image_height, rear_view, mirror_boxes, roof_boxes)
        scored.append((score, det.model_copy(update={
            "component": component,
            "priority_score": score,
        })))
    scored.sort(
        key=lambda kv: (kv[0], kv[1].confidence,
                        estimate_instance_area(kv[1]), kv[1].instance_id),
        reverse=True,
    )
    out: List[DetectionItem] = []
    for i, (_, det) in enumerate(scored):
        out.append(det.model_copy(update={"priority": "primary" if i == 0 else "secondary"}))
    return out
