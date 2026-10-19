"""Automated Unit & Integration Tests for AI Vehicle Repair Cost Estimation.

Verifies:
1. Pydantic schemas & segregation of damage vs component confidence.
2. Technical repairability evaluation (windshield safety, headlight housing, panel beating).
3. Online pricing service (Boodmo/PartsBigBoss Indian catalogue benchmarks, caching TTL).
4. Estimation engine itemized calculations (Parts, Labour hours, Painting, GST 18%, Shipping).
5. Economic vs technical recommendation logic (Repair vs Replacement).
6. Localized PDF inspection report rendering with Section 4.
"""

from __future__ import annotations

import json
import pytest
from reports.pdf_renderer import render_inspection_pdf
from ml.cost_estimation.schemas import (
    ComponentCategory,
    ComponentDamageSummary,
    ComponentIdentificationMethod,
    EstimateConfidenceLevel,
    ExtentCategory,
    PartTier,
    RepairCostEstimateResponse,
    VehicleCostContext,
)
from ml.cost_estimation.taxonomy import (
    AUTOMOTIVE_GST_PARTS_RATE,
    DEFAULT_HOURLY_LABOUR_INR,
    calculate_extent_category,
    evaluate_repairability,
    get_component_metadata,
)
from ml.cost_estimation.pricing_service import OnlinePricingService, online_pricing_service
from ml.cost_estimation.engine import RepairCostEstimator, repair_cost_estimator


def test_schemas_confidence_segregation():
    """Verify component confidence and damage confidence are tracked independently."""
    summary = ComponentDamageSummary(
        component_id="front_bumper",
        component_display_name="Front Bumper Cover",
        component_confidence=0.72,  # Positional heuristic confidence
        damage_type="scratch",
        damage_confidence=0.94,     # Vision classifier confidence
        extent_category=ExtentCategory.MINOR,
        component_identification_method=ComponentIdentificationMethod.POSITIONAL_HEURISTIC,
    )
    assert summary.component_confidence == 0.72
    assert summary.damage_confidence == 0.94
    assert summary.component_confidence != summary.damage_confidence


def test_taxonomy_extent_calculation():
    """Verify extent categorization from relative area and distinct count."""
    cat1, desc1 = calculate_extent_category("scratch", relative_area=0.02, distinct_count=1)
    assert cat1 == ExtentCategory.MINOR

    cat2, desc2 = calculate_extent_category("dent", relative_area=0.08, distinct_count=1)
    assert cat2 == ExtentCategory.MODERATE

    cat3, desc3 = calculate_extent_category("bumper_smash", relative_area=0.18, distinct_count=2)
    assert cat3 == ExtentCategory.EXTENSIVE


def test_repairability_safety_rules():
    """Verify deterministic technical repairability rules."""
    # 1. Minor cosmetic scratch on bumper -> Repair is feasible
    is_rep, rep_reason, repl_reason = evaluate_repairability("front_bumper", "scratch", ExtentCategory.MINOR)
    assert is_rep is True

    # 2. Broken polycarbonate headlamp -> Replacement mandatory (cannot plastic weld sealed lens)
    is_rep_hl, rep_reason_hl, _ = evaluate_repairability("headlight", "broken_light", ExtentCategory.MODERATE)
    assert is_rep_hl is False
    assert "moisture ingress" in rep_reason_hl.lower() or "lens" in rep_reason_hl.lower()

    # 3. Moderate/Extensive windshield crack -> Replacement mandatory under safety norms
    is_rep_ws, rep_reason_ws, _ = evaluate_repairability("windshield", "glass_crack", ExtentCategory.MODERATE)
    assert is_rep_ws is False
    assert "50mm" in rep_reason_ws or "ais" in rep_reason_ws.lower()


def test_pricing_service_maruti_benchmarks():
    """Verify online pricing service returns genuine Indian market sources & part numbers."""
    service = OnlinePricingService(cache_ttl_hours=24)
    v_ctx = VehicleCostContext(make="Maruti Suzuki", model="Swift", year=2022)

    sources, p_min, p_exp, p_max, is_cached = service.fetch_component_pricing("front_bumper", v_ctx)

    assert len(sources) >= 2
    boodmo_src = next((s for s in sources if s.source_id == "boodmo_oem"), None)
    assert boodmo_src is not None
    assert boodmo_src.currency == "INR"
    assert boodmo_src.advertised_price > 0
    assert "boodmo.com" in boodmo_src.source_url
    assert boodmo_src.part_number == "71711M66R00-5PK"
    assert p_min <= p_exp <= p_max

    # Second call should be retrieved from cache
    _, _, _, _, is_cached_2 = service.fetch_component_pricing("front_bumper", v_ctx)
    assert is_cached_2 is True


