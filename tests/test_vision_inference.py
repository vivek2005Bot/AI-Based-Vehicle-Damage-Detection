"""Tests for the classical-CV damage inference engine and pipeline integration."""

import pytest
from PIL import Image, ImageDraw

from ml.vision.classical_engine import ClassicalDamageEngine
from ml.vision.detector import Stage3DamageDetector
from ml.vision.pipeline import VisionPipeline
from ml.vision.preprocessing import letterbox_resize
from ml.vision.schemas import AssessmentStatus, StageStatus

REPO_ROOT = __file__.rsplit("/tests/", 1)[0]
FIXTURE_DIR = (
    f"{REPO_ROOT}/private_uploads/insp_0079e9eb-040c-429d-b8d7-ae8fcf7ac724"
)
DAMAGED_MIRROR_IMG = f"{FIXTURE_DIR}/9674b2077a7243228116b24977e6cf5d.jpg"
DAMAGED_HOOD_IMG = f"{FIXTURE_DIR}/b720690c2e0a4445969ea38ded046500.jpg"


def _synthetic_scratched_panel() -> Image.Image:
    """Panel with a drawn scratch line and a dent-like shading blob."""
    img = Image.new("RGB", (640, 480), (150, 150, 150))
    d = ImageDraw.Draw(img)
    d.line([(100, 240), (500, 260)], fill=(80, 80, 80), width=3)
    d.ellipse([220, 300, 420, 420], fill=(115, 115, 120))
    return img


def test_engine_returns_no_regions_on_flat_panel():
    eng = ClassicalDamageEngine()
    res = eng.analyze(Image.new("RGB", (640, 480), (120, 120, 120)))
    assert res.probability == 0.0
    assert res.regions == []


def test_engine_returns_no_regions_on_smooth_gradient():
    """Quantization banding on a smooth ramp must not register as damage."""
    img = Image.new("RGB", (640, 480))
    d = ImageDraw.Draw(img)
    for x in range(640):
        v = int(80 + 100 * x / 640)
        d.line([(x, 0), (x, 480)], fill=(v, v, v))
    res = ClassicalDamageEngine().analyze(img)
    assert res.probability < 0.85
    assert res.regions == []


def test_engine_detects_synthetic_damage():
    res = ClassicalDamageEngine().analyze(_synthetic_scratched_panel())
    assert res.probability >= 0.85
    assert res.regions
    assert all(0.0 <= r.confidence <= 1.0 for r in res.regions)
    assert all(r.polygon for r in res.regions)  # real pixel contours present


def test_engine_rejects_degenerate_input():
    with pytest.raises(ValueError):
        ClassicalDamageEngine().analyze(Image.new("RGB", (10, 10), (0, 0, 0)))


def test_engine_analysis_is_cached_per_image():
    eng = ClassicalDamageEngine()
    img = _synthetic_scratched_panel()
    first = eng.analyze(img)
    second = eng.analyze(img)
    assert first is second  # same cached object -> stages share one analysis


def test_pipeline_valid_negative_on_clean_panel():
    finding = VisionPipeline().process_image(
        Image.new("RGB", (700, 500), (135, 135, 135)), filename="clean.jpg"
    )
    assert finding.assessment == AssessmentStatus.NO_DAMAGE
    assert finding.damage_detected is False
    assert finding.warnings == []
    assert finding.stage_status["filter"] == StageStatus.COMPLETED


def test_pipeline_detects_synthetic_damage():
    finding = VisionPipeline().process_image(_synthetic_scratched_panel(), filename="dmg.jpg")
    assert finding.assessment == AssessmentStatus.DAMAGED
    assert finding.damage_detected is True
    assert finding.damage_probability is not None and finding.damage_probability >= 0.85
    assert finding.detections, "damaged finding must carry localized detections"
    assert finding.classifications
    for det in finding.detections:
        assert 0.0 <= det.confidence <= 1.0
        assert len(det.bbox_xyxy) == 4
        assert det.coordinate_space == "original_image_pixels"


