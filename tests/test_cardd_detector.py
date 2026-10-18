"""Tests for the optional CarDD Mask R-CNN adapter (mocked inference)."""

import os

import pytest
from PIL import Image

from ml.vision.cardd_detector import (
    CARDD_CLASSES,
    CarddDamageDetector,
    CarddDetectorConfig,
    clamp_box_xyxy,
    decode_cardd_class_id,
    is_cardd_finetuned_checkpoint,
    map_cardd_label,
    resolve_cardd_device,
)
from ml.vision.pipeline import VisionPipeline
from ml.vision.schemas import AssessmentStatus


def test_resolve_cardd_device_mac_cuda_fallback():
    assert resolve_cardd_device("cpu") == "cpu"
    # On macOS where CUDA is not present, requesting cuda / cuda:0 falls back to cpu
    assert resolve_cardd_device("cuda") == "cpu"
    assert resolve_cardd_device("cuda:0") == "cpu"


def test_cardd_class_order_matches_official_config():
    assert CARDD_CLASSES == (
        "dent", "scratch", "crack", "glass shatter", "lamp broken", "tire flat",
    )


def test_decode_class_ids_cover_all_six():
    assert [decode_cardd_class_id(i) for i in range(6)] == list(CARDD_CLASSES)
    with pytest.raises(ValueError):
        decode_cardd_class_id(6)
    with pytest.raises(ValueError):
        decode_cardd_class_id(99)


def test_mapping_preserves_glass_and_crack_explicitly():
    assert map_cardd_label("crack") == "crack"
    assert map_cardd_label("glass shatter") == "glass_shatter"
    assert map_cardd_label("dent") == "dent"
    assert map_cardd_label("scratch") == "scratch"
    assert map_cardd_label("lamp broken") == "broken_light"
    assert map_cardd_label("tire flat") == "flat_tire"
    with pytest.raises(ValueError):
        map_cardd_label("bumper_smash")


def test_box_clamping_handles_edges_and_degenerate():
    out = clamp_box_xyxy([-20, -5, 200, 300], 100, 80)
    assert out == [0.0, 0.0, 100.0, 80.0]
    assert clamp_box_xyxy([50, 50, 10, 10], 100, 100) is None
    assert clamp_box_xyxy([10, 10, 10, 50], 100, 100) is None
    assert clamp_box_xyxy([1, 2, 3], 100, 100) is None


def test_coco_checkpoint_rejected_as_production_model():
    coco = "mask_rcnn_r50_fpn_2x_coco_bbox_mAP-0.392__segm_mAP-0.354_20200505_003907-3e542a40.pth"
    assert is_cardd_finetuned_checkpoint(coco) is False
    assert is_cardd_finetuned_checkpoint("work_dirs/cardd_mask_rcnn_r50_fpn_2x/epoch_12.pth") is True
    assert is_cardd_finetuned_checkpoint("checkpoints/cardd_epoch_best.pth") is True
    assert is_cardd_finetuned_checkpoint("some/random_model.pth") is False


def test_disabled_flag_keeps_classical_behavior():
    det = CarddDamageDetector(CarddDetectorConfig(enabled=False))
    assert det.is_available is False
    assert det.status_dict()["enabled"] is False
    finding = VisionPipeline().process_image(
        Image.new("RGB", (700, 500), (135, 135, 135)), filename="clean.jpg"
    )
    assert finding.assessment == AssessmentStatus.NO_DAMAGE

def test_missing_checkpoint_disables_safely_with_status():
    cfg = CarddDetectorConfig(
        enabled=True,
        config_path="./configs/cardd/mask_rcnn_r50_fpn_2x_cardd.py",
        checkpoint_path="./does/not/exist_epoch_1.pth",
    )
    det = CarddDamageDetector(cfg)
    assert det.is_available is False
    assert "not found" in det.status_dict()["reason"]


