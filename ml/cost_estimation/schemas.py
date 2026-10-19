"""Typed Pydantic Schemas for AI Vehicle Repair Cost Estimation.

Complies with the Implementation Specification:
- Segregates damage classification confidence from component identity confidence.
- Provides separate, independent Repair vs Replacement scenarios.
- Tracks genuine online price provenance, currency, timestamps, and confidence.
- Distinguishes damage extent ratio from arbitrary bounding-box approximations.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ComponentCategory(str, Enum):
    FRONT_BUMPER = "front_bumper"
    REAR_BUMPER = "rear_bumper"
    FRONT_GRILLE = "front_grille"
    HEADLIGHT = "headlight"
    TAILLIGHT = "taillight"
    SIDE_MIRROR = "side_mirror"
    WINDSHIELD = "windshield"
    REAR_WINDSHIELD = "rear_windshield"
    SIDE_WINDOW = "side_window"
    DOOR = "door"
    FRONT_FENDER = "front_fender"
    REAR_QUARTER_PANEL = "rear_quarter_panel"
    HOOD = "hood"
    ROOF = "roof"
    TRUNK_TAILGATE = "trunk_tailgate"
    WHEEL_TIRE = "wheel_tire"
    OTHER_PANEL = "other_panel"
    UNKNOWN_COMPONENT = "unknown_component"


class ExtentCategory(str, Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    EXTENSIVE = "extensive"
    UNKNOWN = "unknown"


class ComponentIdentificationMethod(str, Enum):
    POSITIONAL_HEURISTIC = "positional_heuristic"
    MODEL_INFERENCE = "model_inference"
    USER_CONFIRMED = "user_confirmed"
    DEFAULT_FALLBACK = "default_fallback"


class EstimateConfidenceLevel(str, Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    LIMITED = "limited"
    INSUFFICIENT = "insufficient"


class PartTier(str, Enum):
    OEM = "oem"
    AFTERMARKET = "aftermarket"
    USED = "used"
    UNKNOWN = "unknown"


class ComponentDamageSummary(BaseModel):
    """Assessment of the affected vehicle component and extent of visible damage."""
    component_id: str
    component_display_name: str
    component_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    damage_type: str
    damage_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    component_identification_method: ComponentIdentificationMethod = ComponentIdentificationMethod.POSITIONAL_HEURISTIC
    component_verification_required: bool = False
    extent_category: ExtentCategory = ExtentCategory.UNKNOWN
    damage_area_pixels: Optional[float] = None
    component_area_pixels: Optional[float] = None
    damage_area_ratio: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    measurement_status: str = "indicative_estimate"
    distinct_regions_count: int = 1
    measurement_limitations: List[str] = Field(default_factory=list)


class PriceSource(BaseModel):
    """Provenance tracking for a live online price observation."""
    source_id: str
    source_name: str
    product_title: str
    source_url: str
    advertised_price: float = Field(..., ge=0.0)
    currency: str = "INR"
    retrieved_at: str
    part_number: Optional[str] = None
    part_tier: PartTier = PartTier.OEM
    shipping_charge: Optional[float] = 0.0
    taxes_included: bool = True
    in_stock: Optional[bool] = True
    reliability_rating: str = "high"
    notes: Optional[str] = None


class CostBreakdownItem(BaseModel):
    """Single itemized operational or material cost item."""
    category: str = Field(..., description="part | labour | painting | materials | taxes | shipping | other")
    description: str
    operation: Optional[str] = None
    quantity: float = 1.0
    unit_cost: float = Field(..., ge=0.0)
    total_cost: float = Field(..., ge=0.0)
    currency: str = "INR"
    labour_hours: Optional[float] = None
    hourly_rate: Optional[float] = None
    is_tax_inclusive: bool = True
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    confidence: str = "industry_standard"


class EstimateScenario(BaseModel):
    """Cost estimate for a specific action path (Repair vs Replacement)."""
    scenario_type: str = Field(..., description="repair | replacement")
    title: str
    is_recommended: bool = False
    feasibility: str = Field(default="feasible", description="feasible | not_recommended | mandatory_replacement | unknown")
    feasibility_reason: str = ""
    minimum: float = Field(..., ge=0.0)
    expected: float = Field(..., ge=0.0)
    maximum: float = Field(..., ge=0.0)
    currency: str = "INR"
    breakdown: List[CostBreakdownItem] = Field(default_factory=list)


class VehicleCostContext(BaseModel):
    """Vehicle identification and geographical context for pricing."""
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    variant: Optional[str] = None
    city: Optional[str] = "Delhi NCR"
    postal_code: Optional[str] = None
    currency: str = "INR"
    oem_preference: PartTier = PartTier.OEM


class RepairCostEstimateResponse(BaseModel):
    """Complete structured repair cost assessment payload."""
    estimate_id: str
    inspection_id: str
    finding_id: Optional[str] = None
    status: str = "completed"
    vehicle: VehicleCostContext
    damage: ComponentDamageSummary
    repair_scenario: EstimateScenario
    replacement_scenario: EstimateScenario
    overall_confidence: EstimateConfidenceLevel = EstimateConfidenceLevel.MODERATE
    confidence_explanation: str = ""
    sources: List[PriceSource] = Field(default_factory=list)
    generated_at: str
    cached_until: Optional[str] = None
    is_cached: bool = False
    cache_retrieval_date: Optional[str] = None
    limitations: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
