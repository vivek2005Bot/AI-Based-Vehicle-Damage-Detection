"""Pydantic schemas for the 4-stage Computer Vision pipeline.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 8.3 & Section 8.4.
Enforces typed output contracts across all vision stages.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class StageStatus(str, Enum):
    COMPLETED = "completed"
    NOT_RUN = "not_run"
    SKIPPED_INTACT = "skipped_intact"
    FAILED = "failed"
    MODEL_UNAVAILABLE = "model_unavailable"


class AssessmentStatus(str, Enum):
    """Tri-state damage outcome. INCONCLUSIVE must never render as NO DAMAGE/SAFE."""
    DAMAGED = "damaged"
    NO_DAMAGE = "no_damage"
    INCONCLUSIVE = "inconclusive"


class DamageSeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNAVAILABLE = "unavailable"


class ClassificationItem(BaseModel):
    label: str = Field(..., description="Canonical damage class name")
    confidence: float = Field(..., ge=0.0, le=1.0)
    source_label: Optional[str] = None


class BoundingBox(BaseModel):
    xmin: float
    ymin: float
    xmax: float
    ymax: float

    @property
    def xyxy(self) -> List[float]:
        return [self.xmin, self.ymin, self.xmax, self.ymax]

    @property
    def width(self) -> float:
        return max(0.0, self.xmax - self.xmin)

    @property
    def height(self) -> float:
        return max(0.0, self.ymax - self.ymin)

    @property
    def area(self) -> float:
        return self.width * self.height


class DetectionItem(BaseModel):
    instance_id: str
    label: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    bbox_xyxy: List[float] = Field(..., description="[xmin, ymin, xmax, ymax] in coordinate_space")
    coordinate_space: str = Field(default="original_image_pixels")
    mask: Optional[List[List[float]]] = Field(default=None, description="Polygon contour points [[x, y], ...]")
    mask_pixel_area: Optional[float] = Field(default=None, ge=0.0)
    relative_area: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    # Prioritization + component (major-collision fix). Optional so older
    # payloads still parse; pipeline always stamps them on new findings.
    # priority: "primary" (most prominent validated damage) | "secondary".
    # component: positional estimate (hood, grille_fascia, front_bumper,
    #   headlight, front_fender, windshield, ...) — advisory, not trained parts.
    component: Optional[str] = Field(default=None)
    priority: str = Field(default="secondary")
    priority_score: Optional[float] = Field(default=None, ge=0.0)


class SeverityAssessment(BaseModel):
    score: Optional[float] = Field(default=None, ge=0.0, description="Weighted composite severity score S")
    level: DamageSeverityLevel = DamageSeverityLevel.UNAVAILABLE
    method: str = "relative_area_weighted_by_class"
    calibrated: bool = False
    affected_pixel_area_total: Optional[float] = None
    vehicle_pixel_area: Optional[float] = None
    relative_damage_ratio: Optional[float] = None
    formula_citation: str = "S = Σ(w_c * r_c)"


class PreprocessingTransformMetadata(BaseModel):
    original_width: int
    original_height: int
    target_width: int
    target_height: int
    scale_factor: float
    pad_left: int
    pad_top: int


class ImageFinding(BaseModel):
    image_id: str
    filename: str
    damage_detected: bool
    assessment: AssessmentStatus = AssessmentStatus.INCONCLUSIVE
    assessment_reason: Optional[str] = None
    damage_probability: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    filter_threshold: float = 0.85
    filter_model: str = "efficientnet_b4"
    classifications: List[ClassificationItem] = Field(default_factory=list)
    detections: List[DetectionItem] = Field(default_factory=list)
    severity: SeverityAssessment = Field(default_factory=SeverityAssessment)
    stage_status: Dict[str, StageStatus] = Field(default_factory=lambda: {
        "filter": StageStatus.NOT_RUN,
        "classification": StageStatus.NOT_RUN,
        "detection": StageStatus.NOT_RUN,
        "segmentation": StageStatus.NOT_RUN,
        "severity": StageStatus.NOT_RUN,
    })
    transforms: Optional[PreprocessingTransformMetadata] = None
    warnings: List[str] = Field(default_factory=list)
    latency_ms: Dict[str, float] = Field(default_factory=dict)


class VisionPipelineResult(BaseModel):
    inspection_id: str
    overall_damage_detected: bool
    overall_assessment: AssessmentStatus = AssessmentStatus.INCONCLUSIVE
    overall_reason: Optional[str] = None
    overall_severity: SeverityAssessment
    primary_damage_classes: List[str] = Field(default_factory=list)
    total_damage_instances: int = 0
    images: List[ImageFinding] = Field(default_factory=list)
    compute_saved_by_early_filter: bool = False
    total_latency_ms: float = 0.0
    pipeline_version: str = "1.0.0"
    warnings: List[str] = Field(default_factory=list)