def test_engine_repair_vs_replace_calculations():
    """Verify estimation engine computes Scenario A and Scenario B with GST 18%."""
    estimator = RepairCostEstimator()
    v_ctx = VehicleCostContext(make="Hyundai", model="Creta", year=2021)
    damage_summary = ComponentDamageSummary(
        component_id="front_bumper",
        component_display_name="Front Bumper Cover",
        component_confidence=0.88,
        damage_type="scratch",
        damage_confidence=0.91,
        extent_category=ExtentCategory.MINOR,
        component_identification_method=ComponentIdentificationMethod.USER_CONFIRMED,
    )

    resp = estimator.estimate_cost(
        inspection_id="test_insp_001",
        damage_summary=damage_summary,
        vehicle_context=v_ctx,
    )

    assert resp.status == "completed"
    assert resp.overall_confidence == EstimateConfidenceLevel.STRONG
    assert resp.repair_scenario.expected > 0
    assert resp.replacement_scenario.expected > 0

    # Minor scratch on bumper should economically recommend repair
    assert resp.repair_scenario.is_recommended is True
    assert resp.replacement_scenario.is_recommended is False

    # Check GST 18% calculation in breakdown
    gst_item = next((i for i in resp.repair_scenario.breakdown if i.category == "taxes"), None)
    assert gst_item is not None
    assert "18%" in gst_item.description


def test_engine_mandatory_replacement_recommendation():
    """Verify broken headlight mandates replacement as recommended scenario."""
    estimator = RepairCostEstimator()
    v_ctx = VehicleCostContext(make="Tata", model="Nexon", year=2023)
    damage_summary = ComponentDamageSummary(
        component_id="headlight",
        component_display_name="Headlight Assembly",
        component_confidence=0.95,
        damage_type="broken_light",
        damage_confidence=0.93,
        extent_category=ExtentCategory.MODERATE,
    )

    resp = estimator.estimate_cost(
        inspection_id="test_insp_002",
        damage_summary=damage_summary,
        vehicle_context=v_ctx,
    )

    assert resp.repair_scenario.is_recommended is False
    assert resp.repair_scenario.feasibility == "not_recommended"
    assert resp.replacement_scenario.is_recommended is True


def test_pdf_rendering_with_cost_estimate():
    """Verify Section 4 (Vehicle Repair & Replacement Cost Estimate) renders into PDF."""
    mock_report = {
        "inspection_id": "test_insp_pdf_01",
        "generated_at": "2026-10-19T10:00:00Z",
        "overall": {
            "damage_detected": True,
            "assessment": "damaged",
            "summary": "Vehicle inspection complete.",
            "limitations": [],
        },
        "vehicle": {"make": "Maruti Suzuki", "model": "Swift", "year": 2022},
        "severity": {"score": 0.42, "level": "medium", "method": "calibrated", "calibrated": True},
        "images": [],
        "obd": {"status": "not_provided", "flagged_pids": [], "dtcs": []},
        "risk": {"class": "caution", "summary": "Cosmetic exterior repairs required.", "reason_codes": []},
        "knowledge": {"passages": []},
        "estimate": {
            "estimate_id": "est_test_123",
            "inspection_id": "test_insp_pdf_01",
            "overall_confidence": "strong",
            "vehicle": {"make": "Maruti Suzuki", "model": "Swift", "currency": "INR"},
            "damage": {
                "component_id": "front_bumper",
                "component_display_name": "Front Bumper Cover",
                "extent_category": "minor",
            },
            "repair_scenario": {
                "scenario_type": "repair",
                "title": "Component Repair & Refinish",
                "is_recommended": True,
                "feasibility": "feasible",
                "feasibility_reason": "Economically and structurally feasible.",
                "minimum": 3200.0,
                "expected": 3850.0,
                "maximum": 4600.0,
                "currency": "INR",
                "breakdown": [
                    {
                        "category": "labour",
                        "description": "Panel reshaping & surface straightening (1.5 hrs @ ₹750/hr)",
                        "quantity": 1.5,
                        "unit_cost": 750.0,
                        "total_cost": 1125.0,
                    },
                    {
                        "category": "painting",
                        "description": "Spot primer & refinish paint",
                        "quantity": 1.0,
                        "unit_cost": 1400.0,
                        "total_cost": 1400.0,
                    },
                    {
                        "category": "taxes",
                        "description": "Automotive GST (18%)",
                        "quantity": 1.0,
                        "unit_cost": 500.0,
                        "total_cost": 500.0,
                    },
                ],
            },
            "replacement_scenario": {
                "scenario_type": "replacement",
                "title": "Complete Component Replacement",
                "is_recommended": False,
                "feasibility": "feasible",
                "feasibility_reason": "Full factory replacement.",
                "minimum": 6500.0,
                "expected": 7450.0,
                "maximum": 8900.0,
                "currency": "INR",
                "breakdown": [],
            },
            "sources": [
                {
                    "source_id": "boodmo_oem",
                    "source_name": "Boodmo Automotive",
                    "product_title": "Genuine OEM Maruti Front Bumper Cover",
                    "source_url": "https://boodmo.com/catalog/search/?q=Maruti+Swift+Front+Bumper",
                    "advertised_price": 2450.0,
                    "retrieved_at": "2026-10-19T09:00:00Z",
                    "part_number": "71711M66R00-5PK",
                }
            ],
        },
        "disclaimer": "AI-assisted estimate for guidance only.",
    }

    # Render PDF in English
    pdf_bytes_en = render_inspection_pdf(mock_report, locale="en")
    assert pdf_bytes_en.startswith(b"%PDF")
    assert len(pdf_bytes_en) > 1000

    # Render PDF in Hindi
    pdf_bytes_hi = render_inspection_pdf(mock_report, locale="hi")
    assert pdf_bytes_hi.startswith(b"%PDF")
    assert len(pdf_bytes_hi) > 1000
