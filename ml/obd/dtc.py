"""SAE J2012 Standard Diagnostic Trouble Code (DTC) processing and reference database.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 10.2 & Section 10.3.
Provides verified technical descriptions, severity ratings, and risk escalation tags.
Never invents non-standard DTC interpretations.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional
from ml.obd.schemas import DTCEntry

DTC_PATTERN = re.compile(r"\b([PCBU][0-3][0-9A-Fa-f]{3})\b")

# Verified SAE J2012 DTC Technical Dictionary
SAE_DTC_DATABASE: Dict[str, Dict[str, any]] = {
    "P0300": {
        "system": "Powertrain",
        "description": "Random/Multiple Cylinder Misfire Detected",
        "severity": "critical",
        "escalate_risk": True,
    },
    "P0301": {
        "system": "Powertrain",
        "description": "Cylinder 1 Misfire Detected",
        "severity": "major",
        "escalate_risk": True,
    },
    "P0302": {
        "system": "Powertrain",
        "description": "Cylinder 2 Misfire Detected",
        "severity": "major",
        "escalate_risk": True,
    },
    "P0303": {
        "system": "Powertrain",
        "description": "Cylinder 3 Misfire Detected",
        "severity": "major",
        "escalate_risk": True,
    },
    "P0304": {
        "system": "Powertrain",
        "description": "Cylinder 4 Misfire Detected",
        "severity": "major",
        "escalate_risk": True,
    },
    "P0171": {
        "system": "Powertrain",
        "description": "System Too Lean (Bank 1)",
        "severity": "moderate",
        "escalate_risk": False,
    },
    "P0172": {
        "system": "Powertrain",
        "description": "System Too Rich (Bank 1)",
        "severity": "moderate",
        "escalate_risk": False,
    },
    "P0420": {
        "system": "Powertrain",
        "description": "Catalyst System Efficiency Below Threshold (Bank 1)",
        "severity": "moderate",
        "escalate_risk": False,
    },
    "P0117": {
        "system": "Powertrain",
        "description": "Engine Coolant Temperature Sensor 1 Circuit Low",
        "severity": "major",
        "escalate_risk": True,
    },
    "P0118": {
        "system": "Powertrain",
        "description": "Engine Coolant Temperature Sensor 1 Circuit High",
        "severity": "major",
        "escalate_risk": True,
    },
    "P0217": {
        "system": "Powertrain",
        "description": "Engine Coolant Overtemperature Condition",
        "severity": "critical",
        "escalate_risk": True,
    },
    "P0500": {
        "system": "Powertrain",
        "description": "Vehicle Speed Sensor 'A' Malfunction",
        "severity": "major",
        "escalate_risk": True,
    },
    "C0035": {
        "system": "Chassis",
        "description": "Left Front Wheel Speed Sensor Circuit",
        "severity": "critical",
        "escalate_risk": True,
    },
    "C0040": {
        "system": "Chassis",
        "description": "Right Front Wheel Speed Sensor Circuit",
        "severity": "critical",
        "escalate_risk": True,
    },
    "C0060": {
        "system": "Chassis",
        "description": "Left Front ABS Solenoid #1 Malfunction",
        "severity": "critical",
        "escalate_risk": True,
    },
    "B0001": {
        "system": "Body",
        "description": "Driver Frontal Stage 1 Deployment Control (Airbag Circuit)",
        "severity": "critical",
        "escalate_risk": True,
    },
    "B0028": {
        "system": "Body",
        "description": "Right Side Airbag Deployment Control",
        "severity": "critical",
        "escalate_risk": True,
    },
    "U0100": {
        "system": "Network",
        "description": "Lost Communication With ECM/PCM 'A'",
        "severity": "critical",
        "escalate_risk": True,
    },
    "U0121": {
        "system": "Network",
        "description": "Lost Communication With Anti-Lock Brake System (ABS) Control Module",
        "severity": "critical",
        "escalate_risk": True,
    },
}


def lookup_dtc(code: str) -> DTCEntry:
    """Lookup a single DTC code against verified reference database."""
    clean_code = code.strip().upper()
    if clean_code in SAE_DTC_DATABASE:
        info = SAE_DTC_DATABASE[clean_code]
        return DTCEntry(
            code=clean_code,
            system=info["system"],
            description=info["description"],
            severity=info["severity"],
            escalate_risk=info["escalate_risk"],
            source="SAE J2012 Verified Standard",
        )

    # General SAE category decoding if specific code not in curated dictionary
    first_char = clean_code[0] if clean_code else "P"
    system_map = {"P": "Powertrain", "C": "Chassis", "B": "Body", "U": "Network"}
    system = system_map.get(first_char, "Automotive Subsystem")

    return DTCEntry(
        code=clean_code,
        system=system,
        description=f"Standard Diagnostic Trouble Code ({system} Subsystem)",
        severity="moderate",
        escalate_risk=first_char in ("C", "U"),  # Default conservative escalation for Chassis/Brake/Network
        source="SAE J2012 General Classification",
    )


def extract_dtcs_from_text(text: str) -> List[DTCEntry]:
    """Scan raw text or column values for valid SAE DTC codes."""
    matches = set(DTC_PATTERN.findall(text))
    return [lookup_dtc(code) for code in sorted(list(matches))]
