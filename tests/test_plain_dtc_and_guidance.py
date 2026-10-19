"""Unit and integration tests for plain-English DTC explanations, safety guidance, and PDF rendering."""

import pytest
from ml.obd.dtc import lookup_dtc, extract_dtcs_from_text, SAE_DTC_DATABASE
from rag.retrieval import RAGKnowledgeEngine
from rag.source_registry import APPROVED_KNOWLEDGE_BASE
from reports.pdf_renderer import render_inspection_pdf


EXAMPLE_DTCS = ["P0128", "P0133", "P0171", "P0300", "P0401", "P0420", "P0455", "P0700"]


def test_all_eight_example_dtcs_have_verified_plain_english_definitions():
    """Verify all 8 codes from prompt have user-friendly fields and do not fall back to generic label."""
    for code in EXAMPLE_DTCS:
        entry = lookup_dtc(code)
        assert entry.code == code
        # Must not be generic fallback
        assert "Standard Diagnostic Trouble Code" not in entry.description
        assert "Standard Diagnostic Trouble Code" not in entry.simple_title
        # Must have simple title
        assert len(entry.simple_title) > 0
        # Must have plain English explanation (what it means)
        assert len(entry.what_it_means) > 20
        assert any(k in entry.what_it_means.lower() for k in ("computer", "engine", "sensor", "system", "fuel"))
        # Must have what you should do
        assert len(entry.what_you_should_do) > 0
        # Must have urgency and urgency label
        assert entry.urgency in ("informational", "schedule_check", "prompt_attention", "stop_safely")
        assert len(entry.urgency_label) > 0
        # Must have why it matters
        assert len(entry.why_it_matters) > 0
        # Must have technical details and verified source
        assert len(entry.technical_details) > 0
        assert "SAE" in entry.source
        # Must have possible symptoms (indicating may or may not occur)
        assert len(entry.what_you_might_notice) > 0
        # Must have limitations
        assert len(entry.limitations) > 0


def test_specific_code_explanations():
    """Verify specific required content for example codes."""
    # P0128: Engine warming up
    p0128 = lookup_dtc("P0128")
    assert "Expected Temperature" in p0128.simple_title
    assert "thermostat" in p0128.what_it_means.lower() or "temperature-sensor" in p0128.what_it_means.lower()
    assert "cooling system" in p0128.what_you_should_do.lower()

    # P0133: Oxygen sensor slow response
    p0133 = lookup_dtc("P0133")
    assert "Oxygen Sensor" in p0133.simple_title
    assert "slowly" in p0133.what_it_means.lower()

    # P0171: System too lean
    p0171 = lookup_dtc("P0171")
    assert "Too Lean" in p0171.simple_title
    assert "air" in p0171.what_it_means.lower()

    # P0300: Engine misfire (critical escalation preserved)
    p0300 = lookup_dtc("P0300")
    assert "Misfir" in p0300.simple_title
    assert p0300.severity == "critical"
    assert p0300.escalate_risk is True
    assert p0300.urgency == "stop_safely"

    # P0401: EGR flow
    p0401 = lookup_dtc("P0401")
    assert "Exhaust Gas Recirculation" in p0401.simple_title

    # P0420: Catalytic converter
    p0420 = lookup_dtc("P0420")
    assert "Exhaust Emissions" in p0420.simple_title
    assert "does not prove that the catalytic converter must be replaced" in p0420.what_it_means

    # P0455: Fuel vapour system
    p0455 = lookup_dtc("P0455")
    assert "Fuel Vapour" in p0455.simple_title
    assert "fuel cap" in p0455.what_it_means.lower() or "fuel cap" in p0455.what_you_should_do.lower()

    # P0700: Transmission
    p0700 = lookup_dtc("P0700")
    assert "Transmission" in p0700.simple_title
    assert "does not identify the exact transmission fault" in p0700.what_it_means


def test_unknown_dtc_fallback_is_honest_and_unfabricated():
    """Verify unknown DTC does not receive a fabricated explanation."""
    unknown = lookup_dtc("P9999")
    assert unknown.code == "P9999"
    assert "We recognize this as a diagnostic code, but we do not yet have a verified plain-English explanation for it" in unknown.what_it_means
    assert "qualified technician" in unknown.what_you_should_do.lower()
    assert unknown.system == "Powertrain"


def test_rag_guidance_structure_and_can_i_keep_driving_outcomes():
    """Verify RAG knowledge entries use one of the 4 approved driving outcomes."""
    valid_outcomes = {
        "Stop in a safe place and seek assistance.",
        "Avoid unnecessary driving and arrange prompt professional inspection.",
        "Arrange a mechanic's appointment soon.",
        "No immediate action indicated by this finding alone; monitor or follow normal maintenance guidance.",
    }

    engine = RAGKnowledgeEngine(top_k=10)
    res = engine.retrieve(
        damage_classes=["broken_light", "glass_crack", "bumper_smash", "flat_tire"],
        dtc_codes=["P0300", "P0128", "P0171", "P0420"]
    )

    assert len(res.passages) > 0
    for p in res.passages:
        assert p.guidance is not None
        assert len(p.guidance.what_we_found) > 0
        assert len(p.guidance.why_this_matters) > 0
        assert len(p.guidance.what_you_should_do_now) > 0
        # Check driving advice starts with one of the valid outcomes
        outcome_found = any(p.guidance.can_i_keep_driving.startswith(vo.rstrip(".")) for vo in valid_outcomes)
        assert outcome_found, f"Outcome '{p.guidance.can_i_keep_driving}' does not match standard driving outcomes"
        assert len(p.guidance.what_mechanic_may_check) > 0
        assert len(p.guidance.technical_explanation) > 0
        assert p.citation.source_id is not None
        assert p.citation.document_title is not None


def test_pdf_renderer_with_plain_english_dtcs_and_guidance(tmp_path):
    """Verify PDF rendering incorporates structured DTCs and plain-English guidance without error."""
    dtc_entries = [lookup_dtc(c).model_dump() for c in ["P0300", "P0171", "P0128"]]
    rag_engine = RAGKnowledgeEngine(top_k=2)
    rag_res = rag_engine.retrieve(damage_classes=["broken_light"], dtc_codes=["P0300"])

    report_payload = {
        "inspection_id": "test_plain_english_report",
        "generated_at": "2026-10-19T01:00:00Z",
        "overall": {"damage_detected": True, "assessment": "damaged", "summary": "Inspection complete."},
        "vehicle": {"make": "Toyota", "model": "Camry", "year": 2020, "mileage": 45000, "mileage_unit": "km"},
        "images": [],
        "severity": {"score": 0.42, "level": "moderate"},
        "risk": {
            "class": "unsafe",
            "summary": "Active critical DTC detected: P0300 Engine Misfiring.",
            "reason_codes": ["OBD_CRITICAL_DTC_ACTIVE"],
        },
        "obd": {
            "status": "completed",
            "anomaly_detected": True,
            "flagged_pids": [{"pid_name": "COOLANT_TEMP", "observed_value": 110.0, "unit": "°C", "reason": "High"}],
            "dtcs": dtc_entries,
        },
        "knowledge": {
            "status": "completed",
            "citations": [c.model_dump() for c in rag_res.citations],
            "passages": [p.model_dump() for p in rag_res.passages],
            "summary_guidance": rag_res.summary_guidance,
        },
        "disclaimer": "AI-assisted decision support only.",
    }

    pdf_out = tmp_path / "plain_report.pdf"
    pdf_bytes = render_inspection_pdf(report_payload, output_target=pdf_out)

    assert len(pdf_bytes) > 2000
    assert pdf_out.is_file()
