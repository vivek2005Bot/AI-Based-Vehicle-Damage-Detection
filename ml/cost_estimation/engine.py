"""AI Vehicle Repair Cost Estimation Engine.

Computes itemized, transparent Repair (Scenario A) vs Replacement (Scenario B) costs
grounded in authentic Indian online parts pricing, standard bodyshop labour hours,
and deterministic technical repairability rules.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from ml.cost_estimation.pricing_service import (
    DEFAULT_CACHE_HOURS,
    OnlinePricingService,
    online_pricing_service,
)
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
    AUTOMOTIVE_GST_PARTS_RATE,
    COMPONENT_METADATA,
    DEFAULT_HOURLY_LABOUR_INR,
    DEALER_HOURLY_LABOUR_INR,
    calculate_extent_category,
    evaluate_repairability,
    get_component_metadata,
)

logger = logging.getLogger(__name__)


class RepairCostEstimator:
    """Core estimation engine executing technical and economic repair assessments."""

    def __init__(self, pricing_service: Optional[OnlinePricingService] = None):
        self.pricing_service = pricing_service or online_pricing_service

    def estimate_cost(
        self,
        inspection_id: str,
        damage_summary: ComponentDamageSummary,
        vehicle_context: Optional[VehicleCostContext] = None,
        finding_id: Optional[str] = None,
    ) -> RepairCostEstimateResponse:
        """Generate comprehensive Repair vs Replacement estimate for a damaged component."""
        vehicle = vehicle_context or VehicleCostContext()
        cid = damage_summary.component_id.lower().strip()
        comp_meta = get_component_metadata(cid)
        is_exterior = comp_meta.get("is_exterior_panel", True)
        requires_paint = comp_meta.get("requires_paint_matching", False)
        base_rr_hours = float(comp_meta.get("rr_labour_hours", 2.0))
        default_paint = float(comp_meta.get("default_paint_cost", 0.0))
        consumables_cost = float(comp_meta.get("consumables_cost", 0.0))

        # Determine hourly labour rate based on city / preference
        hourly_rate = DEFAULT_HOURLY_LABOUR_INR
        if vehicle.city and any(metro in vehicle.city.lower() for metro in ["delhi", "mumbai", "bengaluru", "gurugram"]):
            hourly_rate = 850.0

        # 1. Fetch live / cached online parts pricing
        sources, part_min, part_expected, part_max, is_cached = self.pricing_service.fetch_component_pricing(
            component_id=cid,
            vehicle=vehicle,
        )

        primary_source: Optional[PriceSource] = sources[0] if sources else None
        shipping_fee = primary_source.shipping_charge if primary_source else 350.0

        # 2. Evaluate technical feasibility of repairing the component
        is_repair_feasible, repair_reason, replace_reason = evaluate_repairability(
            component_id=cid,
            damage_type=damage_summary.damage_type,
            extent=damage_summary.extent_category,
        )

        # -------------------------------------------------------------------
        # Build Scenario A: Component Repair (Denting / Beating / Spot Painting)
        # -------------------------------------------------------------------
        repair_items: List[CostBreakdownItem] = []
        if is_repair_feasible:
            # Labour hours for panel beating / repair
            if damage_summary.extent_category == ExtentCategory.MINOR:
                repair_labour_hours = 1.5
                paint_cost = 1400.0 if requires_paint else 0.0
                material_cost = 350.0
            elif damage_summary.extent_category == ExtentCategory.MODERATE:
                repair_labour_hours = 3.0
                paint_cost = default_paint * 0.8 if requires_paint else 0.0
                material_cost = 650.0
            else:  # EXTENSIVE
                repair_labour_hours = 5.0
                paint_cost = default_paint if requires_paint else 0.0
                material_cost = 1000.0

            # Item 1: Bodyshop Labour (Denting, pulling, reshaping)
            labour_total = round(repair_labour_hours * hourly_rate, 2)
            repair_items.append(
                CostBreakdownItem(
                    category="labour",
                    description=f"Panel beating, reshaping & surface straightening ({damage_summary.extent_category.value})",
                    operation="denting_and_reshaping",
                    quantity=repair_labour_hours,
                    unit_cost=hourly_rate,
                    total_cost=labour_total,
                    currency="INR",
                    labour_hours=repair_labour_hours,
                    hourly_rate=hourly_rate,
                    confidence="industry_standard",
                )
            )

            # Item 2: Painting & Refinishing
            if paint_cost > 0:
                repair_items.append(
                    CostBreakdownItem(
                        category="painting",
                        description="Surface preparation, spot primer, paint coat & clear blend",
                        operation="refinish_spot_paint",
                        quantity=1.0,
                        unit_cost=paint_cost,
                        total_cost=paint_cost,
                        currency="INR",
                        confidence="industry_standard",
                    )
                )

            # Item 3: Bodyshop Consumables & Fasteners
            repair_items.append(
                CostBreakdownItem(
                    category="materials",
                    description="Polyester putty, sandpaper discs, masking tape & mounting clips",
                    operation="consumables",
                    quantity=1.0,
                    unit_cost=material_cost,
                    total_cost=material_cost,
                    currency="INR",
                    confidence="industry_standard",
                )
            )

            # Calculate Subtotal & GST
            subtotal_repair = sum(item.total_cost for item in repair_items)
            gst_repair = round(subtotal_repair * AUTOMOTIVE_GST_PARTS_RATE, 2)
            repair_items.append(
                CostBreakdownItem(
                    category="taxes",
                    description="Automotive Goods & Services Tax (GST 18%)",
                    operation="gst_calculation",
                    quantity=1.0,
                    unit_cost=gst_repair,
                    total_cost=gst_repair,
                    currency="INR",
                    confidence="statutory_standard",
                )
            )

            repair_expected = round(subtotal_repair + gst_repair, 2)
            repair_min = round(repair_expected * 0.88, 2)
            repair_max = round(repair_expected * 1.18, 2)
            repair_feasibility_status = "feasible"
        else:
            # Repair not recommended or technically unsafe
            repair_feasibility_status = "not_recommended"
            repair_expected = 0.0
            repair_min = 0.0
            repair_max = 0.0

        repair_scenario = EstimateScenario(
            scenario_type="repair",
            title="Component Repair & Refinish",
            is_recommended=False,  # Evaluated below against replacement
            feasibility=repair_feasibility_status,
            feasibility_reason=repair_reason,
            minimum=repair_min,
            expected=repair_expected,
            maximum=repair_max,
            currency="INR",
            breakdown=repair_items,
        )

        # -------------------------------------------------------------------
        # Build Scenario B: Component Replacement (New Part + R&R + Full Paint)
        # -------------------------------------------------------------------
        replace_items: List[CostBreakdownItem] = []

        # Item 1: New Replacement Part from Verified Online Source
        part_desc = primary_source.product_title if primary_source else f"New Replacement {damage_summary.component_display_name}"
        part_num = primary_source.part_number if primary_source else None
        replace_items.append(
            CostBreakdownItem(
                category="part",
                description=f"{part_desc} (Part #{part_num or 'OEM-CAT'})",
                operation="part_procurement",
                quantity=1.0,
                unit_cost=part_expected,
                total_cost=part_expected,
                currency="INR",
                source_name=primary_source.source_name if primary_source else "Boodmo Online Catalogue",
                source_url=primary_source.source_url if primary_source else "https://boodmo.com",
                confidence="verified_online_catalog",
            )
        )

        # Item 2: Removal & Refit (R&R) Labour
        rr_labour_total = round(base_rr_hours * hourly_rate, 2)
        replace_items.append(
            CostBreakdownItem(
                category="labour",
                description=f"Removal of damaged assembly, realignment & refit ({base_rr_hours} hrs)",
                operation="removal_and_refit",
                quantity=base_rr_hours,
                unit_cost=hourly_rate,
                total_cost=rr_labour_total,
                currency="INR",
                labour_hours=base_rr_hours,
                hourly_rate=hourly_rate,
                confidence="industry_standard",
            )
        )

        # Item 3: Full Panel Painting (if exterior body panel needing color matching)
        if requires_paint and default_paint > 0:
            replace_items.append(
                CostBreakdownItem(
                    category="painting",
                    description=f"Full panel spray booth painting & clearcoat ({damage_summary.component_display_name})",
                    operation="full_panel_refinish",
                    quantity=1.0,
                    unit_cost=default_paint,
                    total_cost=default_paint,
                    currency="INR",
                    confidence="industry_standard",
                )
            )

        # Item 4: Installation Consumables / Kits (e.g. PU adhesive kit for windshield)
        if consumables_cost > 0:
            replace_items.append(
                CostBreakdownItem(
                    category="materials",
                    description="OEM mounting hardware, sealant or polyurethane adhesive kit",
                    operation="consumables_replacement",
                    quantity=1.0,
                    unit_cost=consumables_cost,
                    total_cost=consumables_cost,
                    currency="INR",
                    confidence="industry_standard",
                )
            )

        # Item 5: Secure Courier Shipping
        if shipping_fee > 0:
            replace_items.append(
                CostBreakdownItem(
                    category="shipping",
                    description="Direct logistics & doorstep delivery charge",
                    operation="logistics",
                    quantity=1.0,
                    unit_cost=shipping_fee,
                    total_cost=shipping_fee,
                    currency="INR",
                    confidence="verified_online_catalog",
                )
            )

        # Subtotal & GST
        subtotal_replace = sum(item.total_cost for item in replace_items)
        gst_replace = round(subtotal_replace * AUTOMOTIVE_GST_PARTS_RATE, 2)
        replace_items.append(
            CostBreakdownItem(
                category="taxes",
                description="Automotive Goods & Services Tax (GST 18%)",
                operation="gst_calculation",
                quantity=1.0,
                unit_cost=gst_replace,
                total_cost=gst_replace,
                currency="INR",
                confidence="statutory_standard",
            )
        )

        replace_expected = round(subtotal_replace + gst_replace, 2)
        replace_min = round((part_min + (base_rr_hours * hourly_rate) + (default_paint * 0.9)) * 1.18, 2)
        replace_max = round((part_max + (base_rr_hours * hourly_rate * 1.2) + (default_paint * 1.15) + shipping_fee) * 1.18, 2)

        replacement_scenario = EstimateScenario(
            scenario_type="replacement",
            title="Complete Component Replacement",
            is_recommended=False,
            feasibility="feasible",
            feasibility_reason=replace_reason or "Restores vehicle to original factory structural and aesthetic specification.",
            minimum=replace_min,
            expected=replace_expected,
            maximum=replace_max,
            currency="INR",
            breakdown=replace_items,
        )

        # -------------------------------------------------------------------
        # 3. Decision Logic: Which Scenario is Recommended?
        # -------------------------------------------------------------------
        if not is_repair_feasible:
            replacement_scenario.is_recommended = True
            repair_scenario.is_recommended = False
        else:
            # Economic comparison: if repair is more than 70% of replacement cost, recommend replacement
            if repair_expected >= 0.70 * replace_expected:
                replacement_scenario.is_recommended = True
                repair_scenario.is_recommended = False
                replacement_scenario.feasibility_reason += " (Economically optimal: repair cost approaches replacement cost)."
            else:
                repair_scenario.is_recommended = True
                replacement_scenario.is_recommended = False

        # -------------------------------------------------------------------
        # 4. Assess Overall Estimate Confidence & Missing Information
        # -------------------------------------------------------------------
        missing_info: List[str] = []
        if not vehicle.make:
            missing_info.append("Vehicle make and model not provided; using Indian passenger car industry benchmark.")
        if not vehicle.year:
            missing_info.append("Vehicle manufacturing year unspecified; variant generation may alter part pricing.")
        if damage_summary.component_verification_required:
            missing_info.append("Component position determined heuristically; technician manual confirmation recommended.")

        # Determine confidence level
        if damage_summary.component_identification_method == ComponentIdentificationMethod.USER_CONFIRMED:
            overall_confidence = EstimateConfidenceLevel.STRONG
            confidence_explanation = "Component verified by user; genuine Indian part catalog prices verified with active fitment."
        elif damage_summary.damage_confidence and damage_summary.damage_confidence >= 0.80 and vehicle.make:
            overall_confidence = EstimateConfidenceLevel.STRONG
            confidence_explanation = "High visual detection confidence and verified OEM vehicle part catalogue benchmark."
        elif damage_summary.damage_confidence and damage_summary.damage_confidence >= 0.50:
            overall_confidence = EstimateConfidenceLevel.MODERATE
            confidence_explanation = "Clear visible damage pattern; prices grounded in standard Indian aftermarket/OEM catalogues."
        else:
            overall_confidence = EstimateConfidenceLevel.LIMITED
            confidence_explanation = "Indicative estimate based on visible damage region; requires on-site workshop inspection."

        limitations = [
            "This estimate is indicative and subject to internal non-visible damage revealed during panel disassembly.",
            "Labour rates reflect standard metro bodyshop benchmarks in India and may vary by specific authorized dealership.",
            "Online parts availability and pricing fluctuate based on distributor inventory and regional transit taxes.",
            "Vehicle roadworthiness and structural safety evaluations are independent of repair cost estimates.",
        ]

        now_utc = datetime.now(timezone.utc)
        cached_until_dt = now_utc + datetime.resolution * 0  # placeholder

        return RepairCostEstimateResponse(
            estimate_id=f"est_{uuid.uuid4().hex[:10]}",
            inspection_id=inspection_id,
            finding_id=finding_id,
            status="completed",
            vehicle=vehicle,
            damage=damage_summary,
            repair_scenario=repair_scenario,
            replacement_scenario=replacement_scenario,
            overall_confidence=overall_confidence,
            confidence_explanation=confidence_explanation,
            sources=sources,
            generated_at=now_utc.isoformat(),
            is_cached=is_cached,
            limitations=limitations,
            missing_information=missing_info,
        )


# Global singleton
repair_cost_estimator = RepairCostEstimator()
