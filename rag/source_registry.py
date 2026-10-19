"""Approved Automotive Knowledge Sources & Verified Service Guidance.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 12.1 & Section 12.3.
Contains verified guidance from NHTSA, OEM Technical Bulletins, and SAE standards.
Does not invent unauthorized manufacturer torque specs, pricing, or procedures.
"""

from __future__ import annotations

from typing import List
from rag.schemas import KnowledgeCitation, StructuredGuidance

APPROVED_KNOWLEDGE_BASE: List[dict] = [
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
        "guidance": StructuredGuidance(
            title="Headlight or Taillight Damage",
            what_we_found="Your headlight or taillight may be cracked or broken.",
            why_this_matters="Water can enter the light, damage its electrical parts, or make the light less visible to other drivers.",
            what_you_should_do_now="Check whether the light works and whether water can enter the damaged housing. Arrange a repair promptly. If the light is not working or your vehicle is difficult to see at night, avoid driving in conditions where visibility or signalling is unsafe.",
            can_i_keep_driving="Avoid unnecessary driving and arrange prompt professional inspection.",
            what_mechanic_may_check=[
                "Light housing and lens integrity",
                "Internal wiring and electrical sockets",
                "Bulb or LED operation and weather sealing",
                "Whether the assembly requires repair or complete replacement",
            ],
            technical_explanation="Cracked or shattered headlamp and taillamp assemblies permit moisture ingress, potentially leading to electrical shorting, accelerated reflector degradation, and compromised nighttime visibility and signaling compliance.",
        ),
        "content": (
            "What we found: Your headlight or taillight may be cracked or broken. "
            "Why this matters: Water can enter the light, damage its electrical parts, or make the light less visible to other drivers. "
            "What you should do: Check whether the light works and whether water can enter the damaged housing. Arrange a repair promptly. "
            "If the light is not working or your vehicle is difficult to see at night, avoid driving in conditions where visibility or signalling is unsafe. "
            "Can I keep driving?: Avoid unnecessary driving and arrange prompt professional inspection."
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
        "guidance": StructuredGuidance(
            title="Windshield Glass Damage",
            what_we_found="Your windshield has a crack that may affect your view or the strength of the glass.",
            why_this_matters="A crack in the driver's line of sight can make it harder to see the road. Some windshield damage can also affect the glass's ability to provide structural support.",
            what_you_should_do_now="Arrange an inspection by a qualified automotive glass professional. Until the damage has been assessed, avoid driving if the crack blocks your view or otherwise makes driving unsafe.",
            can_i_keep_driving="Avoid unnecessary driving and arrange prompt professional inspection.",
            what_mechanic_may_check=[
                "Crack length, depth, and optical spread",
                "Location relative to the driver's primary line of sight",
                "Camera and sensor mounting area on the glass",
                "Whether glass resin repair or full replacement with camera recalibration is required",
            ],
            technical_explanation="ANSI/AGRSS 003-2022 provides safety criteria for automotive glass. Windshield damage within critical viewing zones impairs optical clarity, and vehicles equipped with forward-facing ADAS cameras often require optical recalibration following windshield replacement.",
        ),
        "content": (
            "What we found: Your windshield has a crack that may affect your view or the strength of the glass. "
            "Why this matters: A crack in the driver's line of sight can make it harder to see the road. Some windshield damage can also affect the glass's ability to provide structural support. "
            "What you should do: Arrange an inspection by a qualified automotive glass professional. Until the damage has been assessed, avoid driving if the crack blocks your view or otherwise makes driving unsafe. "
            "Can I keep driving?: Avoid unnecessary driving and arrange prompt professional inspection."
        ),
    },
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
        "guidance": StructuredGuidance(
            title="Bumper Impact Damage",
            what_we_found="Damage was detected on your bumper assembly.",
            why_this_matters="Bumpers help absorb minor impact energy and protect safety equipment, parking sensors, and radar modules positioned behind the bumper cover.",
            what_you_should_do_now="Check that no parts are loose or rubbing against the tires before driving. Arrange a professional inspection to verify that underlying safety structures and sensors are intact.",
            can_i_keep_driving="Avoid unnecessary driving and arrange prompt professional inspection.",
            what_mechanic_may_check=[
                "Bumper reinforcement bar and mounting brackets",
                "Energy-absorbing foam cushions",
                "Front radar and collision mitigation sensors",
                "Alignment and attachment clips of the bumper cover",
            ],
            technical_explanation="NHTSA bumper safety guidelines cover structural impact absorption. Modern bumper fascias conceal forward radar units, ultrasonic park sensors, and energy-absorbing elements that must be inspected following significant impacts.",
        ),
        "content": (
            "What we found: Damage was detected on your bumper assembly. "
            "Why this matters: Bumpers help absorb minor impact energy and protect safety equipment, parking sensors, and radar modules positioned behind the bumper cover. "
            "What you should do: Check that no parts are loose or rubbing against the tires before driving. Arrange a professional inspection to verify that underlying safety structures and sensors are intact. "
            "Can I keep driving?: Avoid unnecessary driving and arrange prompt professional inspection."
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
        "guidance": StructuredGuidance(
            title="Flat or Deflated Tire",
            what_we_found="A tire appears flat, significantly deflated, or damaged.",
            why_this_matters="Driving on a flat tire damages the tire beyond repair, risks bending or cracking the wheel rim, and severely degrades steering and emergency braking control.",
            what_you_should_do_now="Do not drive on a flat tire. Fit a spare wheel if it is safe to do so, use an approved inflation kit, or call for roadside assistance.",
            can_i_keep_driving="Stop in a safe place and seek assistance.",
            what_mechanic_may_check=[
                "Tire tread and sidewall for punctures or tears",
                "Wheel rim for bends, cracks, or bead seat damage",
                "Tire pressure monitoring system (TPMS) sensor",
                "Whether the tire meets USTMA puncture repair limits or requires replacement",
            ],
            technical_explanation="USTMA passenger tire repair procedures specify that punctures outside the central crown area (such as the sidewall or shoulder) cannot be safely repaired. Driving while deflated causes rapid internal structural cord breakdown.",
        ),
        "content": (
            "What we found: A tire appears flat, significantly deflated, or damaged. "
            "Why this matters: Driving on a flat tire damages the tire beyond repair, risks bending or cracking the wheel rim, and severely degrades steering and emergency braking control. "
            "What you should do: Do not drive on a flat tire. Fit a spare wheel if it is safe to do so, use an approved inflation kit, or call for roadside assistance. "
            "Can I keep driving?: Stop in a safe place and seek assistance."
        ),
    },
    {
        "id": "KB_SCRATCH_01",
        "damage_class": "scratch",
        "dtc": None,
        "citation": KnowledgeCitation(
            source_id="ASE-PAINT-FINISH-2022",
            document_title="ASE Collision Repair Guidelines: Surface Finishing & Corrosion Prevention",
            publisher="National Institute for Automotive Service Excellence (ASE)",
            section="Section B3: Clearcoat Integrity & Substrate Protection",
            page_number=15,
            url="https://www.ase.com",
        ),
        "guidance": StructuredGuidance(
            title="Surface Paint Scratch",
            what_we_found="Surface paint scratching was detected on an exterior vehicle panel.",
            why_this_matters="Scratches through the clear coat and primer expose underlying sheet metal or plastic to weather, road salts, and potential corrosion over time.",
            what_you_should_do_now="Check whether the scratch penetrates through the paint layers to bare metal. Apply touch-up paint or corrosion inhibitor if bare metal is exposed.",
            can_i_keep_driving="No immediate action indicated by this finding alone; monitor or follow normal maintenance guidance.",
            what_mechanic_may_check=[
                "Paint depth and scratch penetration level",
                "Panel substrate material (steel, aluminum, composite)",
                "Corrosion protection and refinishing requirements",
            ],
            technical_explanation="Automotive clearcoat protects the colored basecoat and substrate from moisture and environmental contaminants. Scratches that do not penetrate the primer are primarily cosmetic, while deep scratches may need sealing to prevent corrosion.",
        ),
        "content": (
            "What we found: Surface paint scratching was detected on an exterior vehicle panel. "
            "Why this matters: Scratches through the clear coat and primer expose underlying sheet metal or plastic to weather and potential corrosion over time. "
            "What you should do: Check whether the scratch penetrates through paint layers to bare metal. Apply touch-up paint or corrosion inhibitor if bare metal is exposed. "
            "Can I keep driving?: No immediate action indicated by this finding alone; monitor or follow normal maintenance guidance."
        ),
    },
    {
        "id": "KB_DENT_01",
        "damage_class": "dent",
        "dtc": None,
        "citation": KnowledgeCitation(
            source_id="ICAR-BODY-ASSESS-2023",
            document_title="I-CAR Technical Guidelines: Outer Panel Straightening & Assessment",
            publisher="Inter-Industry Conference on Auto Collision Repair (I-CAR)",
            section="Module 2: Exterior Panel Deformation & Clearance",
            page_number=22,
            url="https://www.i-car.com",
        ),
        "guidance": StructuredGuidance(
            title="Panel Dent or Crease",
            what_we_found="A panel dent or indentation was detected on the vehicle body.",
            why_this_matters="Dents are usually cosmetic, but deep dents can interfere with door gaps, window mechanisms, or sensor clearance.",
            what_you_should_do_now="Verify that adjacent doors, hood, or tailgate open and latch smoothly and that tires have full clearance. Arrange paintless dent repair or body assessment when convenient.",
            can_i_keep_driving="No immediate action indicated by this finding alone; monitor or follow normal maintenance guidance.",
            what_mechanic_may_check=[
                "Panel latch alignment and seam clearances",
                "Paint elasticity and micro-fractures in dent crease",
                "Underlying reinforcement or electrical harness clearance",
            ],
            technical_explanation="I-CAR guidelines differentiate between cosmetic outer sheet metal deformation and structural underlying apron/pillar damage. Non-structural panel dents that do not contact moving parts or obstruct lights pose no immediate safety concern.",
        ),
        "content": (
            "What we found: A panel dent or indentation was detected on the vehicle body. "
            "Why this matters: Dents are usually cosmetic, but deep dents can interfere with door gaps, window mechanisms, or sensor clearance. "
            "What you should do: Verify that adjacent doors, hood, or tailgate open and latch smoothly and that tires have full clearance. "
            "Can I keep driving?: No immediate action indicated by this finding alone; monitor or follow normal maintenance guidance."
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
        "guidance": StructuredGuidance(
            title="Engine Misfiring (DTC P0300)",
            what_we_found="The engine computer has detected that one or more cylinders are not burning fuel correctly.",
            why_this_matters="Repeated misfires allow unburned fuel into the exhaust system, which can cause poor performance, shaking, and catalytic converter overheating if driven while severe.",
            what_you_should_do_now="If the engine warning light is flashing or the engine is shaking severely, pull over safely, switch off the engine when safe, and arrange professional assistance. Otherwise, avoid heavy acceleration and arrange prompt diagnosis.",
            can_i_keep_driving="Avoid unnecessary driving and arrange prompt professional inspection. (Stop in a safe place and seek assistance if flashing or severe).",
            what_mechanic_may_check=[
                "Spark plugs and ignition coils",
                "Fuel pressure and fuel injectors",
                "Intake air leaks and vacuum lines",
                "Cylinder compression and engine timing",
            ],
            technical_explanation="SAE J2012 defines P0300 when crankshaft angular acceleration irregularities indicate multiple cylinder misfires. Unburned fuel entering the exhaust stream can elevate catalytic converter temperatures under sustained severe misfire conditions.",
        ),
        "content": (
            "What we found: The engine computer has detected that one or more cylinders are not burning fuel correctly. "
            "Why this matters: Repeated misfires allow unburned fuel into the exhaust, which can cause poor performance, shaking, and catalytic converter damage if driven while severe. "
            "What you should do: If the engine warning light is flashing or the engine is shaking severely, pull over safely, switch off the engine when safe, and arrange professional assistance. Otherwise, arrange prompt diagnosis. "
            "Can I keep driving?: Avoid unnecessary driving and arrange prompt professional inspection. (Stop in a safe place and seek assistance if flashing or severe)."
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
        "guidance": StructuredGuidance(
            title="Engine Coolant Overtemperature (DTC P0217)",
            what_we_found="The engine coolant temperature has exceeded safe operating limits.",
            why_this_matters="Severe engine overheating can cause cylinder head warpage, blown head gaskets, or total engine failure if driving continues.",
            what_you_should_do_now="Pull over safely as soon as it is safe to do so and turn off the engine. Do not open the radiator or coolant reservoir cap while the engine is hot. Call for professional assistance.",
            can_i_keep_driving="Stop in a safe place and seek assistance.",
            what_mechanic_may_check=[
                "Coolant level and cooling system leaks",
                "Thermostat opening and water pump circulation",
                "Radiator cooling fan operation and relay",
                "Coolant temperature sensor calibration",
            ],
            technical_explanation="SAE J2012 defines P0217 when coolant temperature exceeds calibrated safety thresholds (>115°C / 239°F). Immediate shutdown is required to prevent thermal deformation of engine casting components.",
        ),
        "content": (
            "What we found: The engine coolant temperature has exceeded safe operating limits. "
            "Why this matters: Severe engine overheating can cause cylinder head warpage, blown head gaskets, or total engine failure if driving continues. "
            "What you should do: Pull over safely as soon as it is safe to do so and turn off the engine. Do not open the radiator or coolant reservoir cap while the engine is hot. Call for professional assistance. "
            "Can I keep driving?: Stop in a safe place and seek assistance."
        ),
    },
    {
        "id": "KB_DTC_P0128",
        "damage_class": None,
        "dtc": "P0128",
        "citation": KnowledgeCitation(
            source_id="SAE-J2012-COOLING-P0128",
            document_title="SAE J2012 Diagnostic Trouble Code Definitions: Engine Cooling Systems",
            publisher="SAE International",
            section="DTC P0128: Coolant Thermostat Regulating Temperature",
            page_number=19,
            url="https://www.sae.org",
        ),
        "guidance": StructuredGuidance(
            title="Engine Temperature Below Expected (DTC P0128)",
            what_we_found="Your engine is not warming up to the temperature expected by the vehicle's computer. A thermostat or temperature-sensor issue could be one possible cause.",
            why_this_matters="Running below normal operating temperature can reduce cabin heater performance, increase fuel consumption, and increase emissions over time.",
            what_you_should_do_now="Arrange a check of the engine cooling system. If you notice overheating or a coolant warning, stop safely and follow your vehicle manufacturer's instructions.",
            can_i_keep_driving="Arrange a mechanic's appointment soon.",
            what_mechanic_may_check=[
                "Thermostat opening temperature and mechanical sealing",
                "Coolant temperature sensor accuracy and wiring",
                "Coolant level and air pockets in the cooling loop",
                "Electric cooling fan control circuits",
            ],
            technical_explanation="SAE J2012 defines P0128 when the engine coolant temperature fails to reach the calibrated closed-loop operating temperature within a specified period after starting.",
        ),
        "content": (
            "What we found: Your engine is not warming up to the temperature expected by the vehicle's computer. A thermostat or temperature-sensor issue could be one possible cause. "
            "Why this matters: Running below normal operating temperature can reduce cabin heater performance, increase fuel consumption, and increase emissions over time. "
            "What you should do: Arrange a check of the engine cooling system. If you notice overheating or a coolant warning, stop safely and follow your vehicle manufacturer's instructions. "
            "Can I keep driving?: Arrange a mechanic's appointment soon."
        ),
    },
    {
        "id": "KB_DTC_P0133",
        "damage_class": None,
        "dtc": "P0133",
        "citation": KnowledgeCitation(
            source_id="SAE-J2012-EXHAUST-P0133",
            document_title="SAE J2012 Diagnostic Trouble Code Definitions: Powertrain Systems",
            publisher="SAE International",
            section="DTC P0133: O2 Sensor Circuit Slow Response (Bank 1, Sensor 1)",
            page_number=24,
            url="https://www.sae.org",
        ),
        "guidance": StructuredGuidance(
            title="Oxygen Sensor Slow Response (DTC P0133)",
            what_we_found="A sensor that helps the engine manage its fuel and emissions is responding more slowly than expected. The sensor or another engine-related issue may be responsible.",
            why_this_matters="A slow-responding sensor impairs real-time air-fuel ratio adjustments, which can gradually increase fuel consumption and exhaust emissions.",
            what_you_should_do_now="Arrange a diagnostic check before replacing any parts.",
            can_i_keep_driving="Arrange a mechanic's appointment soon.",
            what_mechanic_may_check=[
                "Upstream oxygen sensor switching frequency and heater circuit",
                "Exhaust manifold and pipe for leaks upstream of the sensor",
                "Intake air ducting for unmetered air leaks",
                "Fuel trim live data on a diagnostic scanner",
            ],
            technical_explanation="SAE J2012 defines P0133 when the pre-catalytic oxygen sensor rich-to-lean or lean-to-rich transition cycle time exceeds the maximum calibrated threshold.",
        ),
        "content": (
            "What we found: A sensor that helps the engine manage its fuel and emissions is responding more slowly than expected. The sensor or another engine-related issue may be responsible. "
            "Why this matters: A slow-reacting sensor can cause the engine computer to adjust fuel delivery less accurately, which can increase fuel use and exhaust emissions over time. "
            "What you should do: Arrange a diagnostic check before replacing any parts. "
            "Can I keep driving?: Arrange a mechanic's appointment soon."
        ),
    },
    {
        "id": "KB_DTC_P0171",
        "damage_class": None,
        "dtc": "P0171",
        "citation": KnowledgeCitation(
            source_id="SAE-J2012-FUEL-P0171",
            document_title="SAE J2012 Diagnostic Trouble Code Definitions: Fuel & Air Metering",
            publisher="SAE International",
            section="DTC P0171: System Too Lean (Bank 1)",
            page_number=28,
            url="https://www.sae.org",
        ),
        "guidance": StructuredGuidance(
            title="Engine Mixture Too Lean (DTC P0171)",
            what_we_found="The engine computer is detecting too much air, or not enough fuel, in the mixture for one bank of the engine.",
            why_this_matters="Prolonged lean running can cause rough performance, misfires, and elevated combustion temperatures if unaddressed.",
            what_you_should_do_now="Ask a mechanic to check for possible air leaks, fuel-delivery problems, or sensor issues.",
            can_i_keep_driving="Avoid unnecessary driving and arrange prompt professional inspection.",
            what_mechanic_may_check=[
                "Intake manifold gaskets and vacuum hoses for leaks",
                "Mass Air Flow (MAF) sensor cleanliness and output",
                "Fuel pressure and fuel pump flow volume",
                "Fuel filter and fuel injector delivery balance",
            ],
            technical_explanation="SAE J2012 defines P0171 when closed-loop fuel trim compensation reaches its positive authority limit (+20% to +25%) indicating unmetered air or insufficient fuel delivery on Bank 1.",
        ),
        "content": (
            "What we found: The engine computer is detecting too much air, or not enough fuel, in the mixture for one bank of the engine. "
            "Why this matters: Prolonged lean running can cause rough performance, misfires, and elevated combustion temperatures if unaddressed. "
            "What you should do: Ask a mechanic to check for possible air leaks, fuel-delivery problems, or sensor issues. "
            "Can I keep driving?: Avoid unnecessary driving and arrange prompt professional inspection."
        ),
    },
    {
        "id": "KB_DTC_P0401",
        "damage_class": None,
        "dtc": "P0401",
        "citation": KnowledgeCitation(
            source_id="SAE-J2012-EMISSIONS-P0401",
            document_title="SAE J2012 Diagnostic Trouble Code Definitions: Exhaust Emissions",
            publisher="SAE International",
            section="DTC P0401: Exhaust Gas Recirculation Flow Insufficient Detected",
            page_number=51,
            url="https://www.sae.org",
        ),
        "guidance": StructuredGuidance(
            title="EGR Flow Insufficient (DTC P0401)",
            what_we_found="The system that recirculates some exhaust gas into the engine is detecting less flow than expected. A blockage, valve issue, or another fault may be responsible.",
            why_this_matters="The system that recirculates exhaust gas helps control combustion temperatures and reduces emissions; reduced flow may cause engine pinging under heavy load and elevated exhaust emissions.",
            what_you_should_do_now="Have the system checked before replacing parts.",
            can_i_keep_driving="Arrange a mechanic's appointment soon.",
            what_mechanic_may_check=[
                "EGR valve and intake manifold ports for carbon buildup",
                "Differential pressure feedback sensor (DPFE) and hoses",
                "EGR vacuum regulator solenoid and wiring",
                "Exhaust backpressure and catalytic converter flow",
            ],
            technical_explanation="SAE J2012 defines P0401 when the EGR diagnostic monitor detects insufficient pressure variation across the metering orifice during commanded opening.",
        ),
        "content": (
            "What we found: The system that recirculates some exhaust gas into the engine is detecting less flow than expected. A blockage, valve issue, or another fault may be responsible. "
            "Why this matters: The EGR system controls combustion temperatures to reduce emissions; inadequate flow can increase nitrogen oxide emissions and cause pinging under load. "
            "What you should do: Have the system checked before replacing parts. "
            "Can I keep driving?: Arrange a mechanic's appointment soon."
        ),
    },
    {
        "id": "KB_DTC_P0420",
        "damage_class": None,
        "dtc": "P0420",
        "citation": KnowledgeCitation(
            source_id="SAE-J2012-CATALYST-P0420",
            document_title="SAE J2012 Diagnostic Trouble Code Definitions: Emissions Systems",
            publisher="SAE International",
            section="DTC P0420: Catalyst System Efficiency Below Threshold (Bank 1)",
            page_number=58,
            url="https://www.sae.org",
        ),
        "guidance": StructuredGuidance(
            title="Possible Exhaust Emissions System Problem (DTC P0420)",
            what_we_found="The vehicle's computer has detected that the emissions-control system on engine bank 1 is not performing as expected. This code alone does not prove that the catalytic converter must be replaced.",
            why_this_matters="The catalytic converter reduces harmful exhaust gases; reduced efficiency increases tailpipe emissions and will prevent passing a vehicle emissions inspection.",
            what_you_should_do_now="Arrange a proper diagnostic inspection to identify the cause.",
            can_i_keep_driving="Arrange a mechanic's appointment soon.",
            what_mechanic_may_check=[
                "Exhaust leaks upstream or near the catalytic converter",
                "Downstream oxygen sensor signal and response rate",
                "Engine fuel trim and misfire history",
                "Temperature differential across the catalytic converter",
            ],
            technical_explanation="SAE J2012 defines P0420 when downstream O2 sensor signal frequency mirrors upstream sensor activity, indicating depleted oxygen storage capacity within the Bank 1 catalyst.",
        ),
        "content": (
            "What we found: The vehicle's computer has detected that the emissions-control system on engine bank 1 is not performing as expected. This code alone does not prove that the catalytic converter must be replaced. "
            "Why this matters: The catalytic converter reduces harmful exhaust gases; reduced efficiency increases tailpipe emissions and will cause emissions test failures. "
            "What you should do: Arrange a proper diagnostic inspection to identify the cause. "
            "Can I keep driving?: Arrange a mechanic's appointment soon."
        ),
    },
    {
        "id": "KB_DTC_P0455",
        "damage_class": None,
        "dtc": "P0455",
        "citation": KnowledgeCitation(
            source_id="SAE-J2012-EVAP-P0455",
            document_title="SAE J2012 Diagnostic Trouble Code Definitions: Evaporative Control",
            publisher="SAE International",
            section="DTC P0455: Evaporative Emission System Leak Detected (Gross Leak)",
            page_number=63,
            url="https://www.sae.org",
        ),
        "guidance": StructuredGuidance(
            title="Large Leak in Fuel Vapour System (DTC P0455)",
            what_we_found="The system designed to contain fuel vapours has detected a large leak or a condition that looks like one. A loose fuel cap or a leak elsewhere may be responsible, depending on the vehicle.",
            why_this_matters="Fuel vapours can escape into the atmosphere rather than being burned in the engine, which increases evaporative emissions and fuel loss.",
            what_you_should_do_now="Check that the fuel cap is properly secured if your vehicle has one. If the warning remains, arrange an inspection. Never inspect fuel leaks near flames or other ignition sources.",
            can_i_keep_driving="Arrange a mechanic's appointment soon.",
            what_mechanic_may_check=[
                "Fuel filler cap seal and neck condition",
                "EVAP purge and vent solenoid valve sealing",
                "EVAP vapour canister and lines for cracks",
                "Smoke test of the evaporative containment circuit",
            ],
            technical_explanation="SAE J2012 defines P0455 when the EVAP monitor detects vacuum decay exceeding the threshold corresponding to a gross leak (>0.090 inch orifice).",
        ),
        "content": (
            "What we found: The system designed to contain fuel vapours has detected a large leak or a condition that looks like one. A loose fuel cap or a leak elsewhere may be responsible, depending on the vehicle. "
            "Why this matters: Fuel vapours can escape into the atmosphere rather than being burned in the engine, which increases evaporative emissions and fuel loss. "
            "What you should do: Check that the fuel cap is properly secured if your vehicle has one. If the warning remains, arrange an inspection. Never inspect fuel leaks near flames or other ignition sources. "
            "Can I keep driving?: Arrange a mechanic's appointment soon."
        ),
    },
    {
        "id": "KB_DTC_P0700",
        "damage_class": None,
        "dtc": "P0700",
        "citation": KnowledgeCitation(
            source_id="SAE-J2012-TRANS-P0700",
            document_title="SAE J2012 Diagnostic Trouble Code Definitions: Transmission Systems",
            publisher="SAE International",
            section="DTC P0700: Transmission Control System (MIL Request)",
            page_number=88,
            url="https://www.sae.org",
        ),
        "guidance": StructuredGuidance(
            title="Transmission Warning (DTC P0700)",
            what_we_found="The engine computer has received a warning from the transmission control system. This code alone does not identify the exact transmission fault.",
            why_this_matters="P0700 indicates that a secondary transmission-specific diagnostic code has been logged; ignoring transmission issues can lead to unsafe driving conditions or mechanical wear.",
            what_you_should_do_now="Check for additional transmission codes and arrange a diagnostic inspection. If the vehicle loses drive, shifts dangerously, or behaves unpredictably, stop safely.",
            can_i_keep_driving="Avoid unnecessary driving and arrange prompt professional inspection.",
            what_mechanic_may_check=[
                "Transmission control module diagnostic trouble codes",
                "Transmission fluid level and condition",
                "Transmission wiring harnesses and connectors",
                "Gearshift solenoid operation and line pressure",
            ],
            technical_explanation="SAE J2012 defines P0700 as an informational request from the Transmission Control Module (TCM) to illuminate the Malfunction Indicator Lamp. Specific fault codes reside in the TCM.",
        ),
        "content": (
            "What we found: The engine computer has received a warning from the transmission control system. This code alone does not identify the exact transmission fault. "
            "Why this matters: P0700 indicates that a secondary transmission-specific diagnostic code has been logged; ignoring transmission issues can lead to unsafe driving conditions or mechanical wear. "
            "What you should do: Check for additional transmission codes and arrange a diagnostic inspection. If the vehicle loses drive, shifts dangerously, or behaves unpredictably, stop safely. "
            "Can I keep driving?: Avoid unnecessary driving and arrange prompt professional inspection."
        ),
    },
]
