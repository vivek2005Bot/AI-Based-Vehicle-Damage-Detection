"""Regression tests for MAJOR collision damage (severe front-end white car).

Ground truth below was manually verified by viewing the reference images
(not model predictions):
  * 19f6218212434986b8822ef7608e2fce.jpg (299x449): white sedan, severe
    frontal collision — buckled hood spanning the upper-middle, crushed grille
    + exposed internals center, torn left headlight/fender, deformed front
    bumper lower area, trees/sky in the top background strip.
  * 96b1daea7fec4e1f803ccd08f7140ee0.jpg (301x428): white sedan, rear
    quarter collision — red taillight top-left, crushed rear bumper lower
    right, dented quarter panel.

Matching is class-aware-light: IoU >= 0.20 OR detection center inside GT.
Labels ARE asserted for the primary finding (the model demonstrably emits
bumper_smash/broken_light on these images; any regression to dent-only
output must fail loudly rather than silently).
"""

import os

import numpy as np
import pytest
from PIL import Image

from ml.vision.detector import _iou
from ml.vision.pipeline import VisionPipeline
from ml.vision.schemas import AssessmentStatus

REPO_ROOT = __file__.rsplit("/tests/", 1)[0]
FRONT_IMG = (
    f"{REPO_ROOT}/private_uploads/insp_e7736baa-ec04-4c12-bc60-267be771d32c"
    "/19f6218212434986b8822ef7608e2fce.jpg"
)
REAR_IMG = (
    f"{REPO_ROOT}/private_uploads/insp_e7736baa-ec04-4c12-bc60-267be771d32c"
    "/96b1daea7fec4e1f803ccd08f7140ee0.jpg"
)

# Manually verified zones (original-image pixels).
FRONT_HOOD_GT = [40, 125, 299, 220]      # buckled hood
FRONT_FASCIA_GT = [0, 200, 299, 430]     # grille + bumper crush + headlight
REAR_BUMPER_GT = [150, 210, 295, 428]    # crushed rear bumper
REAR_LAMP_GT = [0, 0, 135, 220]          # red taillight assembly


def _matches(det_box, gt_box) -> bool:
    if _iou(det_box, gt_box) >= 0.20:
        return True
    cx = (det_box[0] + det_box[2]) / 2.0
    cy = (det_box[1] + det_box[3]) / 2.0
    return gt_box[0] <= cx <= gt_box[2] and gt_box[1] <= cy <= gt_box[3]


def _require_images():
    if not (os.path.exists(FRONT_IMG) and os.path.exists(REAR_IMG)):
        pytest.skip("severe-collision reference images not present")


def test_major_front_collision_primary_is_structural():
    """Severe front-end damage must surface bumper_smash/broken_light first."""
    _require_images()
    finding = VisionPipeline().process_image(
        Image.open(FRONT_IMG).convert("RGB"), filename="white_front.jpg"
    )
    assert finding.assessment == AssessmentStatus.DAMAGED
    assert finding.detections, "severe collision must yield detections"
    primary = finding.detections[0]
    assert primary.priority == "primary"
    assert primary.label in ("bumper_smash", "broken_light"), (
        f"primary must be a major-damage class, got {primary.label}"
    )
    assert all(d.priority == "secondary" for d in finding.detections[1:])
    # Report/chips derive from the same ordered list: first class matches.
    assert finding.classifications
    assert finding.classifications[0].label == primary.label


def test_major_front_collision_zones_localized():
    """Buckled hood and crushed fascia zones must each contain a detection."""
    _require_images()
    img = Image.open(FRONT_IMG).convert("RGB")
    finding = VisionPipeline().process_image(img, filename="white_front.jpg")
    w, h = img.size
    assert any(_matches(d.bbox_xyxy, FRONT_HOOD_GT) for d in finding.detections), (
        "buckled-hood zone has no detection"
    )
    assert any(_matches(d.bbox_xyxy, FRONT_FASCIA_GT) for d in finding.detections), (
        "fascia/bumper crush zone has no detection"
    )
    for d in finding.detections:
        x1, y1, x2, y2 = d.bbox_xyxy
        assert 0 <= x1 <= x2 <= w and 0 <= y1 <= y2 <= h
        assert d.component, "every detection must carry a component estimate"


def test_major_front_collision_no_background_boxes():
    """Trees/sky strip must not be labeled damaged (the 79%-on-trees bug)."""
    _require_images()
    img = Image.open(FRONT_IMG).convert("RGB")
    w, h = img.size
    finding = VisionPipeline().process_image(img, filename="white_front.jpg")
    sky_limit = 0.12 * h
    for d in finding.detections:
        x1, y1, x2, y2 = d.bbox_xyxy
        assert not (y2 < sky_limit), (
            f"background sky-band box survived: {d.label} {d.bbox_xyxy}"
        )


def test_major_front_collision_component_vocabulary():
    """Components must come from the documented frontal set for this view."""
    _require_images()
    finding = VisionPipeline().process_image(
        Image.open(FRONT_IMG).convert("RGB"), filename="white_front.jpg"
    )
    allowed = {
        "hood", "grille_fascia", "front_bumper", "bumper", "headlight",
        "headlight_area", "front_fender", "windshield", "roof_area",
        "door", "wheel_area", "wheel_tire", "glass", "trunk_lid",
        "rear_bumper", "rear_quarter_panel", "rear_fascia", "taillight",
        "taillight_area",
    }
    comps = {d.component for d in finding.detections}
    assert comps <= allowed, f"unexpected components: {comps - allowed}"
    # Frontal view: no rear components.
    assert not (comps & {"rear_bumper", "taillight", "rear_quarter_panel"}), (
        f"frontal image mislabeled with rear components: {comps}"
    )


def test_major_rear_collision_primary_and_viewpoint():
    """Rear quarter damage: primary bumper_smash labeled rear_bumper + taillight."""
    _require_images()
    finding = VisionPipeline().process_image(
        Image.open(REAR_IMG).convert("RGB"), filename="white_rear.jpg"
    )
    assert finding.assessment == AssessmentStatus.DAMAGED
    assert finding.detections
    primary = finding.detections[0]
    assert primary.priority == "primary"
    assert primary.label == "bumper_smash"
    assert primary.component == "rear_bumper"
    assert any(_matches(d.bbox_xyxy, REAR_BUMPER_GT) for d in finding.detections)
    lamp = [d for d in finding.detections if d.component == "taillight"]
    assert lamp, "red taillight must be identified as taillight (rear view)"
    assert any(_matches(d.bbox_xyxy, REAR_LAMP_GT) for d in lamp)


def test_major_undamaged_vehicle_clean():
    """Undamaged uniform panel: valid negative, zero detections."""
    finding = VisionPipeline().process_image(
        Image.new("RGB", (640, 480), (140, 140, 140)), filename="clean.jpg"
    )
    assert finding.assessment == AssessmentStatus.NO_DAMAGE
    assert finding.detections == []


def test_major_foliage_background_not_damage():
    """Foliage + clean panel: gates/ROI must yield no detections."""
    rng = np.random.default_rng(0)
    arr = np.zeros((480, 640, 3), dtype=np.uint8)
    arr[:200, :, 1] = np.clip(100 + rng.integers(-40, 40, (200, 640)), 0, 255)
    arr[:200, :, 0] = 60
    arr[:200, :, 2] = 60
    arr[200:] = [150, 150, 150]
    finding = VisionPipeline().process_image(
        Image.fromarray(arr), filename="foliage.jpg"
    )
    assert finding.assessment == AssessmentStatus.NO_DAMAGE
    assert finding.detections == []
