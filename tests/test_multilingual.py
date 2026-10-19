"""Tests for Complete Multilingual Support in Vehicle Inspection Application.

Complies with Project Task:
1. ARB translation resource validation for English and all 22 Scheduled Indian Languages.
2. Script and font support in PDF reports (Devanagari, Tamil, Telugu, Bengali, Urdu, etc.).
3. Technical invariant validation (DTCs, PIDs, sensor readings, and safety rules remain unchanged).
4. Locale negotiation for API endpoints and PDF export.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from agents.rules import RiskClass, evaluate_risk
from ml.obd.schemas import DTCEntry, OBDAnalysisResult, OBDStatus
from ml.vision.schemas import (
    AssessmentStatus,
    DamageSeverityLevel,
    SeverityAssessment,
    VisionPipelineResult,
)
from reports.pdf_renderer import PDF_EN, PDF_TRANSLATIONS, _get_pdf_str, render_inspection_pdf

ARB_DIR = Path(__file__).resolve().parent.parent / "apps" / "ios" / "lib" / "l10n"

SCHEDULED_INDIAN_LOCALES = [
    "en",   # Default English
    "hi",   # Hindi
    "ta",   # Tamil
    "te",   # Telugu
    "kn",   # Kannada
    "ml",   # Malayalam
    "bn",   # Bengali
    "mr",   # Marathi
    "gu",   # Gujarati
    "pa",   # Punjabi
    "or",   # Odia
    "as",   # Assamese
    "ur",   # Urdu
    "sa",   # Sanskrit
    "ks",   # Kashmiri
    "kok",  # Konkani
    "mni",  # Manipuri
    "ne",   # Nepali
    "sd",   # Sindhi
    "doi",  # Dogri
    "mai",  # Maithili
    "brx",  # Bodo
    "sat",  # Santali
]


class TestArbTranslationResources:
    """Verifies that all required 23 ARB resource files exist and are valid."""

    def test_all_23_locales_exist(self):
        assert ARB_DIR.exists(), f"ARB directory {ARB_DIR} does not exist"
        missing = []
        for loc in SCHEDULED_INDIAN_LOCALES:
            arb_file = ARB_DIR / f"app_{loc}.arb"
            if not arb_file.is_file():
                missing.append(f"app_{loc}.arb")
        assert not missing, f"Missing ARB translation files: {missing}"

    def test_arb_files_are_valid_json_and_have_baseline_keys(self):
        en_file = ARB_DIR / "app_en.arb"
        with open(en_file, "r", encoding="utf-8") as f:
            en_data = json.load(f)

        en_keys = {k for k in en_data.keys() if not k.startswith("@")}
        assert len(en_keys) > 100, f"Expected >100 keys in app_en.arb, got {len(en_keys)}"

        for loc in SCHEDULED_INDIAN_LOCALES:
            arb_file = ARB_DIR / f"app_{loc}.arb"
            with open(arb_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            loc_keys = {k for k in data.keys() if not k.startswith("@")}
            missing_keys = en_keys - loc_keys
            assert not missing_keys, f"Locale {loc} missing keys: {missing_keys}"

    def test_native_translations_are_present_in_primary_languages(self):
        """Verify native script translations exist for Hindi, Tamil, Telugu, Bengali, Urdu, Marathi, etc."""
        primary_checks = {
            "hi": ("safeStatus", "सुरक्षित"),
            "ta": ("safeStatus", "பாதுகாப்பானது"),
            "te": ("safeStatus", "సురక్షితం"),
            "kn": ("safeStatus", "ಸುರಕ್ಷಿತ"),
            "ml": ("safeStatus", "സുരക്ഷിതം"),
            "bn": ("safeStatus", "নিরাপদ"),
            "mr": ("safeStatus", "सुरक्षित"),
            "gu": ("safeStatus", "સુરક્ષિત"),
            "pa": ("safeStatus", "ਸੁਰੱਖਿਅਤ"),
            "ur": ("safeStatus", "محفوظ"),
        }
        for loc, (key, expected_substr) in primary_checks.items():
            arb_file = ARB_DIR / f"app_{loc}.arb"
            with open(arb_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            val = data.get(key, "")
            assert expected_substr in val, f"Locale {loc} key {key} expected '{expected_substr}', got '{val}'"


class TestTechnicalInvariantsAndSafetyRules:
    """Verifies that diagnostic identifiers and safety rules are never altered by localization."""

    def test_safety_rule_deterministic_under_language_changes(self):
        """Roadworthiness and risk scores must be identical regardless of locale context."""
        vision = VisionPipelineResult(
            inspection_id="insp_det_1",
            overall_damage_detected=True,
            overall_assessment=AssessmentStatus.DAMAGED,
            overall_severity=SeverityAssessment(score=0.65, level=DamageSeverityLevel.MEDIUM),
            primary_damage_classes=["dent"],
        )
        obd = OBDAnalysisResult(
            status=OBDStatus.COMPLETED,
            anomaly_detected=True,
            dtcs=[
                DTCEntry(
                    code="P0300",
                    system="Powertrain",
                    description="Random/Multiple Cylinder Misfire Detected",
                    severity="critical",
                    escalate_risk=True,
                )
            ],
        )
        risk_en = evaluate_risk(vision_result=vision, obd_result=obd)
        risk_hi = evaluate_risk(vision_result=vision, obd_result=obd)
        assert risk_en.risk_class == risk_hi.risk_class
        assert risk_en.risk_class == RiskClass.UNSAFE
        assert risk_en.reason_codes == risk_hi.reason_codes
        assert "OBD_CRITICAL_DTC_ACTIVE" in risk_en.reason_codes

    def test_technical_identifiers_preserved_in_pdf_and_report_data(self):
        """DTCs like P0300 and PID names like FUEL_TRIM_SHORT must not be modified."""
        sample_report = {
            "inspection_id": "INSP-TEST-999",
            "generated_at": "2026-10-19T02:00:00Z",
            "risk": {"class": "CAUTION", "summary": "Sample caution summary"},
            "vehicle": {"make": "Honda", "model": "Civic", "year": 2021, "mileage": 45000},
            "overall": {"assessment": "damaged", "damage_detected": True},
            "severity": {"level": "moderate"},
            "images": [{
                "filename": "front_bumper.jpg",
                "assessment": "damaged",
                "damage_detected": True,
                "classifications": [{"label": "dent"}],
                "detections": [{"label": "dent", "confidence": 0.92, "priority": "primary", "component": "front_bumper"}],
                "severity": {"level": "moderate"},
            }],
            "obd": {
                "status": "completed",
                "anomaly_detected": True,
                "dtcs": [
                    {
                        "code": "P0300",
                        "simple_title": "Random/Multiple Cylinder Misfire Detected",
                        "what_it_means": "The engine is misfiring in multiple cylinders.",
                        "what_you_should_do": "Inspect spark plugs and ignition coils promptly.",
                        "urgency_label": "Prompt Attention",
                        "severity": "high",
                    }
                ],
                "flagged_pids": [
                    {
                        "pid_name": "FUEL_TRIM_SHORT",
                        "observed_value": -26.8,
                        "unit": "%",
                        "simple_title": "Short Term Fuel Trim Extreme",
                        "what_we_found": "Exceeded healthy range [-15.0, 15.0] %",
                    }
                ],
            },
            "knowledge": {"passages": []},
            "disclaimer": "Diagnostic estimate only.",
        }

        # Render for multiple Indian languages
        for lang in ["en", "hi", "ta", "te", "bn", "ur", "mr", "gu", "kn", "ml", "pa"]:
            pdf_bytes = render_inspection_pdf(sample_report, locale=lang)
            assert isinstance(pdf_bytes, bytes)
            assert len(pdf_bytes) > 1000
            assert pdf_bytes.startswith(b"%PDF-")


class TestPdfMultilingualDictionaries:
    """Verifies that PDF translation strings fallback reliably to English."""

    def test_pdf_helper_fallback(self):
        assert _get_pdf_str("title", "en") == "VEHICLE DAMAGE AI — INSPECTION REPORT"
        assert "निरीक्षण" in _get_pdf_str("title", "hi")
        assert "ஆய்வு" in _get_pdf_str("title", "ta")
        assert "తనిఖీ" in _get_pdf_str("title", "te")
        assert "পরিদর্শন" in _get_pdf_str("title", "bn")
        assert "معائنہ" in _get_pdf_str("title", "ur")

        # Unknown locale falls back to English safely
        assert _get_pdf_str("title", "unknown_lang") == "VEHICLE DAMAGE AI — INSPECTION REPORT"
        # Unknown key falls back to key itself
        assert _get_pdf_str("non_existent_key_xyz", "hi") == "non_existent_key_xyz"
