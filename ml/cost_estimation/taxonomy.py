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


def infer_damage_summary_from_detections(
    images_or_dicts: List[Any],
) -> Tuple[str, str, ExtentCategory, float, int, Optional[str], float, float]:
    """Infers (component_id, damage_type, extent_category, rel_area, distinct_cnt, finding_id, dmg_conf, comp_conf)
    from visual inspection detections (either ImageFinding objects or report JSON dicts).
    """
    candidates = []
    total_detections = 0

    CLASS_WEIGHTS = {
        "bumper_smash": 3.0,
        "broken_light": 2.5,
        "lamp broken": 2.5,
        "broken_mirror": 2.2,
        "glass_crack": 2.2,
        "glass shatter": 2.2,
        "flat_tire": 2.0,
        "tire flat": 2.0,
        "dent": 1.8,
        "crack": 1.5,
        "scratch": 1.0,
    }

    for img in (images_or_dicts or []):
        if hasattr(img, "detections"):
            dets = getattr(img, "detections", []) or []
            transforms = getattr(img, "transforms", None)
            orig_w = getattr(transforms, "original_width", 1024) if transforms else 1024
            orig_h = getattr(transforms, "original_height", 1024) if transforms else 1024
        elif isinstance(img, dict):
            dets = img.get("detections", []) or []
            transforms = img.get("transforms") or {}
            orig_w = transforms.get("original_width", 1024)
            orig_h = transforms.get("original_height", 1024)
        else:
            continue

        total_detections += len(dets)
        for d in dets:
            if isinstance(d, dict):
                inst_id = d.get("instance_id") or d.get("detection_id")
                label = (d.get("label") or d.get("damage_class") or d.get("source_label") or "scratch").lower()
                conf = float(d.get("confidence") or 0.85)
                rel_area = d.get("relative_area")
                comp_hint = d.get("component")
                bbox = d.get("bbox_xyxy")
            else:
                inst_id = getattr(d, "instance_id", None) or getattr(d, "detection_id", None)
                label = (getattr(d, "label", None) or getattr(d, "damage_class", None) or getattr(d, "source_label", None) or "scratch").lower()
                conf = float(getattr(d, "confidence", 0.85))
                rel_area = getattr(d, "relative_area", None)
                comp_hint = getattr(d, "component", None)
                bbox = getattr(d, "bbox_xyxy", None)

            # Compute relative area if not provided
            if rel_area is None or float(rel_area) <= 0.0:
                if bbox and len(bbox) == 4 and orig_h > 0 and orig_w > 0:
                    bw = max(0.0, float(bbox[2]) - float(bbox[0]))
                    bh = max(0.0, float(bbox[3]) - float(bbox[1]))
                    rel_area = round((bw * bh) / max(1.0, float(orig_w * orig_h)), 4)
                else:
                    rel_area = 0.03
            else:
                rel_area = float(rel_area)

            # Spatial center
            cy = 0.5
            cx = 0.5
            if bbox and len(bbox) == 4 and orig_h > 0 and orig_w > 0:
                cy = (float(bbox[1]) + float(bbox[3])) / (2.0 * float(orig_h))
                cx = (float(bbox[0]) + float(bbox[2])) / (2.0 * float(orig_w))

            # Weight score to pick most prominent damage
            base_w = 1.0
            for k, w in CLASS_WEIGHTS.items():
                if k in label:
                    base_w = max(base_w, w)
            score = base_w * (rel_area + 0.02) * conf

            candidates.append({
                "inst_id": inst_id,
                "label": label,
                "conf": conf,
                "rel_area": rel_area,
                "comp_hint": comp_hint,
                "score": score,
                "cy": cy,
                "cx": cx,
            })

    if not candidates:
        raise ValueError("No damage detected across vehicle inspection images.")

    # Sort candidates by prominence
    top = max(candidates, key=lambda c: c["score"])
    lbl = top["label"]
    comp_hint = top["comp_hint"]
    cy = top["cy"]
    cx = top["cx"]

    # Deduce component
    if comp_hint and comp_hint in COMPONENT_METADATA:
        chosen_comp = comp_hint
    elif "light" in lbl or "lamp" in lbl:
        chosen_comp = "taillight" if "rear" in lbl or "tail" in lbl else "headlight"
    elif "mirror" in lbl:
        chosen_comp = "side_mirror"
    elif "windshield" in lbl or "glass" in lbl or "window" in lbl:
        chosen_comp = "windshield"
    elif "tire" in lbl or "wheel" in lbl:
        chosen_comp = "wheel_tire"
    elif "bumper" in lbl:
        chosen_comp = "rear_bumper" if "rear" in lbl else "front_bumper"
    elif "hood" in lbl or "bonnet" in lbl:
        chosen_comp = "hood"
    elif "door" in lbl:
        chosen_comp = "door"
    elif "fender" in lbl:
        chosen_comp = "front_fender"
    elif "quarter" in lbl:
        chosen_comp = "rear_quarter_panel"
    elif "roof" in lbl:
        chosen_comp = "roof"
    else:
        # Positional heuristic from vertical and horizontal center
        if cy > 0.68:
            chosen_comp = "front_bumper"
        elif cy < 0.32:
            chosen_comp = "hood" if 0.2 <= cx <= 0.8 else "front_fender"
        else:
            if cx < 0.25 or cx > 0.75:
                chosen_comp = "front_fender"
            else:
                chosen_comp = "door"

    # Deduce damage type
    if "bumper_smash" in lbl or "smash" in lbl:
        chosen_dmg = "bumper_damage" if "bumper" in chosen_comp else "dent"
    elif "light" in lbl or "lamp" in lbl:
        chosen_dmg = "broken_light"
    elif "mirror" in lbl:
        chosen_dmg = "broken_mirror"
    elif "glass" in lbl or "windshield" in lbl or "shatter" in lbl or "crack" in lbl:
        chosen_dmg = "glass_crack"
    elif "tire" in lbl or "wheel" in lbl:
        chosen_dmg = "flat_tire"
    elif "dent" in lbl:
        chosen_dmg = "dent"
    elif "scratch" in lbl:
        chosen_dmg = "scratch"
    else:
        chosen_dmg = "dent" if "dent" in lbl else "scratch"

    extent_cat, _ = calculate_extent_category(
        damage_type=chosen_dmg,
        relative_area=top["rel_area"],
        distinct_count=max(1, total_detections),
    )

    return (
        chosen_comp,
        chosen_dmg,
        extent_cat,
        top["rel_area"],
        max(1, total_detections),
        top["inst_id"],
        top["conf"],
        0.80 if comp_hint else 0.70,
    )
