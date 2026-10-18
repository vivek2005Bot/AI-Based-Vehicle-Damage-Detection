"""Unit and integration tests for the YOLOv8 / YOLOv11 CarDD detector adapter."""

import os
from unittest.mock import MagicMock, patch
import pytest
from PIL import Image

from ml.vision.yolo_cardd_detector import (
    CARDD_CLASSES,
    CARDD_TO_CANONICAL,
    MODEL_NAME,
    YoloCarddDetector,
    YoloDetectorConfig,
    get_default_yolo_device,
)
from ml.vision.pipeline import VisionPipeline
from ml.vision.schemas import AssessmentStatus, DetectionItem


def test_cardd_classes_and_mapping():
    assert len(CARDD_CLASSES) == 6
    assert CARDD_CLASSES == (
        "dent",
        "scratch",
        "crack",
        "glass shatter",
        "lamp broken",
        "tire flat",
    )
    assert CARDD_TO_CANONICAL["glass shatter"] == "glass_shatter"
    assert CARDD_TO_CANONICAL["lamp broken"] == "broken_light"
    assert CARDD_TO_CANONICAL["tire flat"] == "flat_tire"


def test_yolo_config_defaults_and_env():
    cfg = YoloDetectorConfig()
    assert cfg.enabled is False
    assert cfg.score_threshold == 0.35

    with patch.dict(
        os.environ,
        {
            "CARDD_YOLO_ENABLED": "true",
            "CARDD_YOLO_MODEL_PATH": "checkpoints/test.pt",
            "CARDD_YOLO_SCORE_THRESHOLD": "0.45",
            "CARDD_YOLO_DEVICE": "cpu",
        },
    ):
        env_cfg = YoloDetectorConfig.from_env()
        assert env_cfg.enabled is True
        assert env_cfg.model_path == "checkpoints/test.pt"
        assert env_cfg.score_threshold == 0.45
        assert env_cfg.device == "cpu"


def test_yolo_detector_disabled_status():
    detector = YoloCarddDetector(YoloDetectorConfig(enabled=False))
    assert detector.is_available is False
    status = detector.status_dict()
    assert status["enabled"] is False
    assert status["available"] is False
    assert status["backend"] == "yolo"


def test_yolo_detector_missing_weights():
    detector = YoloCarddDetector(
        YoloDetectorConfig(enabled=True, model_path="/does/not/exist_weights.pt")
    )
    assert detector.is_available is False
    assert "not found" in detector.status_dict()["reason"]


def test_mock_yolo_predict_detections():
    # Setup mock YOLO results
    mock_box1 = MagicMock()
    mock_box1.cls.item.return_value = 0  # dent
    mock_box1.conf.item.return_value = 0.88
    mock_box1.xyxy = MagicMock()
    mock_box1.xyxy.tolist.return_value = [50.0, 60.0, 180.0, 210.0]

    mock_box2 = MagicMock()
    mock_box2.cls.item.return_value = 3  # glass shatter
    mock_box2.conf.item.return_value = 0.92
    mock_box2.xyxy = MagicMock()
    mock_box2.xyxy.tolist.return_value = [200.0, 150.0, 320.0, 280.0]

    mock_boxes = [mock_box1, mock_box2]
    mock_boxes_obj = MagicMock()
    mock_boxes_obj.__len__.return_value = 2
    mock_boxes_obj.__getitem__.side_effect = lambda idx: mock_boxes[idx]
    mock_boxes_obj.cls = [b.cls for b in mock_boxes]
    mock_boxes_obj.conf = [b.conf for b in mock_boxes]
    mock_boxes_obj.xyxy = [b.xyxy for b in mock_boxes]

    # Polygon contours
    mock_masks = MagicMock()
    mock_masks.xy = [
        [[50, 60], [180, 60], [180, 210], [50, 210]],
        [[200, 150], [320, 150], [320, 280], [200, 280]],
    ]

    mock_result = MagicMock()
    mock_result.boxes = mock_boxes_obj
    mock_result.masks = mock_masks

    mock_yolo_instance = MagicMock()
    mock_yolo_instance.predict.return_value = [mock_result]

    detector = YoloCarddDetector(YoloDetectorConfig(enabled=True))
    detector._is_available = True
    detector._model = mock_yolo_instance

    img = Image.new("RGB", (640, 480), (120, 120, 120))
    detections, model_name, latency = detector.predict_detections(img, 640, 480)

    assert model_name == MODEL_NAME
    assert len(detections) == 2
    assert detections[0]["label"] == "dent"
    assert detections[0]["source_label"] == "dent"
    assert detections[0]["confidence"] == 0.88
    assert detections[0]["bbox_xyxy"] == [50.0, 60.0, 180.0, 210.0]
    assert len(detections[0]["mask"]) == 4

    assert detections[1]["label"] == "glass_shatter"
    assert detections[1]["source_label"] == "glass shatter"
    assert detections[1]["confidence"] == 0.92


def test_pipeline_with_yolo_detector():
    """Verify VisionPipeline dynamically incorporates YOLO detections."""
    class FakeYoloDetector:
        is_available = True
        status = None

        def predict_detections(self, image, image_width, image_height):
            return [
                {
                    "instance_id": "yolo_001",
                    "label": "scratch",
                    "confidence": 0.91,
                    "bbox_xyxy": [100.0, 100.0, 300.0, 250.0],
                    "coordinate_space": "original_image_pixels",
                    "mask": [[100, 100], [300, 100], [300, 250], [100, 250]],
                    "source_label": "scratch",
                }
            ], MODEL_NAME, 12.5

        def status_dict(self):
            return {"enabled": True, "available": True, "backend": "yolo", "model": MODEL_NAME}

    img = Image.new("RGB", (640, 480), (150, 150, 150))
    pipe = VisionPipeline(cardd_detector=FakeYoloDetector())
    finding = pipe.process_image(img, filename="car_yolo_test.jpg")

    assert finding.assessment == AssessmentStatus.DAMAGED
    assert finding.detector_model == MODEL_NAME
    assert any(d.instance_id == "yolo_001" for d in finding.detections)
