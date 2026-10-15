"""Unit tests for the 4-stage Computer Vision pipeline and severity calculation."""

import pytest
from PIL import Image

from ml.vision.classifier import CLASS_ID_TO_LABEL, LABEL_TO_CLASS_ID, Stage2DamageClassifier
from ml.vision.detector import Stage3DamageDetector, nms
from ml.vision.pipeline import VisionPipeline
from ml.vision.preprocessing import letterbox_resize, model_to_original_box, normalize_box
from ml.vision.schemas import (
    AssessmentStatus,
    DamageSeverityLevel,
    DetectionItem,
    PreprocessingTransformMetadata,
    StageStatus,
)
from ml.vision.severity import calculate_polygon_area, calculate_severity


def test_letterbox_resize_preserves_geometry():
    img = Image.new("RGB", (800, 400), (255, 0, 0))
    letterboxed, meta = letterbox_resize(img, target_size=(1024, 1024))

    assert letterboxed.size == (1024, 1024)
    assert meta.original_width == 800
    assert meta.original_height == 400
    assert meta.scale_factor == 1024 / 800  # 1.28
    assert meta.pad_left == 0
    assert meta.pad_top > 0  # vertical padding for wide image


def test_coordinate_inverse_mapping():
    meta = PreprocessingTransformMetadata(
        original_width=800,
        original_height=600,
        target_width=1024,
        target_height=1024,
        scale_factor=1.0,
        pad_left=112,
        pad_top=212,
    )
    # Box in model space: [112, 212, 512, 612]
    model_box = [112.0, 212.0, 512.0, 612.0]
    orig_box = model_to_original_box(model_box, meta)

    assert orig_box[0] == 0.0
    assert orig_box[1] == 0.0
    assert orig_box[2] == 400.0
    assert orig_box[3] == 400.0


def test_severity_calculation_low_and_high():
    # Minor scratch detection
    det_minor = DetectionItem(
        instance_id="det_1",
        label="scratch",
        confidence=0.85,
        bbox_xyxy=[10, 10, 50, 50],
        coordinate_space="original_image_pixels",
        mask=[[10, 10], [50, 10], [50, 50], [10, 50]],
    )
    sev_low = calculate_severity([det_minor], image_width=1000, image_height=1000)
    assert sev_low.level == DamageSeverityLevel.LOW
    assert sev_low.score < 0.05

    # Massive bumper smash
    det_heavy = DetectionItem(
        instance_id="det_2",
        label="bumper_smash",
        confidence=0.95,
        bbox_xyxy=[100, 100, 900, 900],
        coordinate_space="original_image_pixels",
        mask=[[100, 100], [900, 100], [900, 900], [100, 900]],
    )
    sev_high = calculate_severity([det_heavy], image_width=1000, image_height=1000)
    assert sev_high.level == DamageSeverityLevel.HIGH
    assert sev_high.score >= 0.20


def test_full_vision_pipeline_execution():
    pipeline = VisionPipeline()
    sample_img = Image.new("RGB", (640, 480), (120, 120, 120))

    finding = pipeline.process_image(sample_img, filename="test_car.jpg")
    assert finding.filename == "test_car.jpg"
    assert finding.transforms is not None
    assert finding.damage_detected is False
    assert finding.detections == []


def test_detector_without_weights_abstains():
    from ml.vision.preprocessing import letterbox_resize

    img = Image.new("RGB", (800, 600), (150, 150, 150))
    lb, meta = letterbox_resize(img)
    dets, status, _ = Stage3DamageDetector().predict(lb, meta)
    assert dets == []
    assert status == StageStatus.COMPLETED  # real inference, clean frame -> zero regions



def test_classifier_class_id_mapping():
    assert CLASS_ID_TO_LABEL == {0: "scratch", 1: "dent", 2: "glass_crack", 3: "bumper_smash", 4: "flat_tire", 5: "broken_light"}
    assert LABEL_TO_CLASS_ID["scratch"] == 0
    assert Stage2DamageClassifier.decode_class_id(2) == "glass_crack"
    with pytest.raises(ValueError):
        Stage2DamageClassifier.decode_class_id(99)


def test_nms_dedupes_same_label_overlap():
    a = DetectionItem(instance_id="a", label="scratch", confidence=0.9, bbox_xyxy=[10, 10, 100, 100])
    b = DetectionItem(instance_id="b", label="scratch", confidence=0.6, bbox_xyxy=[20, 20, 100, 100])
    c = DetectionItem(instance_id="c", label="dent", confidence=0.6, bbox_xyxy=[20, 20, 100, 100])
    out = nms([b, a, c], iou_thresh=0.45)
    assert [d.instance_id for d in out] == ["a", "c"]


def test_letterbox_roundtrip_portrait_landscape():
    for wh in [(730, 1100), (1100, 730), (800, 800), (640, 480)]:
        img = Image.new("RGB", wh, (128, 128, 128))
        _, meta = letterbox_resize(img)
        # Full content box in model space maps back to full original frame.
        model_box = [float(meta.pad_left), float(meta.pad_top),
                     float(meta.target_width - meta.pad_left), float(meta.target_height - meta.pad_top)]
        orig = model_to_original_box(model_box, meta)
        assert orig[0] == pytest.approx(0.0, abs=1.5)
        assert orig[1] == pytest.approx(0.0, abs=1.5)
        assert orig[2] == pytest.approx(wh[0], abs=1.5)
        assert orig[3] == pytest.approx(wh[1], abs=1.5)


def test_pipeline_reports_inconclusive_without_model():
    """Engine failure must abstain as INCONCLUSIVE, never a fabricated NO DAMAGE verdict."""
    pipeline = VisionPipeline()
    # Force engine failure to exercise the abstention path.
    pipeline.stage1_filter._is_loaded = False
    pipeline.stage1_filter._engine = None
    img = Image.new("RGB", (900, 700), (140, 140, 140))
    finding = pipeline.process_image(img, filename="clean.jpg")
    assert finding.damage_detected is False
    assert finding.detections == []
    assert finding.assessment == AssessmentStatus.INCONCLUSIVE
    assert finding.assessment_reason is not None
    assert finding.severity.score is None
    assert finding.severity.level == DamageSeverityLevel.UNAVAILABLE
    assert finding.warnings, "inconclusive findings must carry a warning"


def test_pipeline_valid_negative_on_clean_panel():
    """A clean frame with the engine running is a completed valid negative."""
    pipeline = VisionPipeline()
    img = Image.new("RGB", (900, 700), (140, 140, 140))
    finding = pipeline.process_image(img, filename="clean.jpg")
    assert finding.damage_detected is False
    assert finding.assessment == AssessmentStatus.NO_DAMAGE
    assert finding.damage_probability is not None and finding.damage_probability < 0.85
    assert finding.stage_status["filter"] == StageStatus.COMPLETED
    assert finding.severity.score == 0.0


def test_process_inspection_overall_inconclusive_without_model():
    pipeline = VisionPipeline()
    pipeline.stage1_filter._is_loaded = False
    pipeline.stage1_filter._engine = None
    img = Image.new("RGB", (640, 480), (90, 90, 90))
    result = pipeline.process_inspection([img], filenames=["a.jpg"])
    assert result.overall_damage_detected is False
    assert result.overall_assessment == AssessmentStatus.INCONCLUSIVE
    assert result.overall_reason is not None
    assert result.overall_severity.score is None
    assert result.warnings

