"""Component Taxonomy, Repairability Logic & Bodyshop Labour Norms.

Provides standardized vehicle component definitions, repair feasibility rules,
and Indian market automotive repair standards (INR) based on industry bodyshop norms.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from ml.cost_estimation.schemas import (
    ComponentCategory,
    ExtentCategory,
)

# ---------------------------------------------------------------------------
# 1. Component Registry & Display Mappings
# ---------------------------------------------------------------------------

COMPONENT_METADATA: Dict[str, Dict[str, Any]] = {
    "front_bumper": {
        "display_name": "Front Bumper Cover",
        "category": ComponentCategory.FRONT_BUMPER,
        "is_exterior_panel": True,
        "requires_paint_matching": True,
        "rr_labour_hours": 2.0,  # Removal & refit
        "default_paint_cost": 3200.0,  # Basecoat + clearcoat + booth
    },
    "rear_bumper": {
        "display_name": "Rear Bumper Cover",
        "category": ComponentCategory.REAR_BUMPER,
        "is_exterior_panel": True,
        "requires_paint_matching": True,
        "rr_labour_hours": 2.0,
        "default_paint_cost": 3200.0,
    },
    "front_grille": {
        "display_name": "Front Grille / Fascia",
        "category": ComponentCategory.FRONT_GRILLE,
        "is_exterior_panel": True,
        "requires_paint_matching": False,  # Often molded composite / chrome
        "rr_labour_hours": 1.2,
        "default_paint_cost": 0.0,
    },
    "grille_fascia": {
        "display_name": "Front Grille & Radiator Fascia",
        "category": ComponentCategory.FRONT_GRILLE,
        "is_exterior_panel": True,
        "requires_paint_matching": False,
        "rr_labour_hours": 1.5,
        "default_paint_cost": 0.0,
    },
    "headlight": {
        "display_name": "Headlight Assembly",
        "category": ComponentCategory.HEADLIGHT,
        "is_exterior_panel": False,
        "requires_paint_matching": False,
        "rr_labour_hours": 1.0,  # Includes beam alignment check
        "default_paint_cost": 0.0,
    },
    "headlight_area": {
        "display_name": "Headlight / Front Corner Assembly",
        "category": ComponentCategory.HEADLIGHT,
        "is_exterior_panel": False,
        "requires_paint_matching": False,
        "rr_labour_hours": 1.2,
        "default_paint_cost": 0.0,
    },
    "taillight": {
        "display_name": "Taillight Assembly",
        "category": ComponentCategory.TAILLIGHT,
        "is_exterior_panel": False,
        "requires_paint_matching": False,
        "rr_labour_hours": 0.8,
        "default_paint_cost": 0.0,
    },
    "side_mirror": {
        "display_name": "Outside Rear-View Mirror (ORVM)",
        "category": ComponentCategory.SIDE_MIRROR,
        "is_exterior_panel": True,
        "requires_paint_matching": True,  # Outer skull cap painting
        "rr_labour_hours": 0.9,
        "default_paint_cost": 1200.0,
    },
    "windshield": {
        "display_name": "Front Windshield Glass (Laminated)",
        "category": ComponentCategory.WINDSHIELD,
        "is_exterior_panel": False,
        "requires_paint_matching": False,
        "rr_labour_hours": 2.5,  # Urethane cut-out, bead prep, curing
        "default_paint_cost": 0.0,
        "consumables_cost": 1500.0,  # OEM PU sealant & primer kit
    },
    "glass": {
        "display_name": "Vehicle Glass / Window",
        "category": ComponentCategory.SIDE_WINDOW,
        "is_exterior_panel": False,
        "requires_paint_matching": False,
        "rr_labour_hours": 1.5,
        "default_paint_cost": 0.0,
    },
    "front_fender": {
        "display_name": "Front Fender Panel",
        "category": ComponentCategory.FRONT_FENDER,
        "is_exterior_panel": True,
        "requires_paint_matching": True,
        "rr_labour_hours": 2.2,
        "default_paint_cost": 3000.0,
    },
    "rear_quarter_panel": {
        "display_name": "Rear Quarter Panel",
        "category": ComponentCategory.REAR_QUARTER_PANEL,
        "is_exterior_panel": True,
        "requires_paint_matching": True,
        "rr_labour_hours": 3.0,
        "default_paint_cost": 3500.0,
    },
    "hood": {
        "display_name": "Engine Hood / Bonnet",
        "category": ComponentCategory.HOOD,
        "is_exterior_panel": True,
        "requires_paint_matching": True,
        "rr_labour_hours": 2.0,
        "default_paint_cost": 3800.0,
    },
    "roof": {
        "display_name": "Vehicle Roof Panel",
        "category": ComponentCategory.ROOF,
        "is_exterior_panel": True,
        "requires_paint_matching": True,
        "rr_labour_hours": 3.5,
        "default_paint_cost": 4500.0,
    },
    "roof_pillar": {
        "display_name": "A/B/C Roof Pillar Section",
        "category": ComponentCategory.ROOF,
        "is_exterior_panel": True,
        "requires_paint_matching": True,
        "rr_labour_hours": 2.5,
        "default_paint_cost": 2500.0,
    },
    "door": {
        "display_name": "Side Door Panel",
        "category": ComponentCategory.DOOR,
        "is_exterior_panel": True,
        "requires_paint_matching": True,
        "rr_labour_hours": 2.5,
        "default_paint_cost": 3200.0,
    },
    "trunk_lid": {
        "display_name": "Trunk Lid / Tailgate",
        "category": ComponentCategory.TRUNK_TAILGATE,
        "is_exterior_panel": True,
        "requires_paint_matching": True,
        "rr_labour_hours": 2.0,
        "default_paint_cost": 3200.0,
    },
    "wheel_tire": {
        "display_name": "Wheel & Tire Assembly",
        "category": ComponentCategory.WHEEL_TIRE,
        "is_exterior_panel": False,
        "requires_paint_matching": False,
        "rr_labour_hours": 0.5,
        "default_paint_cost": 0.0,
    },
    "wheel_area": {
        "display_name": "Wheel Arch & Alloy Assembly",
        "category": ComponentCategory.WHEEL_TIRE,
        "is_exterior_panel": False,
        "requires_paint_matching": False,
        "rr_labour_hours": 0.6,
        "default_paint_cost": 0.0,
    },
}

# ---------------------------------------------------------------------------
# 2. Hourly Labour Rates & GST Tax Constants (India / INR)
# ---------------------------------------------------------------------------

DEFAULT_HOURLY_LABOUR_INR = 750.0  # Independent bodyshop benchmark in India
DEALER_HOURLY_LABOUR_INR = 1450.0  # Authorized OEM workshop benchmark in India
AUTOMOTIVE_GST_PARTS_RATE = 0.18   # Standard GST on automotive parts & services in India (18%)


# ---------------------------------------------------------------------------
# 3. Damage Extent Assessment Logic
# ---------------------------------------------------------------------------

def calculate_extent_category(
    damage_type: str,
    relative_area: Optional[float],
    distinct_count: int = 1,
) -> Tuple[ExtentCategory, str]:
    """Determine transparent extent category without fabricating physical measurements."""
    d_lower = damage_type.lower()

    if d_lower in ("panel_crush", "structural_damage"):
        return ExtentCategory.EXTENSIVE, "Major structural defect affecting panel integrity."

    if relative_area is None:
        if d_lower in ("bumper_smash", "glass_crack"):
            return ExtentCategory.MODERATE, "Defect observed on safety-sensitive component; exact area ratio unmeasured."
        return ExtentCategory.MINOR, "Cosmetic surface irregularity observed."

    # Measured relative pixel area over image or detected vehicle region
    if relative_area >= 0.15 or distinct_count >= 3:
        return ExtentCategory.EXTENSIVE, f"Visible defect spans approximately {round(relative_area * 100, 1)}% of the frame/region."
    elif relative_area >= 0.04 or distinct_count == 2:
        return ExtentCategory.MODERATE, f"Visible defect occupies approximately {round(relative_area * 100, 1)}% of the frame/region."
    else:
        return ExtentCategory.MINOR, f"Localized defect occupying less than {round(relative_area * 100, 1)}% of the frame/region."


# ---------------------------------------------------------------------------
# 4. Repairability Assessment (Repair vs Replacement Feasibility)
# ---------------------------------------------------------------------------

def evaluate_repairability(
    component_id: str,
    damage_type: str,
    extent: ExtentCategory,
) -> Tuple[bool, str, str]:
    """Evaluate whether repairing the component is technically feasible or if replacement is required.
    
    Returns:
        (is_repair_feasible, repair_feasibility_reason, replacement_reason)
    """
    comp = component_id.lower()
    dmg = damage_type.lower()

    # Safety-critical glass & transparent optical parts
    if comp in ("windshield", "glass"):
        if dmg in ("glass_crack", "glass_shatter") and extent in (ExtentCategory.MODERATE, ExtentCategory.EXTENSIVE):
            return (
                False,
                "Laminated windshield cracks longer than 50mm cannot be safely filled under AIS-024 standards.",
                "Mandatory replacement required for structural roof rigidity and driver visibility.",
            )
        else:
            return (
                True,
                "Minor surface chip (<25mm) away from direct driver sightline may be resin-repaired.",
                "Full replacement provides guaranteed optical clarity and airbag backstop integrity.",
            )

    # Lighting assemblies (polycarbonate lenses cannot be panel-beaten)
    if comp in ("headlight", "headlight_area", "taillight"):
        if dmg in ("broken_light", "glass_shatter", "structural_damage"):
            return (
                False,
                "Modern sealed headlamp assemblies with cracked outer polycarbonate lenses allow moisture ingress and cannot be spot-welded.",
                "Full assembly replacement ensures weather seal and beam photometric compliance.",
            )
        else:
            return (
                True,
                "Minor cosmetic surface haze or scratch can be treated with multi-stage abrasive polishing.",
                "Replacement eliminates internal reflector degradation or tab fatigue.",
            )

    # Tires
    if comp in ("wheel_tire", "wheel_area"):
        if dmg in ("flat_tire", "tire_deflated", "structural_damage"):
            return (
                False,
                "Sidewall cuts, carcass bulge, or severe wheel rim cracks cannot be safely plugged for high-speed operation.",
                "Replacement is strictly mandatory to prevent catastrophic blowout.",
            )

    # Sheet metal & bumpers (dents, scratches, minor smashes)
    if dmg == "scratch":
        return (
            True,
            "Clearcoat or primer scratches can be machine-rubbed or spot-painted with color blending.",
            "Complete component replacement is usually unnecessary and uneconomical for surface scratches.",
        )

    if dmg == "dent":
        if extent == ExtentCategory.EXTENSIVE:
            return (
                True,
                "Extensive dent requires hydraulic panel beating, filler, and full panel repainting.",
                "Replacement provides factory stamping precision without filler weight.",
            )
        return (
            True,
            "Minor to moderate dent can be restored via Paintless Dent Repair (PDR) or light panel tapping.",
            "Replacement is optional but typically more costly than PDR.",
        )

    if dmg in ("bumper_smash", "structural_damage"):
        if extent == ExtentCategory.EXTENSIVE:
            return (
                False,
                "Severe plastic bumper tearing or broken mounting tabs cannot withstand future low-speed impacts.",
                "Full bumper skin replacement recommended for proper mounting alignment and energy absorption.",
            )
        return (
            True,
            "Moderate bumper deformities can be heat-reshaped, plastic-welded, primed, and repainted.",
            "Replacement avoids internal plastic stress weakness.",
        )

    # Default: both are feasible options
    return (
        True,
        "Surface restoration and refinishing is technically feasible.",
        "Component replacement installs fresh factory part with new warranty.",
    )


def get_component_metadata(component_id: str) -> Dict[str, Any]:
    """Retrieve metadata for a component, with fallback for unknown components."""
    cid = component_id.lower().strip()
    return COMPONENT_METADATA.get(
        cid,
        {
            "display_name": cid.replace("_", " ").title(),
            "category": ComponentCategory.OTHER_PANEL,
            "is_exterior_panel": True,
            "requires_paint_matching": True,
            "rr_labour_hours": 2.0,
            "default_paint_cost": 3000.0,
        },
    )
