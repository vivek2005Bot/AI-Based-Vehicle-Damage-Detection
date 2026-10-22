"""Vehicle Repair Cost Estimation Module."""

from ml.cost_estimation.engine import RepairCostEstimator, repair_cost_estimator
from ml.cost_estimation.pricing_service import OnlinePricingService, online_pricing_service
from ml.cost_estimation.schemas import (
    ComponentCategory,
    ComponentDamageSummary,
    ComponentIdentificationMethod,
    CostBreakdownItem,
    EstimateConfidenceLevel,
    EstimateScenario,
    ExtentCategory,
    PartTier,
    PriceSource,
    RepairCostEstimateResponse,
    VehicleCostContext,
)
from ml.cost_estimation.taxonomy import (
    COMPONENT_METADATA,
    DEFAULT_HOURLY_LABOUR_INR,
    DEALER_HOURLY_LABOUR_INR,
    AUTOMOTIVE_GST_PARTS_RATE,
    calculate_extent_category,
    evaluate_repairability,
    get_component_metadata,
    infer_damage_summary_from_detections,
)

__all__ = [
    "RepairCostEstimator",
    "repair_cost_estimator",
    "OnlinePricingService",
    "online_pricing_service",
    "ComponentCategory",
    "ComponentDamageSummary",
    "ComponentIdentificationMethod",
    "CostBreakdownItem",
    "EstimateConfidenceLevel",
    "EstimateScenario",
    "ExtentCategory",
    "PartTier",
    "PriceSource",
    "RepairCostEstimateResponse",
    "VehicleCostContext",
    "COMPONENT_METADATA",
    "DEFAULT_HOURLY_LABOUR_INR",
    "DEALER_HOURLY_LABOUR_INR",
    "AUTOMOTIVE_GST_PARTS_RATE",
    "calculate_extent_category",
    "evaluate_repairability",
    "get_component_metadata",
    "infer_damage_summary_from_detections",
]