def test_coco_weights_disables_with_provenance_warning(tmp_path):
    fake_coco = tmp_path / "mask_rcnn_r50_fpn_2x_coco_bbox_mAP-0.392__segm_mAP-0.354_20200505_003907-3e542a40.pth"
    fake_coco.write_bytes(b"fake")
    cfg = CarddDetectorConfig(
        enabled=True,
        config_path="./configs/cardd/mask_rcnn_r50_fpn_2x_cardd.py",
        checkpoint_path=str(fake_coco),
    )
    det = CarddDamageDetector(cfg)
    assert det.is_available is False
    assert "COCO" in det.status_dict()["reason"]


def test_parse_empty_and_multi_class_outputs():
    det = CarddDamageDetector(CarddDetectorConfig(enabled=False, score_threshold=0.5))
    W, H = 640, 480
    assert det.parse_raw_result(None, W, H) == []
    assert det.parse_raw_result(([], []), W, H) == []
    raw = (
        [[[10, 10, 100, 100, 0.9]], [], [], [[200, 200, 300, 300, 0.75]], [], []],
        [[None], None, None, [None], None, None],
    )
    out = det.parse_raw_result(raw, W, H)
    assert len(out) == 2
    assert out[0]["label"] == "dent" and out[0]["source_label"] == "dent"
    assert out[1]["label"] == "glass_shatter" and out[1]["source_label"] == "glass shatter"
    assert all(d["coordinate_space"] == "original_image_pixels" for d in out)
    det_hi = CarddDamageDetector(CarddDetectorConfig(enabled=False, score_threshold=0.95))
    assert det_hi.parse_raw_result(raw, W, H) == []


def test_parse_handles_unexpected_structure_gracefully():
    det = CarddDamageDetector(CarddDetectorConfig(enabled=False))
    assert det.parse_raw_result("garbage", 100, 100) == []
    assert det.parse_raw_result(([999, 999], None), 100, 100) == []

def test_parse_rejects_invalid_and_out_of_frame_boxes():
    det = CarddDamageDetector(CarddDetectorConfig(enabled=False, score_threshold=0.1))
    W, H = 100, 100
    raw = (
        [[[50, 50, 10, 10, 0.9], [-50, -50, 500, 500, 0.8], [10, 10, 20, 20, 0.7]], [], [], [], [], []],
        [[None, None, None], None, None, None, None, None],
    )
    out = det.parse_raw_result(raw, W, H)
    boxes = [d["bbox_xyxy"] for d in out]
    assert [0.0, 0.0, 100.0, 100.0] in boxes
    assert [10.0, 10.0, 20.0, 20.0] in boxes
    assert len(out) == 2

def test_mask_parsing_handles_arrays_and_empty_masks():
    """Phase 8.5: real mask arrays -> polygons; empty masks stay box-only."""
    np = pytest.importorskip("numpy")
    det = CarddDamageDetector(CarddDetectorConfig(enabled=False, score_threshold=0.1))
    W, H = 100, 100
    rect = np.zeros((H, W), dtype=np.float32)
    rect[30:60, 20:70] = 1.0
    empty = np.zeros((H, W), dtype=np.float32)
    raw = (
        [[[10, 10, 80, 80, 0.9], [5, 5, 50, 50, 0.8]], [], [], [], [], []],
        [[rect, empty], None, None, None, None, None],
    )
    out = det.parse_raw_result(raw, W, H)
    assert len(out) == 2
    assert out[0]["mask"] is not None and len(out[0]["mask"]) >= 3
    xs = [p[0] for p in out[0]["mask"]]
    ys = [p[1] for p in out[0]["mask"]]
    assert min(xs) >= 15 and max(xs) <= 75  # contour tracks the rect region
    assert min(ys) >= 25 and max(ys) <= 65
    assert out[1]["mask"] is None  # empty mask -> valid box-only detection
    assert CarddDamageDetector._mask_to_polygon(None, W, H) is None
    assert CarddDamageDetector._mask_to_polygon([], W, H) is None