def test_process_inspection_corrupt_bytes_yields_inconclusive():
    """A corrupt upload must never be reported as NO DAMAGE or crash aggregation."""
    result = VisionPipeline().process_inspection(
        [b"definitely-not-an-image"], filenames=["bad.jpg"]
    )
    assert result.overall_assessment == AssessmentStatus.INCONCLUSIVE
    assert result.overall_reason is not None
    # Exception detail must not leak into user-facing text.
    assert "Traceback" not in (result.overall_reason or "")
    assert "sha256" not in (result.overall_reason or "")


def test_process_inspection_mixed_valid_and_corrupt():
    result = VisionPipeline().process_inspection(
        [_synthetic_scratched_panel(), b"not-an-image"],
        filenames=["ok.jpg", "bad.jpg"],
    )
    # Damaged evidence wins; corrupt image contributes an inconclusive
    # finding without overwriting or crashing aggregation.
    assert result.overall_assessment == AssessmentStatus.DAMAGED
    corrupt = [f for f in result.images if f.filename == "bad.jpg"]
    assert corrupt and corrupt[0].assessment == AssessmentStatus.INCONCLUSIVE


def test_process_inspection_dedupes_inconclusive_reasons():
    """Repeated identical inconclusive reasons must appear exactly once."""
    pipeline = VisionPipeline()
    pipeline.stage1_filter._is_loaded = False
    pipeline.stage1_filter._engine = None
    # Distinct contents (varying size) so content-dedup does not apply.
    imgs = [Image.new("RGB", (400 + 8 * i, 300), (90, 90, 90)) for i in range(3)]
    result = pipeline.process_inspection(imgs, filenames=["a.jpg", "b.jpg", "c.jpg"])
    assert result.overall_assessment == AssessmentStatus.INCONCLUSIVE
    assert result.warnings, "inconclusive aggregation must emit a warning"
    assert len(result.warnings) == len(set(result.warnings)), (
        "duplicate reason strings must be deduplicated"
    )
    # Old bug: each reason was appended twice (reason + identical warning),
    # and repeated once per image (6 messages for 3 images). Now: exactly one.
    assert len(result.warnings) == 1


def test_repeated_image_selection_analyzed_once():
    """Same image selected twice must be analyzed once and flagged once."""
    img = _synthetic_scratched_panel()
    result = VisionPipeline().process_inspection(
        [img, img], filenames=["first.jpg", "second_pick.jpg"]
    )
    assert len(result.images) == 1, "duplicate content must be skipped"
    assert result.overall_assessment == AssessmentStatus.DAMAGED
    assert any("duplicate image upload" in w for w in result.warnings)


def test_stage3_detect_on_real_damaged_photo():
    """End-to-end on the known-damaged reference upload (skipped if absent)."""
    import os

    if not os.path.exists(DAMAGED_HOOD_IMG):
        pytest.skip("reference upload not present")
    img = Image.open(DAMAGED_HOOD_IMG).convert("RGB")
    lb, meta = letterbox_resize(img)
    dets, status, _ = Stage3DamageDetector().predict(lb, meta)
    assert status == StageStatus.COMPLETED
    assert dets, "known-damaged photo must yield detections"
    w, h = img.size
    for d in dets:
        x1, y1, x2, y2 = d.bbox_xyxy
        assert 0.0 <= x1 <= x2 <= w + 1.0
        assert 0.0 <= y1 <= y2 <= h + 1.0


def test_pipeline_on_real_damaged_photos():
    import os

    paths = [p for p in (DAMAGED_MIRROR_IMG, DAMAGED_HOOD_IMG) if os.path.exists(p)]
    if not paths:
        pytest.skip("reference uploads not present")
    pipeline = VisionPipeline()
    for p in paths:
        finding = pipeline.process_image(Image.open(p).convert("RGB"), filename="ref.jpg")
        assert finding.assessment == AssessmentStatus.DAMAGED, (
            f"known-damaged image {p} must be flagged damaged"
        )
        assert finding.damage_probability is not None
        assert finding.damage_probability >= 0.85
        assert finding.detections
        assert finding.severity.score is not None
        # Every stage must report completed real inference.
        for stage, status in finding.stage_status.items():
            assert status == StageStatus.COMPLETED, f"stage {stage} = {status}"

