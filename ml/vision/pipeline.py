"""4-Stage Computer Vision Pipeline Coordinator.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 8.1:
  Stage 1: Damaged vs. Undamaged binary filter
  Stage 2: Damage taxonomy classification
  Stage 3: Damage detection (bounding boxes)
  Stage 4: Instance segmentation (polygon masks)
  Severity: Relative damage ratio r = A_mask / A_veh and score S = sum(w_c * r_c)
"""

from __future__ import annotations

import hashlib
import logging
import time
import uuid
from pathlib import Path
from typing import List, Optional, Union
from PIL import Image

from ml.vision.classifier import Stage2DamageClassifier
from ml.vision.detector import Stage3DamageDetector
from ml.vision.filter_model import Stage1FilterModel
from ml.vision.preprocessing import decode_image_bytes, letterbox_resize, load_image_from_file
from ml.vision.schemas import (
    AssessmentStatus,
    ClassificationItem,
    DamageSeverityLevel,
    ImageFinding,
    SeverityAssessment,
    StageStatus,
    VisionPipelineResult,
)
from ml.vision.segmenter import Stage4DamageSegmenter
from ml.vision.severity import calculate_severity

logger = logging.getLogger(__name__)


class VisionPipeline:
    """End-to-end 4-stage vehicle damage inspection pipeline."""

    def __init__(
        self,
        filter_threshold: float = 0.85,
        target_size: tuple[int, int] = (1024, 1024),
    ):
        from ml.vision.classical_engine import ClassicalDamageEngine

        self.target_size = target_size
        # One shared engine => one image analysis (cached) feeds all 4 stages.
        self._engine = ClassicalDamageEngine()
        self.stage1_filter = Stage1FilterModel(threshold=filter_threshold)
        self.stage1_filter._engine = self._engine
        self.stage1_filter._is_loaded = True
        self.stage2_classifier = Stage2DamageClassifier(engine=self._engine)
        self.stage3_detector = Stage3DamageDetector(engine=self._engine)
        self.stage4_segmenter = Stage4DamageSegmenter()


    def process_image(
        self,
        image_input: Union[bytes, str, Path, Image.Image],
        filename: str = "vehicle_image.jpg",
        image_id: Optional[str] = None,
    ) -> ImageFinding:
        """Execute the full 4-stage pipeline for a single image."""
        img_id = image_id or f"img_{uuid.uuid4().hex[:8]}"
        latencies: dict[str, float] = {}

        # 1. Decode & Preprocess
        t0 = time.perf_counter()
        if isinstance(image_input, bytes):
            image = decode_image_bytes(image_input)
        elif isinstance(image_input, (str, Path)):
            image = load_image_from_file(image_input)
        elif isinstance(image_input, Image.Image):
            image = image_input
        else:
            raise TypeError(f"Unsupported image_input type: {type(image_input)}")

        # Preprocessing metadata for coordinate mapping. The classical engine
        # analyzes the unpadded source image directly: letterbox padding exists
        # only for future neural backends, and feeding the padded canvas to the
        # engine used to create artificial gray-seam edges along the pad border
        # that fired the chaos/crack channels (border-hugging false positives).
        _, transforms = letterbox_resize(image, target_size=self.target_size)
        latencies["preprocessing"] = round((time.perf_counter() - t0) * 1000.0, 2)

        # 2. Stage 1: Damaged vs. Undamaged Filter
        is_damaged, prob, s1_status, s1_latency = self.stage1_filter.predict(image)
        latencies["stage1_filter"] = s1_latency

        stage_status = {
            "filter": s1_status,
            "classification": StageStatus.NOT_RUN,
            "detection": StageStatus.NOT_RUN,
            "segmentation": StageStatus.NOT_RUN,
            "severity": StageStatus.NOT_RUN,
        }

        # Early exit if predicted intact (below calibrated threshold)
        if not is_damaged:
            stage_status["classification"] = StageStatus.SKIPPED_INTACT
            stage_status["detection"] = StageStatus.SKIPPED_INTACT
            stage_status["segmentation"] = StageStatus.SKIPPED_INTACT
            stage_status["severity"] = StageStatus.SKIPPED_INTACT

            if s1_status == StageStatus.MODEL_UNAVAILABLE:
                assessment = AssessmentStatus.INCONCLUSIVE
                reason = "Vision model unavailable; unable to assess damage. Manual review required."
                sev = SeverityAssessment(
                    score=None,
                    level=DamageSeverityLevel.UNAVAILABLE,
                    method="relative_area_weighted_by_class",
                    calibrated=False,
                    affected_pixel_area_total=None,
                    vehicle_pixel_area=float(transforms.original_width * transforms.original_height),
                    relative_damage_ratio=None,
                )
            elif s1_status == StageStatus.FAILED:
                assessment = AssessmentStatus.INCONCLUSIVE
                reason = "Vision inference failed; unable to assess damage. Manual review required."
                sev = SeverityAssessment(
                    score=None,
                    level=DamageSeverityLevel.UNAVAILABLE,
                    method="relative_area_weighted_by_class",
                    calibrated=False,
                    affected_pixel_area_total=None,
                    vehicle_pixel_area=float(transforms.original_width * transforms.original_height),
                    relative_damage_ratio=None,
                )
            else:
                assessment = AssessmentStatus.NO_DAMAGE
                reason = "Model completed inference with no damage above threshold."
                sev = SeverityAssessment(
                    score=0.0,
                    level=DamageSeverityLevel.LOW,
                    method="relative_area_weighted_by_class",
                    calibrated=False,
                    affected_pixel_area_total=0.0,
                    vehicle_pixel_area=float(transforms.original_width * transforms.original_height),
                    relative_damage_ratio=0.0,
                )

            return ImageFinding(
                image_id=img_id,
                filename=filename,
                damage_detected=False,
                assessment=assessment,
                assessment_reason=reason,
                damage_probability=prob,
                filter_threshold=self.stage1_filter.threshold,
                filter_model=self.stage1_filter.model_name,
                classifications=[],
                detections=[],
                severity=sev,
                stage_status=stage_status,
                transforms=transforms,
                warnings=[] if assessment == AssessmentStatus.NO_DAMAGE else [reason],
                latency_ms=latencies,
            )

        # 3. Stage 2: Damage Classification
        classes, s2_status, s2_latency = self.stage2_classifier.predict(image)
        stage_status["classification"] = s2_status
        latencies["stage2_classification"] = s2_latency

        # 4. Stage 3: Damage Detection (+ confidence gate)
        raw_detections, s3_status, s3_latency = self.stage3_detector.predict(image, transforms)
        # Confidence gate only. Spatial de-duplication (class-agnostic IoU/IoM
        # suppression) already runs once inside the classical engine — do not
        # apply a second NMS pass here: duplicate NMS stages can disagree with
        # each other and drop correct boxes (double suppression).
        raw_detections = [
            d for d in raw_detections if d.confidence >= self.stage3_detector.confidence_threshold
        ]
        if s3_status == StageStatus.COMPLETED and not raw_detections:
            s3_status = StageStatus.COMPLETED
        stage_status["detection"] = s3_status
        latencies["stage3_detection"] = s3_latency

        # No localizations -> distinguish valid negative vs inconclusive.
        if not raw_detections:
            stage_status["segmentation"] = StageStatus.SKIPPED_INTACT
            stage_status["severity"] = StageStatus.SKIPPED_INTACT
            model_missing = s3_status in (StageStatus.MODEL_UNAVAILABLE, StageStatus.FAILED) or s2_status in (
                StageStatus.MODEL_UNAVAILABLE, StageStatus.FAILED)
            if is_damaged and not model_missing:
                # Filter measured damage mass above threshold but no region
                # survived the confidence gate -> contradictory evidence.
                assessment = AssessmentStatus.INCONCLUSIVE
                reason = (
                    "Damage probability exceeded threshold but no region passed "
                    "the localization confidence gate. Manual review required."
                )
                sev = SeverityAssessment(
                    score=None,
                    level=DamageSeverityLevel.UNAVAILABLE,
                    method="relative_area_weighted_by_class",
                    calibrated=False,
                    affected_pixel_area_total=None,
                    vehicle_pixel_area=float(transforms.original_width * transforms.original_height),
                    relative_damage_ratio=None,
                )
            elif model_missing:
                assessment = AssessmentStatus.INCONCLUSIVE
                reason = "Damage detector unavailable; unable to assess damage. Manual review required."
                sev = SeverityAssessment(
                    score=None,
                    level=DamageSeverityLevel.UNAVAILABLE,
                    method="relative_area_weighted_by_class",
                    calibrated=False,
                    affected_pixel_area_total=None,
                    vehicle_pixel_area=float(transforms.original_width * transforms.original_height),
                    relative_damage_ratio=None,
                )
            else:
                assessment = AssessmentStatus.NO_DAMAGE
                reason = "Model completed inference with no damage above threshold."
                sev = SeverityAssessment(
                    score=0.0,
                    level=DamageSeverityLevel.LOW,
                    method="relative_area_weighted_by_class",
                    calibrated=False,
                    affected_pixel_area_total=0.0,
                    vehicle_pixel_area=float(transforms.original_width * transforms.original_height),
                    relative_damage_ratio=0.0,
                )
            return ImageFinding(
                image_id=img_id,
                filename=filename,
                damage_detected=False,
                assessment=assessment,
                assessment_reason=reason,
                damage_probability=prob,
                filter_threshold=self.stage1_filter.threshold,
                filter_model=self.stage1_filter.model_name,
                classifications=[],
                detections=[],
                severity=sev,
                stage_status=stage_status,
                transforms=transforms,
                warnings=[] if assessment == AssessmentStatus.NO_DAMAGE else [reason],
                latency_ms=latencies,
            )

        # 5. Stage 4: Damage Segmentation
        segmented_detections, s4_status, s4_latency = self.stage4_segmenter.segment_instances(
            raw_detections, transforms
        )
        stage_status["segmentation"] = s4_status
        latencies["stage4_segmentation"] = s4_latency

        # 5b. Prioritization: rank primary-first (major collision before minor
        # defects) and stamp component/priority/score. Same ordered list feeds
        # severity, classifications, overlay, chips, and PDF report so every
        # surface agrees on what the primary damage is.
        from ml.vision.prioritization import prioritize_detections

        t_prio = time.perf_counter()
        rear_view = self._detect_rear_view(image, segmented_detections)
        segmented_detections = prioritize_detections(
            segmented_detections,
            image_width=transforms.original_width,
            image_height=transforms.original_height,
            rear_view=rear_view,
        )
        latencies["prioritization"] = round((time.perf_counter() - t_prio) * 1000.0, 2)

        # 6. Severity Assessment
        t_sev = time.perf_counter()
        severity = calculate_severity(
            detections=segmented_detections,
            image_width=transforms.original_width,
            image_height=transforms.original_height,
        )
        stage_status["severity"] = StageStatus.COMPLETED if segmented_detections else StageStatus.SKIPPED_INTACT
        latencies["severity_calc"] = round((time.perf_counter() - t_sev) * 1000.0, 2)

        has_damage = bool(segmented_detections)
        if has_damage:
            img_assessment = AssessmentStatus.DAMAGED
            img_reason = None
            img_warnings: list[str] = []
        else:
            img_assessment = AssessmentStatus.INCONCLUSIVE
            img_reason = "Segmentation produced no measurable regions. Manual review required."
            img_warnings = [img_reason]
        # Consistency contract: classification chips shown in the UI/PDF must
        # describe exactly the detections drawn on the overlay (same labels,
        # same confidences). Stage 2 still runs as a real inference stage —
        # its status is reported — but the exposed classes are derived from
        # the final post-gate detections so boxes and chips cannot disagree.
        if has_damage:
            # Order classes by priority (first appearance in the prioritized
            # detection list), not by raw confidence, so chips/report lead
            # with the primary damage class.
            best_by_label: dict[str, float] = {}
            label_order: list[str] = []
            for det in segmented_detections:
                if det.label not in best_by_label:
                    label_order.append(det.label)
                    best_by_label[det.label] = det.confidence
                elif det.confidence > best_by_label[det.label]:
                    best_by_label[det.label] = det.confidence
            classes = [
                ClassificationItem(label=label, confidence=round(best_by_label[label], 4))
                for label in label_order
            ]
        return ImageFinding(
            image_id=img_id,
            filename=filename,
            damage_detected=has_damage,
            assessment=img_assessment,
            assessment_reason=img_reason,
            damage_probability=prob,
            filter_threshold=self.stage1_filter.threshold,
            filter_model=self.stage1_filter.model_name,
            classifications=classes if has_damage else [],
            detections=segmented_detections,
            severity=severity if has_damage else SeverityAssessment(
                score=None,
                level=DamageSeverityLevel.UNAVAILABLE,
                method="relative_area_weighted_by_class",
                calibrated=False,
                affected_pixel_area_total=None,
                vehicle_pixel_area=float(transforms.original_width * transforms.original_height),
                relative_damage_ratio=None,
            ),
            stage_status=stage_status,
            transforms=transforms,
            warnings=img_warnings,
            latency_ms=latencies,
        )

    @staticmethod
    def _detect_rear_view(image: Image.Image, detections) -> bool:
        """Evidence-based viewpoint check: substantial red taillight reflector => rear view.

        Taillights have saturated red reflectors ((hue <= 8 | hue >= 172) & sat >= 80 & val >= 60).
        A genuine taillight cluster contains a concentrated red mass (>= 300 connected red pixels).
        Frontal collisions (which have negligible or zero red pixels) are never flagged as rear.
        """
        try:
            import cv2
            import numpy as np

            arr = np.asarray(image.convert("RGB"), dtype=np.uint8)
            hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)
            h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
            red = ((h <= 8) | (h >= 172)) & (s >= 80) & (v >= 60)
            if int(red.sum()) < 350:
                return False

            # Check if there is a concentrated red cluster representing a taillight
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(red.astype(np.uint8))
            for i in range(1, num_labels):
                area = stats[i, cv2.CC_STAT_AREA]
                if area >= 300:
                    return True
            return False
        except Exception:
            return False

    @staticmethod
    def _content_hash(image_input: Union[bytes, str, Path, Image.Image]) -> Optional[str]:
        """Stable content hash for duplicate-selection detection (None if unknown)."""
        try:
            if isinstance(image_input, bytes):
                return hashlib.sha256(image_input).hexdigest()
            if isinstance(image_input, (str, Path)):
                return hashlib.sha256(Path(image_input).read_bytes()).hexdigest()
            if isinstance(image_input, Image.Image):
                return hashlib.sha256(image_input.convert("RGB").tobytes()).hexdigest()
        except Exception:  # pragma: no cover - unreadable source
            return None
        return None

    @staticmethod
    def _failed_finding(
        filename: str,
        reason: str,
        img_id: Optional[str] = None,
    ) -> ImageFinding:
        """Build an INCONCLUSIVE finding for an image that could not be decoded/analyzed.

        Never fabricates a NO_DAMAGE verdict; the exception detail stays in logs
        while the user-facing reason is a fixed, deduplicable sentence.
        """
        return ImageFinding(
            image_id=img_id or f"img_{uuid.uuid4().hex[:8]}",
            filename=filename,
            damage_detected=False,
            assessment=AssessmentStatus.INCONCLUSIVE,
            assessment_reason=reason,
            damage_probability=None,
            classifications=[],
            detections=[],
            severity=SeverityAssessment(
                score=None,
                level=DamageSeverityLevel.UNAVAILABLE,
                method="relative_area_weighted_by_class",
                calibrated=False,
                affected_pixel_area_total=None,
                vehicle_pixel_area=None,
                relative_damage_ratio=None,
            ),
            stage_status={
                "filter": StageStatus.FAILED,
                "classification": StageStatus.NOT_RUN,
                "detection": StageStatus.NOT_RUN,
                "segmentation": StageStatus.NOT_RUN,
                "severity": StageStatus.NOT_RUN,
            },
            transforms=None,
            warnings=[reason],
            latency_ms={},
        )

    def process_inspection(
        self,
        images: List[Union[bytes, str, Path, Image.Image]],
        filenames: Optional[List[str]] = None,
        inspection_id: Optional[str] = None,
    ) -> VisionPipelineResult:
        """Execute vision pipeline across all uploaded inspection images and aggregate findings."""
        start_time = time.perf_counter()
        insp_id = inspection_id or f"insp_{uuid.uuid4().hex[:8]}"
        names = filenames or [f"image_{i+1}.jpg" for i in range(len(images))]

        findings: List[ImageFinding] = []
        seen_content_hashes: set[str] = set()
        duplicate_images_skipped = 0
        any_damage = False
        any_inconclusive = False
        inconclusive_reasons: list[str] = []
        all_classes: set[str] = set()
        total_instances = 0
        max_severity_score: float | None = None
        worst_level = DamageSeverityLevel.UNAVAILABLE
        any_early_filter_skip = False

        for img_input, name in zip(images, names):
            # Content-level dedup: the same bytes/PIL image selected twice
            # must be analyzed once (repeat selection is not new evidence).
            # Content-level dedup: the same bytes/PIL image selected twice
            # must be analyzed once (repeat selection is not new evidence).
            content_key = self._content_hash(img_input)
            if content_key is not None:
                if content_key in seen_content_hashes:
                    duplicate_images_skipped += 1
                    continue
                seen_content_hashes.add(content_key)

            try:
                finding = self.process_image(img_input, filename=name)
            except Exception as exc:
                # Detail goes to logs only; user-facing reason is fixed text.
                logger.warning("Image %r could not be analyzed: %s", name, exc)
                finding = self._failed_finding(
                    filename=name,
                    reason=(
                        "Image could not be decoded or analyzed; "
                        "manual review required."
                    ),
                )
            findings.append(finding)

            if finding.assessment == AssessmentStatus.DAMAGED:
                any_damage = True
                for c in finding.classifications:
                    all_classes.add(c.label)
                for d in finding.detections:
                    all_classes.add(d.label)
                    total_instances += 1
                if finding.severity.score is not None and (
                        max_severity_score is None or finding.severity.score > max_severity_score):
                    max_severity_score = finding.severity.score
                    worst_level = finding.severity.level
            elif finding.assessment == AssessmentStatus.INCONCLUSIVE:
                any_inconclusive = True
                # Collect reason texts (not filename-prefixed) and de-duplicate.
                # Previously the reason AND identical warning were both appended
                # under filename prefixes, doubling every message in the report.
                for text in [finding.assessment_reason, *finding.warnings]:
                    if text and text not in inconclusive_reasons:
                        inconclusive_reasons.append(text)
            else:
                any_early_filter_skip = True

        total_latency = (time.perf_counter() - start_time) * 1000.0

        if any_damage:
            overall_assessment = AssessmentStatus.DAMAGED
            overall_reason = None
            overall_severity = SeverityAssessment(
                score=round(max_severity_score or 0.0, 4),
                level=worst_level,
                method="aggregated_worst_image_severity",
                calibrated=False,
                relative_damage_ratio=round(max_severity_score or 0.0, 4),
            )
        elif any_inconclusive:
            overall_assessment = AssessmentStatus.INCONCLUSIVE
            overall_reason = "; ".join(inconclusive_reasons) or "Unable to determine; manual review required."
            overall_severity = SeverityAssessment(
                score=None,
                level=DamageSeverityLevel.UNAVAILABLE,
                method="aggregated_worst_image_severity",
                calibrated=False,
                relative_damage_ratio=None,
            )
        else:
            overall_assessment = AssessmentStatus.NO_DAMAGE
            overall_reason = "Model completed inference with no damage above threshold."
            overall_severity = SeverityAssessment(
                score=0.0,
                level=DamageSeverityLevel.LOW,
                method="aggregated_worst_image_severity",
                calibrated=False,
                relative_damage_ratio=0.0,
            )

        return VisionPipelineResult(
            inspection_id=insp_id,
            overall_damage_detected=any_damage,
            overall_assessment=overall_assessment,
            overall_reason=overall_reason,
            overall_severity=overall_severity,
            primary_damage_classes=sorted(list(all_classes)),
            total_damage_instances=total_instances,
            images=findings,
            compute_saved_by_early_filter=any_early_filter_skip,
            total_latency_ms=round(total_latency, 2),
            pipeline_version="1.0.0",
            warnings=list(
                dict.fromkeys(
                    [
                        *(inconclusive_reasons if any_inconclusive and not any_damage else []),
                        *(
                            [f"Skipped {duplicate_images_skipped} duplicate image upload(s)."]
                            if duplicate_images_skipped
                            else []
                        ),
                    ]
                )
            ),

        )