def test_adapter_preserves_preprocessing_coordinates():
    """Phase 8.6: CarDD boxes merge into the letterboxed pipeline in-frame."""
    raw = (
        [[[20, 20, 120, 120, 0.9]], [], [], [], [], []],
        [[None], None, None, None, None, None],
    )

    class _FakeCardd:
        is_available = True
        status = None

        def predict_detections(self, image, image_width, image_height):
            det = CarddDamageDetector(CarddDetectorConfig(enabled=False))
            return det.parse_raw_result(raw, image_width, image_height), "cardd_test", 1.0

    from PIL import ImageDraw
    img = Image.new("RGB", (640, 480), (150, 150, 150))
    d = ImageDraw.Draw(img)
    d.line([(100, 240), (500, 260)], fill=(80, 80, 80), width=3)
    d.ellipse([220, 300, 420, 420], fill=(115, 115, 120))
    finding = VisionPipeline(cardd_detector=_FakeCardd()).process_image(img, filename="coord.jpg")
    cardd_boxes = [x.bbox_xyxy for x in finding.detections if x.instance_id.startswith("cardd_")]
    assert cardd_boxes, "fused CarDD box must be present"
    for x1, y1, x2, y2 in cardd_boxes:
        assert 0.0 <= x1 < x2 <= 640 and 0.0 <= y1 < y2 <= 480


def test_pipeline_status_path_reports_disabled_by_default(monkeypatch):
    monkeypatch.delenv("CARDD_MODEL_ENABLED", raising=False)
    monkeypatch.delenv("CARDD_YOLO_ENABLED", raising=False)
    monkeypatch.setenv("CARDD_MODEL_BACKEND", "disabled")
    st = VisionPipeline().cardd_status()
    assert st["enabled"] is False and st["available"] is False


def test_opt_in_smoke_real_checkpoint():
    ckpt = os.getenv("CARDD_SMOKE_CHECKPOINT", "")
    img_path = os.getenv("CARDD_SMOKE_IMAGE", "")
    if not ckpt or not img_path:
        pytest.skip("CARDD_SMOKE_CHECKPOINT/CARDD_SMOKE_IMAGE not set")
    pytest.importorskip("mmdet")
    cfg = CarddDetectorConfig(
        enabled=True,
        config_path=os.getenv("CARDD_MODEL_CONFIG", "./configs/cardd/mask_rcnn_r50_fpn_2x_cardd.py"),
        checkpoint_path=ckpt,
    )
    det = CarddDamageDetector(cfg)
    assert det.is_available, det.status_dict()["reason"]
    img = Image.open(img_path).convert("RGB")
    parsed, name, latency = det.predict_detections(img, *img.size)
    assert isinstance(parsed, list) and name.startswith("cardd_")
    assert latency >= 0


def test_detection_item_accepts_source_label():
    from ml.vision.schemas import DetectionItem
    d = DetectionItem(
        instance_id="cardd_000", label="glass_shatter", confidence=0.8,
        bbox_xyxy=[1, 1, 10, 10], source_label="glass shatter",
    )
    assert d.source_label == "glass shatter"
    d2 = DetectionItem(
        instance_id="det_000", label="dent", confidence=0.8,
        bbox_xyxy=[1, 1, 10, 10],
    )
    assert d2.source_label is None
