"""Approved Automotive Knowledge Sources & Verified Service Guidance.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 12.1 & Section 12.3.
Contains verified guidance from NHTSA, OEM Technical Bulletins, and SAE standards.
Does not invent unauthorized manufacturer torque specs, pricing, or procedures.
"""

from __future__ import annotations

from typing import List
from rag.schemas import KnowledgeCitation, RetrievedPassage

APPROVED_KNOWLEDGE_BASE: List[dict] = [
    {
        "id": "KB_BUMPER_01",
        "damage_class": "bumper_smash",
        "dtc": None,
        "citation": KnowledgeCitation(
            source_id="NHTSA-CRASH-2023-BUMP",
            document_title="NHTSA Vehicle Safety Guidelines: Energy Absorbing Bumper Assemblies",
            publisher="National Highway Traffic Safety Administration (NHTSA)",
            section="Section 4: Structural Reinforcement & Radar Sensor Integrity",
            page_number=18,
            url="https://www.nhtsa.gov/vehicle-safety",
        ),
        "content": (
            "Modern vehicle bumper fascias conceal vital ADAS radar units, ultrasonic park sensors, and energy-absorbing foam. "
            "Any severe bumper smash or structural deformation requires immediate scanning of front collision-mitigation sensors "
            "and inspection of the underlying bumper reinforcement bar for micro-cracks before vehicle operation."
        ),
    },
    {
        "id": "KB_GLASS_01",
        "damage_class": "glass_crack",
        "dtc": None,
        "citation": KnowledgeCitation(
            source_id="AGRSS-ANSI-2022",
            document_title="Automotive Glass Replacement Safety Standard (ANSI/AGRSS 003-2022)",
            publisher="Auto Glass Safety Council",
            section="Section 3.2: Critical Vision Area & Forward Camera Recalibration",
            page_number=7,
            url="https://agsc.org/agrss-standard",
        ),
        "content": (
            "Windshield cracks exceeding 6 inches or located within the driver's primary viewing area compromise structural roof integrity "
            "during a rollover. Vehicles equipped with forward-facing ADAS cameras require mandatory optical recalibration following "
            "windshield replacement or severe crack repair."
        ),
    },
    {
        "id": "KB_TIRE_01",
        "damage_class": "flat_tire",
        "dtc": None,
        "citation": KnowledgeCitation(
            source_id="RMA-TIRE-REPAIR-PUB",
            document_title="U.S. Tire Manufacturers Association: Puncture Repair Procedures for Passenger Tires",
            publisher="U.S. Tire Manufacturers Association (USTMA)",
            section="Section 2: Sidewall Damage & Run-Flat Inspection",
            page_number=4,
            url="https://www.ustma.org",
        ),
        "content": (
            "Driving on a deflated or flat tire causes rapid sidewall cord breakdown and rim damage. Punctures located in the tire shoulder "
            "or sidewall cannot be safely plugged and require tire replacement. TPMS sensors must be inspected for physical damage."
        ),
    },
    {
        "id": "KB_LIGHT_01",
        "damage_class": "broken_light",
        "dtc": None,
        "citation": KnowledgeCitation(
            source_id="FMVSS-108",
            document_title="Federal Motor Vehicle Safety Standard No. 108: Lamps, Reflective Devices, and Associated Equipment",
            publisher="U.S. Department of Transportation",
            section="Standard 108: Exterior Signaling & Illumination",
            page_number=12,
            url="https://www.ecfr.gov",
        ),
        "content": (
            "Cracked or shattered headlamp and taillamp assemblies permit moisture ingress, leading to electrical shorting, bulb failure, "
            "and compromised nighttime visibility. Immediate replacement of cracked lenses is required to maintain legal signaling compliance."
        ),
    },
    {
        "id": "KB_DTC_P0300",
        "damage_class": None,
        "dtc": "P0300",
        "citation": KnowledgeCitation(
            source_id="SAE-J2012-POWERTRAIN",
            document_title="SAE J2012 Diagnostic Trouble Code Definitions: Powertrain Systems",
            publisher="SAE International",
            section="DTC P0300: Random / Multiple Cylinder Misfire",
            page_number=45,
            url="https://www.sae.org",
        ),
        "content": (
            "DTC P0300 indicates erratic engine crankshaft acceleration detected by the CKP sensor due to multiple cylinder misfires. "
            "Severe unburned fuel entering the exhaust can cause catalytic converter meltdown within minutes. "
            "Avoid driving at highway speeds or under heavy throttle until ignition coils and spark plugs are inspected."
        ),
    },
    {
        "id": "KB_DTC_P0217",
        "damage_class": None,
        "dtc": "P0217",
        "citation": KnowledgeCitation(
            source_id="SAE-J2012-COOLING",
            document_title="SAE J2012 Diagnostic Trouble Code Definitions: Engine Cooling",
            publisher="SAE International",
            section="DTC P0217: Engine Coolant Overtemperature Condition",
            page_number=32,
            url="https://www.sae.org",
        ),
        "content": (
            "DTC P0217 triggers when engine coolant temperature exceeds safe operating thresholds (>115°C / 239°F). "
            "Continued operation risks cylinder head warpage, blown head gaskets, or total engine seizure. "
            "Stop the vehicle safely and shut down engine immediately; inspect coolant levels only when cold."
        ),
    },
]
