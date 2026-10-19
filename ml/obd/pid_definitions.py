"""Centralized OBD-II Telemetry PID Definitions, Metadata, and Plain-English Explanations.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 10 and Master Prompt.
Provides:
  1. Canonical PID metadata, aliases, and source field normalization.
  2. Configurable monitoring threshold ranges with documented sources.
  3. Directionality analysis (e.g., negative vs positive fuel trim).
  4. Plain-English descriptions for non-technical vehicle owners.
  5. Sample statistic calculations based strictly on valid recorded observations.
  6. Transparent diagnostic limitations and uncertainty disclaimers.
  7. Cross-finding consistency checks (e.g., DTC P0171 vs negative fuel trim).
  8. Honest fallback for unknown or unverified sensor parameters.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


@dataclass
class PIDConfig:
    """Configurable monitoring range and metadata for a telemetry PID."""
    canonical_name: str
    display_title: str
    physical_meaning: str
    unit: str
    configured_range: List[float]
    range_source: str
    source_citation: str
    technical_details: str
    possible_causes_high: List[str] = field(default_factory=list)
    possible_causes_low: List[str] = field(default_factory=list)
    recommended_action: str = ""
    limitations: List[str] = field(default_factory=list)
    aliases: List[re.Pattern] = field(default_factory=list)
    bank: Optional[int] = None
    sensor_index: Optional[int] = None


# Default PID Metadata and Configurable Monitoring Ranges
# Note: Ranges represent application monitoring boundaries for anomaly detection,
# NOT universally guaranteed OEM manufacturer operating specifications.
DEFAULT_PID_REGISTRY: Dict[str, PIDConfig] = {
    "FUEL_TRIM_SHORT": PIDConfig(
        canonical_name="FUEL_TRIM_SHORT",
        display_title="Engine Fuel Adjustment Outside Expected Range",
        physical_meaning=(
            "The vehicle's computer is making an adjustment to the amount of fuel "
            "supplied to the engine to maintain proper combustion."
        ),
        unit="%",
        configured_range=[-15.0, 15.0],
        range_source=(
            "Application configured monitoring range [-15.0, 15.0] % based on SAE J1979 / OBD-II "
            "standard closed-loop trim bounds. Not a vehicle-specific OEM specification."
        ),
        source_citation="SAE J1979 / ISO 15031-5 Diagnostic Test Modes (Mode $01 PID $06)",
        technical_details=(
            "Short-term fuel trim (STFT) represents immediate closed-loop stoichiometric feedback "
            "adjustments made by the engine control module (ECM) based on switching oxygen or wideband lambda sensor signals."
        ),
        possible_causes_low=[
            "Leaking or sticking fuel injector delivering excess fuel into cylinder",
            "Excessive fuel rail pressure or faulty fuel pressure regulator",
            "Evaporative emissions (EVAP) canister purge valve stuck open admitting fuel vapor",
            "Biased or contaminated oxygen / air-fuel ratio sensor signaling false lean",
            "Restricted intake air filter or ducting reducing air volume",
        ],
        possible_causes_high=[
            "Intake manifold vacuum leak or unmetered air entering downstream of MAF sensor",
            "Low fuel rail pressure, weak fuel pump, or restricted fuel filter",
            "Clogged or restricted fuel injectors delivering insufficient fuel",
            "Exhaust manifold leak upstream of the primary oxygen sensor",
            "Contaminated Mass Air Flow (MAF) sensor under-reporting incoming air flow",
        ],
        recommended_action=(
            "If this is a valid reading from the vehicle, arrange a diagnostic check, "
            "particularly if the engine is running roughly, fuel consumption has changed, or the engine warning light is on."
        ),
        limitations=[
            "This reading alone does not prove that a component is faulty or establish whether the vehicle is safe to drive.",
            "The reading must be interpreted in the vehicle's operating context (idle vs load, open-loop vs closed-loop fuel control).",
            "A single fuel-trim reading cannot identify a specific faulty sensor, injector, fuel pump, or mechanical part.",
        ],
        aliases=[
            re.compile(r"short.*term.*fuel.*trim.*(?:bank\s*1|\b1\b)|stft\s*1\b|stft1\b|fuel_trim_short(?:_b1)?\b", re.I),
            re.compile(r"short.*term.*fuel.*trim|stft", re.I),
        ],
        bank=1,
    ),
    "FUEL_TRIM_SHORT_B2": PIDConfig(
        canonical_name="FUEL_TRIM_SHORT_B2",
        display_title="Engine Fuel Adjustment (Bank 2) Outside Expected Range",
        physical_meaning=(
            "The vehicle's computer is making an adjustment to the amount of fuel "
            "supplied to Bank 2 of the engine to maintain proper combustion."
        ),
        unit="%",
        configured_range=[-15.0, 15.0],
        range_source=(
            "Application configured monitoring range [-15.0, 15.0] % based on SAE J1979 / OBD-II "
            "standard closed-loop trim bounds for Bank 2. Not a vehicle-specific OEM specification."
        ),
        source_citation="SAE J1979 / ISO 15031-5 Diagnostic Test Modes (Mode $01 PID $08)",
        technical_details=(
            "Short-term fuel trim Bank 2 (STFT B2) represents immediate closed-loop stoichiometric "
            "adjustments made by the ECM for the secondary cylinder bank."
        ),
        possible_causes_low=[
            "Leaking fuel injector on Bank 2",
            "Excessive fuel rail pressure on Bank 2 rail",
            "Biased Bank 2 oxygen sensor signaling false lean",
            "Ignition or mechanical issue causing unburned fuel on Bank 2",
        ],
        possible_causes_high=[
            "Intake manifold vacuum leak localized to Bank 2",
            "Clogged or restricted Bank 2 fuel injectors",
            "Exhaust leak upstream of Bank 2 oxygen sensor",
            "Faulty Bank 2 oxygen sensor reading falsely rich",
        ],
        recommended_action=(
            "If this reading is confirmed, arrange a diagnostic check with a qualified technician "
            "to inspect Bank 2 fuel trims and related sensors."
        ),
        limitations=[
            "This reading alone does not prove that a component is faulty or establish whether the vehicle is safe to drive.",
            "The reading must be interpreted alongside Bank 1 values and engine load context.",
            "Cannot isolate individual injectors or sensors without cylinder-specific testing.",
        ],
        aliases=[
            re.compile(r"short.*term.*fuel.*trim.*(?:bank\s*2|\b2\b)|stft\s*2\b|stft2\b|fuel_trim_short_b2\b", re.I),
        ],
        bank=2,
    ),
    "FUEL_TRIM_LONG": PIDConfig(
        canonical_name="FUEL_TRIM_LONG",
        display_title="Long-Term Fuel Adjustment Outside Expected Range",
        physical_meaning=(
            "The vehicle's computer has learned a sustained correction to fuel delivery "
            "over multiple driving cycles to compensate for ongoing fuel or air imbalances."
        ),
        unit="%",
        configured_range=[-15.0, 15.0],
        range_source=(
            "Application configured monitoring range [-15.0, 15.0] % based on SAE J1979 / OBD-II "
            "standard learned adaptive trim bounds. Not a vehicle-specific OEM specification."
        ),
        source_citation="SAE J1979 / ISO 15031-5 Diagnostic Test Modes (Mode $01 PID $07)",
        technical_details=(
            "Long-term fuel trim (LTFT) represents persistent learned fuel table offsets stored in ECM non-volatile memory."
        ),
        possible_causes_low=[
            "Persistent fuel injector leakage or high system fuel pressure",
            "Persistent EVAP canister purge flow during closed loop",
            "Aging or contaminated upstream lambda sensor drift",
        ],
        possible_causes_high=[
            "Persistent vacuum or intake duct leak",
            "Degraded fuel pump or restricted fuel filter",
            "Dirty mass air flow sensor measuring less air than actual",
        ],
        recommended_action=(
            "Arrange a professional diagnostic inspection to check for sustained vacuum leaks or fuel delivery issues."
        ),
        limitations=[
            "LTFT represents accumulated adaptations and may reflect past conditions that have already been resolved.",
            "Cannot independently confirm component failure without live data and freeze frame evaluation.",
        ],
        aliases=[
            re.compile(r"long.*term.*fuel.*trim.*(?:bank\s*1|\b1\b)|ltft\s*1\b|ltft1\b|fuel_trim_long(?:_b1)?\b", re.I),
            re.compile(r"long.*term.*fuel.*trim|ltft", re.I),
        ],
        bank=1,
    ),
    "FUEL_TRIM_LONG_B2": PIDConfig(
        canonical_name="FUEL_TRIM_LONG_B2",
        display_title="Long-Term Fuel Adjustment (Bank 2) Outside Expected Range",
        physical_meaning=(
            "The vehicle's computer has learned a sustained correction to fuel delivery "
            "for Bank 2 over multiple driving cycles."
        ),
        unit="%",
        configured_range=[-15.0, 15.0],
        range_source=(
            "Application configured monitoring range [-15.0, 15.0] % based on SAE J1979 / OBD-II "
            "standard learned adaptive trim bounds for Bank 2. Not a vehicle-specific OEM specification."
        ),
        source_citation="SAE J1979 / ISO 15031-5 Diagnostic Test Modes (Mode $01 PID $09)",
        technical_details=(
            "Long-term fuel trim Bank 2 represents persistent learned fuel table offsets for cylinder bank 2."
        ),
        possible_causes_low=[
            "Bank 2 injector leakage or high rail pressure",
            "Drifted Bank 2 oxygen sensor",
        ],
        possible_causes_high=[
            "Bank 2 intake manifold gasket leak",
            "Restricted Bank 2 fuel injectors",
        ],
        recommended_action="Arrange a professional inspection to compare Bank 1 and Bank 2 trim profiles.",
        limitations=[
            "Learned trim values may reflect operating history rather than current transient faults.",
        ],
        aliases=[
            re.compile(r"long.*term.*fuel.*trim.*(?:bank\s*2|\b2\b)|ltft\s*2\b|ltft2\b|fuel_trim_long_b2\b", re.I),
        ],
        bank=2,
    ),
    "ENGINE_COOLANT_TEMP": PIDConfig(
        canonical_name="ENGINE_COOLANT_TEMP",
        display_title="Engine Coolant Temperature Outside Expected Range",
        physical_meaning=(
            "Measures the temperature of the liquid circulating through the engine to carry away excess heat."
        ),
        unit="°C",
        configured_range=[75.0, 105.0],
        range_source=(
            "Application configured monitoring range [75.0, 105.0] °C based on typical modern passenger vehicle "
            "fully-warmed operating temperatures. Not a universal OEM specification."
        ),
        source_citation="SAE J1979 / ISO 15031-5 Diagnostic Test Modes (Mode $01 PID $05)",
        technical_details=(
            "Engine Coolant Temperature (ECT) sensor utilizes a negative temperature coefficient (NTC) thermistor "
            "reporting engine thermal status to the powertrain control module."
        ),
        possible_causes_low=[
            "Engine recently started and still in warm-up phase",
            "Thermostat stuck open preventing engine from reaching normal operating temperature",
            "Faulty coolant temperature sensor or circuit resistance issue",
        ],
        possible_causes_high=[
            "Low coolant level or coolant leak in cooling system",
            "Thermostat stuck closed or failing water pump",
            "Radiator cooling fan inoperative or radiator core obstructed",
            "Head gasket failure or severe engine overheating",
        ],
        recommended_action=(
            "If the temperature is high, check coolant levels when the engine is completely cold. "
            "If the temperature exceeds normal range during driving, pull over safely to prevent engine damage."
        ),
        limitations=[
            "Temperatures below range are normal immediately after engine startup until full operating warm-up.",
            "Vehicle-specific thermostat opening temperatures vary between 82°C and 105°C depending on manufacturer calibration.",
        ],
        aliases=[
            re.compile(r"coolant.*temp|engine.*temp|ect\b", re.I),
        ],
    ),
    "ENGINE_RPM": PIDConfig(
        canonical_name="ENGINE_RPM",
        display_title="Engine Speed (RPM) Outside Expected Range",
        physical_meaning=(
            "Measures how fast the engine crankshaft is spinning in revolutions per minute."
        ),
        unit="RPM",
        configured_range=[600.0, 6500.0],
        range_source=(
            "Application configured monitoring range [600.0, 6500.0] RPM representing typical passenger vehicle "
            "operating limits between warm idle and redline. Not a vehicle-specific OEM specification."
        ),
        source_citation="SAE J1979 / ISO 15031-5 Diagnostic Test Modes (Mode $01 PID $0C)",
        technical_details=(
            "Engine RPM is calculated from crankshaft position sensor (CKP) reluctance or Hall-effect pulse intervals."
        ),
        possible_causes_low=[
            "Engine stalling, rough idle, or idle air control issue",
            "Crankshaft position sensor signal dropout",
            "Low battery voltage or excessive electrical loading at idle",
        ],
        possible_causes_high=[
            "Aggressive acceleration or sustained high-RPM driving",
            "Transmission slippage or failure to upshift",
            "Unintended throttle opening or cruise control anomaly",
        ],
        recommended_action="If engine speed fluctuates erratically at idle or fails to rev smoothly, arrange an idle and ignition check.",
        limitations=[
            "Engine RPM naturally varies from idle (600-800 RPM) to higher cruising speeds. Operating above idle is expected during driving.",
        ],
        aliases=[
            re.compile(r"engine.*rpm|crankshaft.*speed|\brpm\b", re.I),
        ],
    ),
    "VEHICLE_SPEED": PIDConfig(
        canonical_name="VEHICLE_SPEED",
        display_title="Vehicle Speed Outside Expected Range",
        physical_meaning="Measures the forward road speed of the vehicle.",
        unit="km/h",
        configured_range=[0.0, 200.0],
        range_source="Application configured monitoring range [0.0, 200.0] km/h.",
        source_citation="SAE J1979 / ISO 15031-5 Diagnostic Test Modes (Mode $01 PID $0D)",
        technical_details="Calculated by the vehicle speed sensor (VSS) or wheel speed sensors via ABS/ESC module over CAN bus.",
        possible_causes_low=["Vehicle stationary or driving in heavy stop-and-go traffic."],
        possible_causes_high=["High-speed highway travel or potential speed sensor calibration mismatch."],
        recommended_action="Verify speedometer accuracy if readings do not correspond to driving conditions.",
        limitations=["Vehicle speed varies constantly with traffic conditions and road limits."],
        aliases=[
            re.compile(r"vehicle.*speed|speed.*sensor|\bvss\b", re.I),
        ],
    ),
    "THROTTLE_POS": PIDConfig(
        canonical_name="THROTTLE_POS",
        display_title="Throttle Position Outside Expected Range",
        physical_meaning="Indicates the opening percentage of the engine throttle plate or electronic throttle control valve.",
        unit="%",
        configured_range=[0.0, 100.0],
        range_source="Application configured monitoring range [0.0, 100.0] %.",
        source_citation="SAE J1979 / ISO 15031-5 Diagnostic Test Modes (Mode $01 PID $11)",
        technical_details="Reports throttle position sensor (TPS) potentiometer or Hall-effect sensor percentage.",
        possible_causes_low=["Closed throttle during idle or coasting deceleration."],
        possible_causes_high=["Wide-open throttle during hard acceleration."],
        recommended_action="Have the throttle body inspected for carbon buildup if pedal response is sluggish or erratic.",
        limitations=["Relative throttle position values may read 10-20% at idle on electronic throttle bodies (ETB)."],
        aliases=[
            re.compile(r"throttle|pedal.*pos|tps\b", re.I),
        ],
    ),
    "ENGINE_LOAD": PIDConfig(
        canonical_name="ENGINE_LOAD",
        display_title="Engine Load Outside Expected Range",
        physical_meaning="Represents the percentage of maximum available torque or air capacity currently being demanded from the engine.",
        unit="%",
        configured_range=[0.0, 100.0],
        range_source="Application configured monitoring range [0.0, 100.0] % based on SAE J1979 standard load calculation.",
        source_citation="SAE J1979 / ISO 15031-5 Diagnostic Test Modes (Mode $01 PID $04)",
        technical_details="Calculated load value as defined by SAE J1979: current airflow divided by peak airflow at standard temperature and pressure.",
        possible_causes_low=["Deceleration fuel cut-off or light engine idling."],
        possible_causes_high=["Steep uphill climbing, heavy towing, or full-throttle acceleration."],
        recommended_action="If engine load remains abnormally high at idle or light cruising, check for binding brakes or restricted exhaust.",
        limitations=["Engine load is a calculated mathematical value dependent on MAF/MAP calibration and air density."],
        aliases=[
            re.compile(r"engine.*load|calc.*load", re.I),
        ],
    ),
    "INTAKE_PRESSURE": PIDConfig(
        canonical_name="INTAKE_PRESSURE",
        display_title="Intake Manifold Pressure Outside Expected Range",
        physical_meaning="Measures the absolute air pressure inside the engine intake manifold downstream of the throttle.",
        unit="kPa",
        configured_range=[20.0, 255.0],
        range_source="Application configured monitoring range [20.0, 255.0] kPa.",
        source_citation="SAE J1979 / ISO 15031-5 Diagnostic Test Modes (Mode $01 PID $0B)",
        technical_details="Intake manifold absolute pressure (MAP) sensor reports intake vacuum (below atmospheric ~101 kPa) or boost pressure on turbocharged engines.",
        possible_causes_low=["High manifold vacuum during closed-throttle deceleration."],
        possible_causes_high=["Turbocharger boost, heavy engine load, or intake vacuum leak at idle."],
        recommended_action="If manifold pressure is abnormally high at idle (above 50 kPa), inspect for intake vacuum leaks.",
        limitations=["Values depend on atmospheric elevation and whether the vehicle is naturally aspirated or turbocharged."],
        aliases=[
            re.compile(r"intake.*manifold.*press|intake.*press|\bmap\b", re.I),
        ],
    ),
    "INTAKE_AIR_TEMP": PIDConfig(
        canonical_name="INTAKE_AIR_TEMP",
        display_title="Intake Air Temperature Outside Expected Range",
        physical_meaning="Measures the temperature of the ambient air entering the engine intake system.",
        unit="°C",
        configured_range=[-20.0, 60.0],
        range_source="Application configured monitoring range [-20.0, 60.0] °C based on typical operating climates.",
        source_citation="SAE J1979 / ISO 15031-5 Diagnostic Test Modes (Mode $01 PID $0F)",
        technical_details="Intake Air Temperature (IAT) sensor thermistor placed in air ducting or integrated with MAF sensor.",
        possible_causes_low=["Extreme winter ambient conditions or open sensor circuit."],
        possible_causes_high=["Under-hood heat soak during extended idling, desert climate, or turbocharger intercooler heat soak."],
        recommended_action="If temperature reads high while moving, check cold-air intake ducting and intercooler airflow.",
        limitations=["Under-hood heat soak after sitting with engine off can temporarily elevate IAT readings."],
        aliases=[
            re.compile(r"intake.*air.*temp|\biat\b", re.I),
        ],
    ),
    "MAF_AIR_FLOW": PIDConfig(
        canonical_name="MAF_AIR_FLOW",
        display_title="Mass Air Flow Rate Outside Expected Range",
        physical_meaning="Measures the total mass of air entering the engine cylinders per second.",
        unit="g/s",
        configured_range=[1.0, 300.0],
        range_source="Application configured monitoring range [1.0, 300.0] g/s.",
        source_citation="SAE J1979 / ISO 15031-5 Diagnostic Test Modes (Mode $01 PID $10)",
        technical_details="Hot-wire or hot-film Mass Air Flow (MAF) sensor measuring instantaneous intake air volume and density.",
        possible_causes_low=["Engine idling or air intake restriction."],
        possible_causes_high=["High RPM full-throttle operation or false high reading from oil/dirt contamination on sensor wire."],
        recommended_action="Clean the MAF sensor with approved electronics cleaner if readings are erratic or causing fuel trim codes.",
        limitations=["Expected air flow scales directly with engine displacement and current RPM."],
        aliases=[
            re.compile(r"mass.*air.*flow|air.*flow.*rate|\bmaf\b", re.I),
        ],
    ),
}


class PIDDescriptionSystem:
    """Central registry and explanation generator for OBD-II telemetry PIDs."""

    def __init__(self, custom_configs: Optional[Dict[str, PIDConfig]] = None):
        self.registry: Dict[str, PIDConfig] = dict(DEFAULT_PID_REGISTRY)
        if custom_configs:
            self.registry.update(custom_configs)

    def match_column(self, raw_header: str) -> Optional[Tuple[str, PIDConfig]]:
        """Match a raw CSV header to a verified canonical PID configuration.

        Preserves bank-specific mappings (e.g. Bank 2) when identified in the header.
        """
        clean = raw_header.strip()

        # Check Bank 2 specific patterns first to avoid greedy general matches
        for name, config in self.registry.items():
            if config.bank == 2:
                for pattern in config.aliases:
                    if pattern.search(clean):
                        return name, config

        # Then check remaining canonical PIDs
        for name, config in self.registry.items():
            if config.bank != 2:
                for pattern in config.aliases:
                    if pattern.search(clean):
                        return name, config

        return None

    def get_config(self, canonical_name: str) -> Optional[PIDConfig]:
        """Retrieve PID configuration for a canonical name."""
        return self.registry.get(canonical_name)

    def explain_directionality(
        self,
        canonical_name: str,
        observed_value: float,
        unit: str,
        configured_range: Optional[List[float]],
    ) -> Tuple[str, str]:
        """Explain what a specific reading means in physical terms, including directionality.

        Returns:
            Tuple of (directionality_tag, explanation_text)
        """
        if not np.isfinite(observed_value):
            return "invalid", "The sensor reading could not be converted to a valid finite numeric measurement."

        # Fuel Trim directionality
        if "FUEL_TRIM" in canonical_name:
            if observed_value < 0:
                direction = "negative"
                meaning = (
                    "A negative fuel-trim value means the engine computer is reducing fuel delivery "
                    "relative to its calculated baseline. A positive value means it is adding fuel. "
                    "A strongly negative reading can indicate that the computer is trying to compensate "
                    "for a mixture it considers too rich, but this reading alone cannot identify the cause."
                )
            elif observed_value > 0:
                direction = "positive"
                meaning = (
                    "A positive fuel-trim value means the engine computer is adding fuel relative to "
                    "its calculated baseline. A negative value means it is reducing fuel. "
                    "A strongly positive reading can indicate that the computer is trying to compensate "
                    "for a mixture it considers too lean, but this reading alone cannot identify the cause."
                )
            else:
                direction = "neutral"
                meaning = (
                    "A fuel-trim reading of 0.0% indicates that the engine computer is not applying any "
                    "correction to baseline fuel delivery."
                )
            return direction, meaning

        # General range-based directionality
        if configured_range and len(configured_range) == 2:
            min_val, max_val = configured_range
            if observed_value > max_val:
                direction = "above_range"
                if "COOLANT" in canonical_name:
                    meaning = (
                        f"The recorded temperature of {observed_value}{unit} is above the application's "
                        f"configured monitoring threshold of {max_val}{unit}. This indicates the engine "
                        "is operating warmer than typical steady-state conditions."
                    )
                elif "RPM" in canonical_name:
                    meaning = (
                        f"The recorded engine speed of {observed_value} {unit} is above the application's "
                        f"configured monitoring range of {max_val} {unit}, reflecting high-engine-speed operation."
                    )
                else:
                    meaning = (
                        f"The recorded measurement of {observed_value} {unit} is above the application's "
                        f"configured monitoring range [{min_val}, {max_val}] {unit}."
                    )
            elif observed_value < min_val:
                direction = "below_range"
                if "COOLANT" in canonical_name:
                    meaning = (
                        f"The recorded temperature of {observed_value}{unit} is below the application's "
                        f"configured monitoring threshold of {min_val}{unit}. This is normal during initial warm-up, "
                        "but if persistent, it may indicate a thermostat or sensor issue."
                    )
                elif "RPM" in canonical_name:
                    meaning = (
                        f"The recorded engine speed of {observed_value} {unit} is below typical idle speed "
                        f"({min_val} {unit}), indicating possible engine stalling or idle control struggle."
                    )
                else:
                    meaning = (
                        f"The recorded measurement of {observed_value} {unit} is below the application's "
                        f"configured monitoring range [{min_val}, {max_val}] {unit}."
                    )
            else:
                direction = "within_range"
                meaning = (
                    f"The recorded measurement of {observed_value} {unit} is within the application's "
                    f"configured monitoring range [{min_val}, {max_val}] {unit}."
                )
            return direction, meaning

        return "unspecified", f"Recorded measurement: {observed_value} {unit}."

    def build_sample_explanation(
        self,
        valid_outside: int,
        valid_total: int,
        pct_outside: Optional[float],
    ) -> str:
        """Build an accurate, non-misleading explanation of sample statistics.

        Explicitly clarifies that sample percentage applies only to logged telemetry observations,
        not to physical vehicle damage or operating time duration.
        """
        if valid_total == 0 or pct_outside is None:
            return (
                "Sample statistics unavailable: no valid numeric samples were recorded for this sensor."
            )

        pct_formatted = f"{round(pct_outside, 1)}%"
        return (
            f"{pct_formatted} of the recorded telemetry samples were outside the application's "
            f"configured monitoring range ({valid_outside} of {valid_total} valid observations). "
            "This percentage refers strictly to recorded data samples in this session and does not "
            "indicate that any percentage of the vehicle is damaged or that total operating time was abnormal."
        )

    def check_p0171_fuel_trim_consistency(
        self,
        dtc_codes: List[str],
        canonical_name: str,
        observed_value: float,
        has_timestamps: bool = False,
        same_bank: bool = False,
    ) -> Optional[str]:
        """Analyze potential DTC P0171 vs negative fuel trim inconsistency.

        DTC P0171 indicates 'System Too Lean (Bank 1)'. In steady state, a lean condition causes
        the ECU to add positive fuel trim (+STFT/+LTFT).
        If telemetry shows a strongly negative fuel trim (-STFT), this appears inconsistent if assumed
        to represent the same operating condition and bank.
        """
        dtc_upper = [d.strip().upper() for d in dtc_codes]
        if "P0171" not in dtc_upper:
            return None

        # Only relevant for negative fuel trim readings
        if "FUEL_TRIM" in canonical_name and observed_value < -10.0:
            if not has_timestamps or not same_bank:
                return (
                    "We also found a lean-mixture diagnostic code (P0171). This fuel-adjustment reading "
                    f"({observed_value}%) does not clearly explain that code. Because the readings may come "
                    "from different conditions or sensor contexts, a technician should review the complete diagnostic data."
                )
            else:
                return (
                    "We also found a lean-mixture diagnostic code (P0171) on the same bank. "
                    f"This negative fuel-trim reading ({observed_value}%) appears divergent from a typical steady-state "
                    "lean compensation. This can occur during transient deceleration fuel cut-off or intermittent "
                    "sensor conditions, and requires comprehensive diagnostic review."
                )

        return None

    def build_honest_fallback(
        self,
        raw_column_name: str,
        observed_value: float,
        unit: str = "",
        valid_outside: int = 0,
        valid_total: int = 0,
        pct_outside: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Construct an honest, transparent fallback for unmapped or unverified PIDs."""
        sample_explanation = self.build_sample_explanation(valid_outside, valid_total, pct_outside)
        return {
            "pid_name": raw_column_name,
            "raw_column_name": raw_column_name,
            "simple_title": f"Unverified Sensor Reading ({raw_column_name})",
            "what_we_found": (
                "We found an unusual reading, but we do not yet have a verified explanation for this sensor. "
                "A qualified technician can review the reading and vehicle-specific information."
            ),
            "observed_value": round(observed_value, 2) if np.isfinite(observed_value) else 0.0,
            "unit": unit,
            "value_meaning": (
                "This reading was recorded from an unmapped or vehicle-specific diagnostic parameter. "
                "The exact physical meaning, scaling, and operating baseline depend on the vehicle manufacturer's specification."
            ),
            "sample_percentage_outside": round(pct_outside, 1) if pct_outside is not None else None,
            "sample_count_evaluated": valid_total,
            "sample_count_outside": valid_outside,
            "sample_explanation": sample_explanation,
            "configured_range": None,
            "range_source": "No standard monitoring range configured for this unmapped parameter.",
            "what_you_should_do": (
                "Have a qualified technician review the raw reading using vehicle-specific service documentation."
            ),
            "possible_causes": [
                "Proprietary manufacturer-specific parameter",
                "Non-standard diagnostic PID scaling or dialect",
                "Transient sensor noise or recording artifact",
            ],
            "limitations": [
                "No verified SAE J1979 standard definition is available in the application library for this parameter.",
                "This reading alone does not prove that a component is faulty or establish whether the vehicle is safe to drive.",
            ],
            "cross_finding_notice": None,
            "source": "Unmapped Telemetry Channel",
            "technical_details": f"Raw channel identifier: {raw_column_name}. Unit: {unit or 'unspecified'}.",
            "directionality": "unverified",
        }


# Global singleton instance
PID_REGISTRY = PIDDescriptionSystem()