def test_pipeline_fusion_merges_cardd_with_classical():
    """Enabled+available CarDD merges boxes; classical never dropped silently."""
    from ml.vision.schemas import DetectionItem

    raw = (
        [[[20, 20, 120, 120, 0.9]], [], [], [], [], []],
        [[None], None, None, None, None, None],
    )

    class _FakeCardd:
        is_available = True
        status = None

        def predict_detections(self, image, image_width, image_height):
            det = CarddDamageDetector(CarddDetectorConfig(enabled=False))
            return det.parse_raw_result(raw, image_width, image_height), "cardd_test", 1.0

    from PIL import ImageDraw
    img = Image.new("RGB", (640, 480), (150, 150, 150))
    d = ImageDraw.Draw(img)
    d.line([(100, 240), (500, 260)], fill=(80, 80, 80), width=3)
    d.ellipse([220, 300, 420, 420], fill=(115, 115, 120))

    pipe = VisionPipeline(cardd_detector=_FakeCardd())
    finding = pipe.process_image(img, filename="fusion.jpg")
    assert finding.assessment == AssessmentStatus.DAMAGED
    assert finding.detector_model == "cardd_test"
    assert any(getattr(x, "instance_id", "").startswith("cardd_") for x in finding.detections)


def test_pipeline_cardd_failure_falls_back_with_warning():
    """CarDD raising at inference keeps classical output + warning (no crash)."""
    class _Boom:
        is_available = True
        status = None

        def predict_detections(self, image, image_width, image_height):
            raise RuntimeError("cuda oom (simulated)")

    from PIL import ImageDraw
    img = Image.new("RGB", (640, 480), (150, 150, 150))
    d = ImageDraw.Draw(img)
    d.line([(100, 240), (500, 260)], fill=(80, 80, 80), width=3)
    d.ellipse([220, 300, 420, 420], fill=(115, 115, 120))

    pipe = VisionPipeline(cardd_detector=_Boom())
    finding = pipe.process_image(img, filename="fallback.jpg")
    assert finding.assessment == AssessmentStatus.DAMAGED
    assert finding.detections, "classical detections must be retained"
    assert any("CarDD" in w for w in finding.warnings)


def test_pipeline_cardd_enabled_but_unavailable_warns_not_inconclusive():
    """Enabled-but-unverified CarDD on a clean frame stays NO_DAMAGE + notice."""
    cfg = CarddDetectorConfig(
        enabled=True,
        config_path="./configs/cardd/mask_rcnn_r50_fpn_2x_cardd.py",
        checkpoint_path="./does/not/exist_epoch_1.pth",
    )
    det = CarddDamageDetector(cfg)
    assert det.is_available is False
    pipe = VisionPipeline(cardd_detector=det)
    finding = pipe.process_image(
        Image.new("RGB", (700, 500), (135, 135, 135)), filename="clean.jpg"
    )
    assert finding.assessment == AssessmentStatus.NO_DAMAGE
    assert any("CarDD unavailable" in w for w in finding.warnings)
def test_result_carries_cardd_provenance():
    """process_inspection surfaces CarDD flags; fusion stamps the model name."""
    from ml.vision.schemas import DetectionItem

    raw = (
        [[[20, 20, 120, 120, 0.9]], [], [], [], [], []],
        [[None], None, None, None, None, None],
    )

    class _FakeCardd:
        is_available = True
        status = None

        def predict_detections(self, image, image_width, image_height):
            det = CarddDamageDetector(CarddDetectorConfig(enabled=False))
            return det.parse_raw_result(raw, image_width, image_height), "cardd_test", 1.0

    from PIL import ImageDraw
    img = Image.new("RGB", (640, 480), (150, 150, 150))
    d = ImageDraw.Draw(img)
    d.line([(100, 240), (500, 260)], fill=(80, 80, 80), width=3)
    d.ellipse([220, 300, 420, 420], fill=(115, 115, 120))

    pipe = VisionPipeline(cardd_detector=_FakeCardd())
    res = pipe.process_inspection([img], filenames=["fusion.jpg"])
    assert res.overall_assessment == AssessmentStatus.DAMAGED
    assert res.images[0].detector_model == "cardd_test"


def test_result_defaults_to_classical_provenance(monkeypatch):
    monkeypatch.delenv("CARDD_MODEL_ENABLED", raising=False)
    monkeypatch.delenv("CARDD_YOLO_ENABLED", raising=False)
    monkeypatch.setenv("CARDD_MODEL_BACKEND", "disabled")
    res = VisionPipeline().process_inspection(
        [Image.new("RGB", (700, 500), (135, 135, 135))], filenames=["clean.jpg"]
    )
    assert res.cardd_enabled is False and res.cardd_available is False
    assert res.cardd_model is None
    assert res.images[0].detector_model == "classical_cv_v1"
def test_cardd_labels_have_explicit_severity_weights():
    """New CarDD labels must not fall through to the silent 0.10 fallback."""
    from ml.vision.severity import DEFAULT_CLASS_WEIGHTS, calculate_severity
    from ml.vision.schemas import DetectionItem
    import yaml

    yaml_weights = yaml.safe_load(
        open("ml/config/severity.yaml")
    )["class_weights"]
    for label in ("glass_shatter", "crack", "tire_flat", "flat_tire"):
        assert label in DEFAULT_CLASS_WEIGHTS, f"{label} missing in code weights"
        assert label in yaml_weights, f"{label} missing in severity.yaml"
        assert DEFAULT_CLASS_WEIGHTS[label] == yaml_weights[label]

    # Behavioral check: 50%-frame glass_shatter (0.25) must outscore
    # 50%-frame crack (0.10).
    box = [0, 0, 100, 50]
    mask = [[0, 0], [100, 0], [100, 50], [0, 50]]
    s_glass = calculate_severity(
        [DetectionItem(instance_id="g", label="glass_shatter",
                        confidence=0.9, bbox_xyxy=box, mask=mask)],
        image_width=100, image_height=100,
    )
    s_crack = calculate_severity(
        [DetectionItem(instance_id="c", label="crack",
                        confidence=0.9, bbox_xyxy=box, mask=mask)],
        image_width=100, image_height=100,
    )
    assert s_glass.score == 0.125
    assert s_crack.score == 0.05
    assert s_glass.score is not None and s_crack.score is not None
    assert s_glass.score > s_crack.score


def test_meta_endpoint_reports_cardd_block(monkeypatch):
    """API contract: /api/v1/meta exposes cardd_detector status, truthful models."""
    monkeypatch.setenv("CARDD_MODEL_ENABLED", "false")
    monkeypatch.setenv("CARDD_YOLO_ENABLED", "false")
    monkeypatch.setenv("CARDD_MODEL_BACKEND", "disabled")
    import asyncio
    from httpx import ASGITransport, AsyncClient
    from backend.app.db.session import init_db
    from backend.app.main import app

    async def _go():
        await init_db()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.get("/api/v1/meta")
            assert r.status_code == 200
            body = r.json()
            assert body["models"]["filter"] == "classical_cv_v1"
            assert body["models"]["detector"] == "classical_cv_v1"
            cardd = body["models"]["cardd_detector"]
            assert cardd["model"] in ("cardd_mask_rcnn_r50_fpn_2x", "cardd_yolov8_seg")
            assert cardd["enabled"] is False and cardd["available"] is False
            assert body["capabilities"]["cardd_detector_enabled"] is False

    asyncio.run(_go())


def test_backward_compat_old_payloads_still_parse():
    """New optional fields must not break previously stored findings/results."""
    from ml.vision.schemas import DetectionItem, ImageFinding, VisionPipelineResult, SeverityAssessment

    d = DetectionItem(instance_id="det_000", label="dent", confidence=0.8,
                      bbox_xyxy=[1, 1, 10, 10])
    assert d.source_label is None and d.coordinate_space == "original_image_pixels"

    f = ImageFinding(image_id="img_x", filename="a.jpg", damage_detected=False)
    assert f.detector_model is None and f.assessment.value == "inconclusive"

    r = VisionPipelineResult(
        inspection_id="i", overall_damage_detected=False,
        overall_severity=SeverityAssessment(score=0.0, level="low"))
    assert r.cardd_enabled is False and r.cardd_model is None


