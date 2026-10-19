"""Automotive Inspection PDF Report Renderer.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 14.3 and Master Prompt Step 11.
Renders publication-ready, printable PDF reports with ReportLab.
Includes executive summary, risk banner, damage tables, OBD findings,
grounded repair guidance with citations, and safety disclaimers.
"""

from __future__ import annotations

import io
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

_FONTS_INITIALIZED = False
_ACTIVE_UNICODE_FONT = "Helvetica"


def _init_pdf_fonts() -> str:
    """Register system TrueType fonts supporting Indian Unicode scripts on macOS/Linux."""
    global _FONTS_INITIALIZED, _ACTIVE_UNICODE_FONT
    if _FONTS_INITIALIZED:
        return _ACTIVE_UNICODE_FONT

    font_candidates = [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/DevanagariMT.ttc",
        "/System/Library/Fonts/Supplemental/DevanagariMT.ttc",
    ]

    for fp in font_candidates:
        if os.path.exists(fp):
            try:
                if fp.endswith(".ttc"):
                    pdfmetrics.registerFont(TTFont("ArialUnicode", fp, subfontIndex=0))
                else:
                    pdfmetrics.registerFont(TTFont("ArialUnicode", fp))
                _ACTIVE_UNICODE_FONT = "ArialUnicode"
                _FONTS_INITIALIZED = True
                return _ACTIVE_UNICODE_FONT
            except Exception:
                continue

    _FONTS_INITIALIZED = True
    return "Helvetica"


PDF_EN: Dict[str, str] = {
    "title": "VEHICLE DAMAGE AI — INSPECTION REPORT",
    "inspection_id": "Inspection ID",
    "generated": "Generated",
    "risk_assessment": "RISK ASSESSMENT",
    "vehicle": "Vehicle",
    "mileage": "Mileage",
    "damage_detected": "Damage Detected",
    "severity_level": "Severity Level",
    "sec1_vision": "1. Exterior Computer Vision Findings",
    "sec2_obd": "2. OBD-II Telemetry & Diagnostic Codes",
    "sec3_guidance": "3. Verified Repair & Safety Guidance",
    "status": "Status",
    "anomaly_flagged": "Anomaly Flagged",
    "flagged_sensors": "Flagged Sensors",
    "active_dtcs": "Active DTC Codes",
    "dtc_explanations": "Diagnostic Trouble Code Explanations",
    "urgency": "Urgency",
    "what_it_means": "What it means",
    "what_you_should_do": "What you should do",
    "possible_symptoms": "Possible symptoms",
    "why_it_matters": "Why it matters",
    "limitations": "Notice / Limitations",
    "tech_reference": "Technical Reference",
    "reading": "Reading",
    "what_we_found": "What we found",
    "what_reading_means": "What does this reading mean?",
    "sample_analysis": "Sample Analysis",
    "possible_explanations": "Possible explanations (possibilities to investigate)",
    "driving_advice": "Can I keep driving?",
    "mechanic_checks": "What the mechanic may check",
    "notice": "Notice",
    "yes": "YES",
    "no": "NO",
    "none": "None",
    "col_image_file": "Image File",
    "col_damage_detected": "Damage Detected",
    "col_primary_finding": "Primary Finding",
    "col_all_classes": "All Classes",
    "col_detections": "Detections",
    "col_severity": "Severity",
    "no_images": "No images were provided or analyzed.",
    "no_obd": "No OBD-II telemetry log provided with this inspection.",
    "no_guidance": "No verified guidance available.",
    "flagged_sensor_explanations": "Flagged Telemetry Sensor Explanations",
    "sec4_estimate": "4. Indicative Vehicle Repair & Replacement Cost Estimate",
    "no_estimate": "No repair cost estimate generated for this inspection.",
    "estimate_comparison": "Repair (Scenario A) vs. Replacement (Scenario B) Comparison",
    "scenario_repair": "Scenario A: Component Repair & Refinish",
    "scenario_replace": "Scenario B: Complete Replacement",
    "recommended": "RECOMMENDED",
    "expected_cost": "Expected Cost",
    "cost_range": "Cost Range (Min - Max)",
    "itemized_breakdown": "Itemized Cost Breakdown (Recommended Action)",
    "sources_provenance": "Genuine Indian Market Parts Sources & Provenance",
    "category": "Category",
    "description": "Description / Operation",
    "amount": "Amount (INR)",
    "disclaimer_cost": "Notice: Indicative estimate based on visible damage and active Indian market parts catalogues. Concealed internal defects require physical teardown. Roadworthiness rules remain independent of financial repair choices.",
}

PDF_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "hi": {
        "title": "वाहन क्षति एआई — निरीक्षण रिपोर्ट",
        "inspection_id": "निरीक्षण आईडी",
        "generated": "तैयार किया गया",
        "risk_assessment": "जोखिम मूल्यांकन",
        "vehicle": "वाहन",
        "mileage": "माइलेज",
        "damage_detected": "क्षति की पहचान",
        "severity_level": "गंभीरता स्तर",
        "sec1_vision": "1. बाहरी कंप्यूटर विज़न निष्कर्ष",
        "sec2_obd": "2. ओबीडी-II टेलीमेट्री एवं डायग्नोस्टिक कोड",
        "sec3_guidance": "3. सत्यापित मरम्मत एवं सुरक्षा मार्गदर्शन",
        "status": "स्थिति",
        "anomaly_flagged": "असामान्यता चिह्नित",
        "flagged_sensors": "चिह्नित सेंसर",
        "active_dtcs": "सक्रिय डीटीसी कोड",
        "dtc_explanations": "डायग्नोस्टिक ट्रबल कोड विवरण",
        "urgency": "आवश्यकता स्तर",
        "what_it_means": "इसका क्या अर्थ है",
        "what_you_should_do": "आपको क्या करना चाहिए",
        "possible_symptoms": "संभावित लक्षण",
        "why_it_matters": "यह क्यों महत्वपूर्ण है",
        "limitations": "सीमाएं एवं सूचना",
        "tech_reference": "तकनीकी संदर्भ",
        "reading": "रीडिंग",
        "what_we_found": "जांच में क्या मिला",
        "what_reading_means": "इस रीडिंग का क्या अर्थ है?",
        "sample_analysis": "नमूना विश्लेषण",
        "possible_explanations": "संभावित कारण",
        "driving_advice": "क्या गाड़ी चलाना जारी रख सकते हैं?",
        "mechanic_checks": "मैकेनिक को क्या जांचना चाहिए",
        "notice": "सूचना",
        "yes": "हाँ",
        "no": "नहीं",
        "none": "कोई नहीं",
        "col_image_file": "इमेज फ़ाइल",
        "col_damage_detected": "क्षति का पता चला",
        "col_primary_finding": "प्राथमिक निष्कर्ष",
        "col_all_classes": "सभी श्रेणियां",
        "col_detections": "पहचान संख्या",
        "col_severity": "गंभीरता",
        "no_images": "कोई इमेज उपलब्ध नहीं कराई गई।",
        "no_obd": "इस निरीक्षण के साथ कोई ओबीडी-II लॉग प्रदान नहीं किया गया।",
        "no_guidance": "सत्यापित मार्गदर्शन उपलब्ध नहीं है।",
        "flagged_sensor_explanations": "चिह्नित टेलीमेट्री सेंसर विवरण",
    },
    "ta": {
        "title": "வாகன சேத AI — ஆய்வு அறிக்கை",
        "inspection_id": "ஆய்வு ஐடி",
        "generated": "உருவாக்கப்பட்டது",
        "risk_assessment": "பாதுகாப்பு இடர் மதிப்பீடு",
        "vehicle": "வாகனம்",
        "mileage": "மைலேஜ்",
        "damage_detected": "சேதம் கண்டறியப்பட்டது",
        "severity_level": "தீவிரத்தன்மை நிலை",
        "sec1_vision": "1. வெளிப்புற கணினி பார்வை கண்டுபிடிப்புகள்",
        "sec2_obd": "2. OBD-II சென்சார் & தவறு குறியீடுகள்",
        "sec3_guidance": "3. சரிபார்க்கப்பட்ட பழுது & பாதுகாப்பு வழிகாட்டுதல்",
        "status": "நிலை",
        "anomaly_flagged": "முரண்பாடு குறிக்கப்பட்டது",
        "flagged_sensors": "குறிக்கப்பட்ட சென்சார்கள்",
        "active_dtcs": "செயலில் உள்ள DTC குறியீடுகள்",
        "dtc_explanations": "தவறு குறியீடு விளக்கங்கள்",
        "urgency": "அவசரம்",
        "what_it_means": "இதன் பொருள் என்ன",
        "what_you_should_do": "நீங்கள் என்ன செய்ய வேண்டும்",
        "possible_symptoms": "சாத்தியமான அறிகுறிகள்",
        "why_it_matters": "இது ஏன் முக்கியம்",
        "limitations": "வரம்புகள் மற்றும் அறிவிப்பு",
        "tech_reference": "தொழில்நுட்ப குறிப்பு",
        "reading": "அளவீடு",
        "what_we_found": "நாங்கள் கண்டறிந்தது",
        "what_reading_means": "இந்த அளவீட்டின் பொருள் என்ன?",
        "sample_analysis": "மாதிரி பகுப்பாய்வு",
        "possible_explanations": "சாத்தியமான காரணங்கள்",
        "driving_advice": "தொடர்ந்து வாகனம் ஓட்டலாமா?",
        "mechanic_checks": "மெக்கானிக் பரிசோதிக்க வேண்டியவை",
        "notice": "அறிவிப்பு",
        "yes": "ஆம்",
        "no": "இல்லை",
        "none": "எதுவுமில்லை",
        "col_image_file": "படக் கோப்பு",
        "col_damage_detected": "சேதம் கண்டறியப்பட்டது",
        "col_primary_finding": "முதன்மைக் கண்டுபிடிப்பு",
        "col_all_classes": "அனைத்து பிரிவுகள்",
        "col_detections": "கண்டறிதல்கள்",
        "col_severity": "தீவிரம்",
        "no_images": "படங்கள் எதுவும் பகுப்பாய்வு செய்யப்படவில்லை.",
        "no_obd": "இந்த ஆய்வில் OBD-II பதிவு இணைக்கப்படவில்லை.",
        "no_guidance": "சரிபார்க்கப்பட்ட வழிகாட்டுதல் கிடைக்கவில்லை.",
        "flagged_sensor_explanations": "குறிக்கப்பட்ட சென்சார் விளக்கங்கள்",
    },
    "te": {
        "title": "వాహన నష్టం AI — తనిఖీ నివేదిక",
        "inspection_id": "తనిఖీ ID",
        "generated": "రూపొందించబడింది",
        "risk_assessment": "ప్రమాద అంచనా",
        "vehicle": "వాహనం",
        "mileage": "మైలేజ్",
        "damage_detected": "నష్టం కనుగొనబడింది",
        "severity_level": "తీవ్రత స్థాయి",
        "sec1_vision": "1. బాహ్య కంప్యూటర్ విజన్ ఫలితాలు",
        "sec2_obd": "2. OBD-II టెలిమెట్రీ & డయాగ్నస్టిక్ కోడ్‌లు",
        "sec3_guidance": "3. ధృవీకరించబడిన మరమ్మతు & భద్రతా మార్గదర్శకత్వం",
        "status": "స్థితి",
        "anomaly_flagged": "అసాధారణత గుర్తించబడింది",
        "flagged_sensors": "గుర్తించబడిన సెన్సార్లు",
        "active_dtcs": "క్రియాశీల DTC కోడ్‌లు",
        "dtc_explanations": "డయాగ్నస్టిక్ కోడ్ వివరణలు",
        "urgency": "అవసరత",
        "what_it_means": "దీని అర్థం ఏమిటి",
        "what_you_should_do": "మీరు ఏమి చేయాలి",
        "possible_symptoms": "సాధ్యమయ్యే లక్షణాలు",
        "why_it_matters": "ఇది ఎందుకు ముఖ్యం",
        "limitations": "పరిమితులు & నోటీసు",
        "tech_reference": "సాంకేతిక సూచన",
        "reading": "రీడింగ్",
        "what_we_found": "మేము కనుగొన్నది",
        "what_reading_means": "ఈ రీడింగ్ అర్థం ఏమిటి?",
        "sample_analysis": "నమూనా విశ్లేషణ",
        "possible_explanations": "సాధ్యమైన కారణాలు",
        "driving_advice": "డ్రైవింగ్ కొనసాగించవచ్చా?",
        "mechanic_checks": "మెకానిక్ తనిఖీ చేయవలసినవి",
        "notice": "గమనిక",
        "yes": "అవును",
        "no": "కాదు",
        "none": "ఏదీ లేదు",
        "col_image_file": "ఇమేజ్ ఫైల్",
        "col_damage_detected": "నష్టం గుర్తించబడింది",
        "col_primary_finding": "ప్రాథమిక ఫలితం",
        "col_all_classes": "అన్ని రకాలు",
        "col_detections": "గుర్తింపులు",
        "col_severity": "తీవ్రత",
        "no_images": "చిత్రాలు ఏవీ అందించబడలేదు.",
        "no_obd": "ఈ తనిఖీతో OBD-II లాగ్ అందించబడలేదు.",
        "no_guidance": "ధృవీకరించబడిన మార్గదర్శకత్వం అందుబాటులో లేదు.",
        "flagged_sensor_explanations": "గుర్తించబడిన సెన్సార్ వివరణలు",
    },
    "bn": {
        "title": "যানবাহন ক্ষতি এআই — পরিদর্শন রিপোর্ট",
        "inspection_id": "পরিদর্শন আইডি",
        "generated": "তৈরি হয়েছে",
        "risk_assessment": "ঝুঁকি মূল্যায়ন",
        "vehicle": "যানবাহন",
        "mileage": "মাইলেজ",
        "damage_detected": "ক্ষতি শনাক্ত হয়েছে",
        "severity_level": "তীব্রতা স্তর",
        "sec1_vision": "1. বাহ্যিক কম্পিউটার ভিশন ফলাফল",
        "sec2_obd": "2. ওবিডি-II টেলিমেট্রি এবং ডায়াগনস্টিক কোড",
        "sec3_guidance": "3. যাচাইকৃত মেরামত ও নিরাপত্তা নির্দেশিকা",
        "status": "অবস্থা",
        "anomaly_flagged": "অসঙ্গতি চিহ্নিত",
        "flagged_sensors": "চিহ্নিত সেন্সর",
        "active_dtcs": "সক্রিয় ডিটিসি কোড",
        "dtc_explanations": "ডায়াগনস্টিক ট্রাবল কোড ব্যাখ্যা",
        "urgency": "জরুরিতা",
        "what_it_means": "এর অর্থ কি",
        "what_you_should_do": "আপনার কি করা উচিত",
        "possible_symptoms": "সম্ভাব্য লক্ষণ",
        "why_it_matters": "এটি কেন গুরুত্বপূর্ণ",
        "limitations": "সীমাবদ্ধতা ও নোটিশ",
        "tech_reference": "প্রযুক্তিগত রেফারেন্স",
        "reading": "রিডিং",
        "what_we_found": "আমরা যা পেয়েছি",
        "what_reading_means": "এই রিডিং এর অর্থ কি?",
        "sample_analysis": "নমুনা বিশ্লেষণ",
        "possible_explanations": "সম্ভাব্য কারণ",
        "driving_advice": "গাড়ি চালানো কি নিরাপদ?",
        "mechanic_checks": "মেকানিকের কি পরীক্ষা করা উচিত",
        "notice": "বিজ্ঞপ্তি",
        "yes": "হ্যাঁ",
        "no": "না",
        "none": "কোনোটি নয়",
        "col_image_file": "ইমেজ ফাইল",
        "col_damage_detected": "ক্ষতি ধরা পড়েছে",
        "col_primary_finding": "প্রাথমিক অনুসন্ধান",
        "col_all_classes": "সমস্ত শ্রেণি",
        "col_detections": "শনাক্তকরণ",
        "col_severity": "তীব্রতা",
        "no_images": "কোনো ছবি সরবরাহ করা হয়নি।",
        "no_obd": "এই পরিদর্শনে কোনো OBD-II লগ নেই।",
        "no_guidance": "যাচাইকৃত নির্দেশিকা উপলব্ধ নেই।",
        "flagged_sensor_explanations": "চিহ্নিত সেন্সরের ব্যাখ্যা",
    },
    "ur": {
        "title": "گاڑی کے نقصان کا اے آئی معائنہ رپورٹ",
        "inspection_id": "معائنہ شناختی نمبر",
        "generated": "تاریخ تیاری",
        "risk_assessment": "خطرے کا جائزہ",
        "vehicle": "گاڑی",
        "mileage": "مائلیج",
        "damage_detected": "نقصان کی شناخت",
        "severity_level": "شدت کی سطح",
        "sec1_vision": "1. بیرونی کمپیوٹر وژن نتائج",
        "sec2_obd": "2. او بی ڈی ٹیلی میٹری اور تشخیصی کوڈز",
        "sec3_guidance": "3. تصدیق شدہ مرمت اور حفاظتی رہنمائی",
        "status": "حیثیت",
        "anomaly_flagged": "خرابی نشان زد",
        "flagged_sensors": "نشان زدہ سینسرز",
        "active_dtcs": "فعال ڈی ٹی سی کوڈز",
        "dtc_explanations": "تشخیصی کوڈز کی وضاحت",
        "urgency": "فوری ضرورت",
        "what_it_means": "اس کا کیا مطلب ہے",
        "what_you_should_do": "آپ کو کیا کرنا چاہیے",
        "possible_symptoms": "ممکنہ علامات",
        "why_it_matters": "یہ کیوں اہم ہے",
        "limitations": "حدود اور نوٹس",
        "tech_reference": "تکنیکی حوالہ",
        "reading": "ریڈنگ",
        "what_we_found": "ہمیں کیا ملا",
        "what_reading_means": "اس ریڈنگ کا کیا مطلب ہے؟",
        "sample_analysis": "نمونہ تجزیہ",
        "possible_explanations": "ممکنہ وجوہات",
        "driving_advice": "کیا گاڑی چلانا محفوظ ہے؟",
        "mechanic_checks": "مکینک کو کیا چیک کرنا چاہیے",
        "notice": "اطلاع",
        "yes": "ہاں",
        "no": "نہیں",
        "none": "کوئی نہیں",
        "col_image_file": "تصویر فائل",
        "col_damage_detected": "نقصان کی شناخت",
        "col_primary_finding": "بنیادی دریافت",
        "col_all_classes": "تمام اقسام",
        "col_detections": "تعداد",
        "col_severity": "شدت",
        "no_images": "کوئی تصویر فراہم نہیں کی گئی۔",
        "no_obd": "او بی ڈی لاگ موجود نہیں۔",
        "no_guidance": "کوئی رہنمائی دستیاب نہیں۔",
        "flagged_sensor_explanations": "نشان زدہ سینسرز کی وضاحت",
    },
    "mr": {
        "title": "वाहन नुकसान एआय — तपासणी अहवाल",
        "inspection_id": "तपासणी आयडी",
        "generated": "तयार केले",
        "risk_assessment": "धोका मूल्यांकन",
        "vehicle": "वाहन",
        "mileage": "मायलेज",
        "damage_detected": "नुकसान आढळले",
        "severity_level": "तीव्रता पातळी",
        "sec1_vision": "1. बाह्य संगणक दृष्टी निष्कर्ष",
        "sec2_obd": "2. ओबीडी-II सेन्सर आणि दोष कोड",
        "sec3_guidance": "3. पडताळणी केलेले दुरुस्ती आणि सुरक्षा मार्गदर्शन",
        "status": "स्थिती",
        "anomaly_flagged": "विसंगती आढळली",
        "flagged_sensors": "चिन्हांकित सेन्सर्स",
        "active_dtcs": "सक्रिय डीटीसी कोड",
        "dtc_explanations": "दोष कोड तपशील",
        "urgency": "तातडीची गरज",
        "what_it_means": "याचा अर्थ काय",
        "what_you_should_do": "तुम्ही काय करावे",
        "possible_symptoms": "संभाव्य लक्षणे",
        "why_it_matters": "हे का महत्त्वाचे आहे",
        "limitations": "मर्यादा आणि सूचना",
        "tech_reference": "तांत्रिक संदर्भ",
        "reading": "रीडिंग",
        "what_we_found": "आम्हाला काय आढळले",
        "what_reading_means": "या रीडिंगचा अर्थ काय आहे?",
        "sample_analysis": "नमुना विश्लेषण",
        "possible_explanations": "संभाव्य कारणे",
        "driving_advice": "गाडी चालवणे सुरक्षित आहे का?",
        "mechanic_checks": "मेकॅनिकने काय तपासावे",
        "notice": "सूचना",
        "yes": "होय",
        "no": "नाही",
        "none": "काही नाही",
    },
    "gu": {
        "title": "વાહન નુકસાન AI — નિરીક્ષણ અહેવાલ",
        "inspection_id": "નિરીક્ષણ ID",
        "generated": "તૈયાર કરેલ",
        "risk_assessment": "જોખમ મૂલ્યાંકન",
        "vehicle": "વાહન",
        "mileage": "માઇલેજ",
        "damage_detected": "નુકસાન મળ્યું",
        "severity_level": "ગંભીરતા સ્તર",
        "sec1_vision": "1. બાહ્ય કમ્પ્યુટર વિઝન તારણો",
        "sec2_obd": "2. OBD-II સેન્સર્સ અને ફોલ્ટ કોડ્સ",
        "sec3_guidance": "3. ચકાસાયેલ સમારકામ અને સુરક્ષા માર્ગદર્શન",
        "status": "સ્થિતિ",
        "anomaly_flagged": "ખામી ચિહ્નિત",
        "flagged_sensors": "ચિહ્નિત સેન્સર્સ",
        "active_dtcs": "સક્રિય DTC કોડ્સ",
        "dtc_explanations": "ફોલ્ટ કોડ સમજૂતી",
        "urgency": "તાકીદ",
        "what_it_means": "આનો અર્થ શું છે",
        "what_you_should_do": "તમારે શું કરવું જોઈએ",
        "possible_symptoms": "સંભવિત લક્ષણો",
        "why_it_matters": "આ શા માટે મહત્વપૂર્ણ છે",
        "limitations": "મર્યાદાઓ અને સૂચના",
        "tech_reference": "તકનીકી સંદર્ભ",
        "reading": "વાંચન",
        "what_we_found": "અમને શું મળ્યું",
        "what_reading_means": "આ રીડિંગનો અર્થ શું છે?",
        "sample_analysis": "નમૂના વિશ્લેષણ",
        "possible_explanations": "સંભવિત કારણો",
        "driving_advice": "શું ડ્રાઇવિંગ ચાલુ રાખી શકાય?",
        "mechanic_checks": "મિકેનિકે શું તપાસવું જોઈએ",
        "notice": "સૂચના",
        "yes": "હા",
        "no": "ના",
        "none": "કોઈ નહીં",
    },
    "kn": {
        "title": "ವಾಹನ ಹಾನಿ AI — ತಪಾಸಣಾ ವರದಿ",
        "inspection_id": "ತಪಾಸಣೆ ಐಡಿ",
        "generated": "ರಚಿಸಲಾಗಿದೆ",
        "risk_assessment": "ಅಪಾಯ ಮೌಲ್ಯಮಾಪನ",
        "vehicle": "ವಾಹನ",
        "mileage": "ಮೈಲೇಜ್",
        "damage_detected": "ಹಾನಿ ಪತ್ತೆಯಾಗಿದೆ",
        "severity_level": "ತೀವ್ರತೆಯ ಮಟ್ಟ",
        "sec1_vision": "1. ಬಾಹ್ಯ ಕಂಪ್ಯೂಟರ್ ದೃಷ್ಟಿ ಸಂಶೋಧನೆಗಳು",
        "sec2_obd": "2. OBD-II ಸಂವೇದಕಗಳು ಮತ್ತು ದೋಷ ಕೋಡ್‌ಗಳು",
        "sec3_guidance": "3. ಪರಿಶೀಲಿಸಿದ ದುರಸ್ತಿ ಮತ್ತು ಸುರಕ್ಷತಾ ಮಾರ್ಗದರ್ಶನ",
        "status": "ಸ್ಥಿತಿ",
        "anomaly_flagged": "ಅಸಂಗತತೆ ಗುರುತಿಸಲಾಗಿದೆ",
        "flagged_sensors": "ಗುರುತಿಸಲಾದ ಸಂವೇದಕಗಳು",
        "active_dtcs": "ಸಕ್ರಿಯ DTC ಕೋಡ್‌ಗಳು",
        "dtc_explanations": "ದೋಷ ಕೋಡ್ ವಿವರಣೆಗಳು",
        "urgency": "ತುರ್ತು",
        "what_it_means": "ಇದರ ಅರ್ಥವೇನು",
        "what_you_should_do": "ನೀವು ಏನು ಮಾಡಬೇಕು",
        "possible_symptoms": "ಸಂಭವನೀಯ ಲಕ್ಷಣಗಳು",
        "why_it_matters": "ಇದು ಏಕೆ ಮುಖ್ಯ",
        "limitations": "ಮಿತಿಗಳು ಮತ್ತು ಸೂಚನೆ",
        "tech_reference": "ತಾಂತ್ರಿಕ ಉಲ್ಲೇಖ",
        "reading": "ಓದುವಿಕೆ",
        "what_we_found": "ನಾವು ಕಂಡುಕೊಂಡದ್ದು",
        "what_reading_means": "ಈ ಓದುವಿಕೆಯ ಅರ್ಥವೇನು?",
        "sample_analysis": "ಮಾದರಿ ವಿಶ್ಲೇಷಣೆ",
        "possible_explanations": "ಸಂಭಾವ್ಯ ಕಾರಣಗಳು",
        "driving_advice": "ಚಾಲನೆ ಮುಂದುವರಿಸಬಹುದೇ?",
        "mechanic_checks": "ಮೆಕ್ಯಾನಿಕ್ ಏನನ್ನು ಪರೀಕ್ಷಿಸಬೇಕು",
        "notice": "ಸೂಚನೆ",
        "yes": "ಹೌದು",
        "no": "ಇಲ್ಲ",
        "none": "ಯಾವುದೂ ಇಲ್ಲ",
    },
    "ml": {
        "title": "വാഹന നാശനഷ്ട AI — പരിശോധനാ റിപ്പോർട്ട്",
        "inspection_id": "പരിശോധന ഐഡി",
        "generated": "തയ്യാറാക്കിയത്",
        "risk_assessment": "അപകടസാധ്യത വിലയിരുത്തൽ",
        "vehicle": "വാഹനം",
        "mileage": "മൈലേജ്",
        "damage_detected": "കേടുപാടുകൾ കണ്ടെത്തി",
        "severity_level": "തീവ്രതാ നില",
        "sec1_vision": "1. ബാഹ്യ കമ്പ്യൂട്ടർ ദർശന കണ്ടെത്തലുകൾ",
        "sec2_obd": "2. OBD-II സെൻസറുകളും തകരാർ കോഡുകളും",
        "sec3_guidance": "3. സ്ഥിരീകരിച്ച അറ്റകുറ്റപ്പണികളും സുരക്ഷാ മാർഗ്ഗനിർദ്ദേശങ്ങളും",
        "status": "നില",
        "anomaly_flagged": "അപാകത അടയാളപ്പെടുത്തി",
        "flagged_sensors": "അടയാളപ്പെടുത്തിയ സെൻസറുകൾ",
        "active_dtcs": "സജീവമായ DTC കോഡുകൾ",
        "dtc_explanations": "തകരാർ കോഡ് വിശദീകരണങ്ങൾ",
        "urgency": "അടിയന്തിരത",
        "what_it_means": "ഇതിന്റെ അർത്ഥമെന്താണ്",
        "what_you_should_do": "നിങ്ങൾ എന്ത് ചെയ്യണം",
        "possible_symptoms": "സാധ്യമായ ലക്ഷണങ്ങൾ",
        "why_it_matters": "ഇത് പ്രധാനമായിരിക്കുന്നത് എന്തുകൊണ്ട്",
        "limitations": "പരിമിതികളും അറിയിപ്പും",
        "tech_reference": "സാങ്കേതിക റഫറൻസ്",
        "reading": "റീഡിംഗ്",
        "what_we_found": "ഞങ്ങൾ കണ്ടെത്തിയത്",
        "what_reading_means": "ഈ റീഡിംഗ് എന്താണ് അർത്ഥമാക്കുന്നത്?",
        "sample_analysis": "സാമ്പിൾ വിശകലനം",
        "possible_explanations": "സാധ്യമായ കാരണങ്ങൾ",
        "driving_advice": "തുടർന്നും വാഹനം ഓടിക്കാമോ?",
        "mechanic_checks": "മെക്കാനിക്ക് പരിശോധിക്കേണ്ട കാര്യങ്ങൾ",
        "notice": "അറിയിപ്പ്",
        "yes": "അതെ",
        "no": "അല്ല",
        "none": "ഒന്നുമില്ല",
    },
    "pa": {
        "title": "ਵਾਹਨ ਨੁਕਸਾਨ AI — ਨਿਰੀਖਣ ਰਿਪੋਰਟ",
        "inspection_id": "ਨਿਰੀਖਣ ਆਈਡੀ",
        "generated": "ਤਿਆਰ ਕੀਤਾ",
        "risk_assessment": "ਖ਼ਤਰੇ ਦਾ ਮੁਲਾਂਕਣ",
        "vehicle": "ਵਾਹਨ",
        "mileage": "ਮਾਈਲੇਜ",
        "damage_detected": "ਨੁਕਸਾਨ ਮਿਲਿਆ",
        "severity_level": "ਗੰਭੀਰਤਾ ਦਾ ਪੱਧਰ",
        "sec1_vision": "1. ਬਾਹਰੀ ਕੰਪਿਊਟਰ ਵਿਜ਼ਨ ਨਤੀਜੇ",
        "sec2_obd": "2. OBD-II ਸੈਂਸਰ ਅਤੇ ਫਾਲਟ ਕੋਡ",
        "sec3_guidance": "3. ਪ੍ਰਮਾਣਿਤ ਮੁਰੰਮਤ ਅਤੇ ਸੁਰੱਖਿਆ ਮਾਰਗਦਰਸ਼ਨ",
        "status": "ਸਥਿਤੀ",
        "anomaly_flagged": "ਖ਼ਰਾਬੀ ਚਿੰਨ੍ਹਿਤ",
        "flagged_sensors": "ਚਿੰਨ੍ਹਿਤ ਸੈਂਸਰ",
        "active_dtcs": "ਸਰਗਰਮ DTC ਕੋਡ",
        "dtc_explanations": "ਫਾਲਟ ਕੋਡ ਵੇਰਵਾ",
        "urgency": "ਜ਼ਰੂਰਤ",
        "what_it_means": "ਇਸਦਾ ਕੀ ਅਰਥ ਹੈ",
        "what_you_should_do": "ਤੁਹਾਨੂੰ ਕੀ ਕਰਨਾ ਚਾਹੀਦਾ ਹੈ",
        "possible_symptoms": "ਸੰਭਾਵਿਤ ਲੱਛਣ",
        "why_it_matters": "ਇਹ ਮਹੱਤਵਪੂਰਨ ਕਿਉਂ ਹੈ",
        "limitations": "ਸੀਮਾਵਾਂ ਅਤੇ ਸੂਚਨਾ",
        "tech_reference": "ਤਕਨੀਕੀ ਹਵਾਲਾ",
        "reading": "ਰੀਡਿੰਗ",
        "what_we_found": "ਸਾਨੂੰ ਕੀ ਮਿਲਿਆ",
        "what_reading_means": "ਇਸ ਰੀਡਿੰਗ ਦਾ ਕੀ ਅਰਥ ਹੈ?",
        "sample_analysis": "ਨਮੂਨਾ ਵਿਸ਼ਲੇਸ਼ਣ",
        "possible_explanations": "ਸੰਭਾਵਿਤ ਕਾਰਨ",
        "driving_advice": "ਕੀ ਗੱਡੀ ਚਲਾਉਣਾ ਜਾਰੀ ਰੱਖਿਆ ਜਾ ਸਕਦਾ ਹੈ?",
        "mechanic_checks": "ਮਕੈਨਿਕ ਨੂੰ ਕੀ ਜਾਂਚਣਾ ਚਾਹੀਦਾ ਹੈ",
        "notice": "ਸੂਚਨਾ",
        "yes": "ਹਾਂ",
        "no": "ਨਹੀਂ",
        "none": "ਕੋਈ ਨਹੀਂ",
    },
    "bn": {
        "title": "যানবাহন ক্ষতি এআই — পরিদর্শন রিপোর্ট",
        "inspection_id": "পরিদর্শন আইডি",
        "generated": "তৈরি হয়েছে",
        "risk_assessment": "ঝুঁকি মূল্যায়ন",
        "vehicle": "যানবাহন",
        "mileage": "মাইলেজ",
        "damage_detected": "ক্ষতি শনাক্ত হয়েছে",
        "severity_level": "তীব্রতা স্তর",
        "sec1_vision": "1. বাহ্যিক কম্পিউটার ভিশন ফলাফল",
        "sec2_obd": "2. ওবিডি-II টেলিমেট্রি এবং ডায়াগনস্টিক কোড",
        "sec3_guidance": "3. যাচাইকৃত মেরামত ও নিরাপত্তা নির্দেশিকা",
        "status": "অবস্থা",
        "anomaly_flagged": "অসঙ্গতি চিহ্নিত",
        "flagged_sensors": "চিহ্নিত সেন্সর",
        "active_dtcs": "সক্রিয় ডিটিসি কোড",
        "dtc_explanations": "ডায়াগনস্টিক ট্রাবল কোড ব্যাখ্যা",
        "urgency": "জরুরিতা",
        "what_it_means": "এর অর্থ কি",
        "what_you_should_do": "আপনার কি করা উচিত",
        "possible_symptoms": "সম্ভাব্য লক্ষণ",
        "why_it_matters": "এটি কেন গুরুত্বপূর্ণ",
        "limitations": "সীমাবদ্ধতা ও নোটিশ",
        "tech_reference": "প্রযুক্তিগত রেফারেন্স",
        "reading": "রিডিং",
        "what_we_found": "আমরা যা পেয়েছি",
        "what_reading_means": "এই রিডিং এর অর্থ কি?",
        "sample_analysis": "নমুনা বিশ্লেষণ",
        "possible_explanations": "সম্ভাব্য কারণ",
        "driving_advice": "গাড়ি চালানো কি নিরাপদ?",
        "mechanic_checks": "মেকানিকের কি পরীক্ষা করা উচিত",
        "notice": "বিজ্ঞপ্তি",
        "yes": "হ্যাঁ",
        "no": "না",
        "none": "কোনোটি নয়",
    },
    "ur": {
        "title": "گاڑی کے نقصان کا اے آئی معائنہ رپورٹ",
        "inspection_id": "معائنہ شناختی نمبر",
        "generated": "تاریخ تیاری",
        "risk_assessment": "خطرے کا جائزہ",
        "vehicle": "گاڑی",
        "mileage": "مائلیج",
        "damage_detected": "نقصان کی شناخت",
        "severity_level": "شدت کی سطح",
        "sec1_vision": "1. بیرونی کمپیوٹر وژن نتائج",
        "sec2_obd": "2. او بی ڈی ٹیلی میٹری اور تشخیصی کوڈز",
        "sec3_guidance": "3. تصدیق شدہ مرمت اور حفاظتی رہنمائی",
        "status": "حیثیت",
        "anomaly_flagged": "خرابی نشان زد",
        "flagged_sensors": "نشان زدہ سینسرز",
        "active_dtcs": "فعال ڈی ٹی سی کوڈز",
        "dtc_explanations": "تشخیصی کوڈز کی وضاحت",
        "urgency": "فوری ضرورت",
        "what_it_means": "اس کا کیا مطلب ہے",
        "what_you_should_do": "آپ کو کیا کرنا چاہیے",
        "possible_symptoms": "ممکنہ علامات",
        "why_it_matters": "یہ کیوں اہم ہے",
        "limitations": "حدود اور نوٹس",
        "tech_reference": "تکنیکی حوالہ",
        "reading": "ریڈنگ",
        "what_we_found": "ہمیں کیا ملا",
        "what_reading_means": "اس ریڈنگ کا کیا مطلب ہے؟",
        "sample_analysis": "نمونہ تجزیہ",
        "possible_explanations": "ممکنہ وجوہات",
        "driving_advice": "کیا گاڑی چلانا محفوظ ہے؟",
        "mechanic_checks": "مکینک کو کیا چیک کرنا چاہیے",
        "notice": "اطلاع",
        "yes": "ہاں",
        "no": "نہیں",
        "none": "کوئی نہیں",
    },
}


def _get_pdf_str(key: str, locale: str = "en") -> str:
    norm = (locale or "en").lower().split("-")[0].split("_")[0]
    return PDF_TRANSLATIONS.get(norm, {}).get(key, PDF_EN.get(key, key))


def _assessment_label(entry: Dict[str, Any], locale: str = "en") -> str:
    """Tri-state damage label. INCONCLUSIVE must never print as 'NO'."""
    assessment = str(entry.get("assessment", "")).lower()
    if assessment == "damaged" or entry.get("damage_detected"):
        return _get_pdf_str("yes", locale)
    if assessment == "no_damage":
        return _get_pdf_str("no", locale)
    reason = entry.get("assessment_reason")
    return "UNABLE TO DETERMINE" + (f" ({reason})" if reason else "")


def render_inspection_pdf(
    report_data: Dict[str, Any],
    output_target: Optional[Union[str, Path, io.BytesIO]] = None,
    locale: str = "en",
) -> bytes:
    """Generate professional PDF inspection report from structured report payload."""
    buffer = io.BytesIO() if output_target is None or isinstance(output_target, io.BytesIO) else None
    target = buffer if buffer is not None else str(output_target)

    norm_locale = (locale or "en").lower().split("-")[0].split("_")[0]
    is_unicode = norm_locale != "en"

    if is_unicode:
        font_name = _init_pdf_fonts()
        font_bold = font_name
        font_oblique = font_name
    else:
        font_name = "Helvetica"
        font_bold = "Helvetica-Bold"
        font_oblique = "Helvetica-Oblique"

    doc = SimpleDocTemplate(
        target,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName=font_bold,
        fontSize=18 if is_unicode else 20,
        leading=22 if is_unicode else 24,
        textColor=colors.HexColor("#0F172A"),
    )
    subtitle_style = ParagraphStyle(
        "DocSubTitle",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=9.5,
        textColor=colors.HexColor("#64748B"),
    )
    h2_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontName=font_bold,
        fontSize=12.5,
        leading=16,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
    )
    disclaimer_style = ParagraphStyle(
        "DisclaimerText",
        parent=styles["Normal"],
        fontName=font_oblique,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#64748B"),
    )
    table_header_style = ParagraphStyle(
        "TableHeaderWhite",
        parent=styles["Normal"],
        fontName=font_bold,
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
    )

    elements = []

    # 1. Header
    title_text = _get_pdf_str("title", norm_locale)
    elements.append(Paragraph(title_text, title_style))
    insp_id = report_data.get("inspection_id", "N/A")
    gen_at = report_data.get("generated_at", "N/A")[:19].replace("T", " ")
    lbl_insp = _get_pdf_str("inspection_id", norm_locale)
    lbl_gen = _get_pdf_str("generated", norm_locale)
    elements.append(Paragraph(f"{lbl_insp}: {insp_id} &nbsp;|&nbsp; {lbl_gen}: {gen_at} UTC", subtitle_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#E2E8F0"), spaceAfter=12))

    # 2. Risk Banner
    risk = report_data.get("risk", {})
    risk_class = str(risk.get("class", "UNAVAILABLE")).upper()
    risk_bg = colors.HexColor("#10B981") if risk_class == "SAFE" else (
        colors.HexColor("#F59E0B") if risk_class == "CAUTION" else (
            colors.HexColor("#EF4444") if risk_class == "UNSAFE" else colors.HexColor("#6B7280")
        )
    )

    lbl_risk = _get_pdf_str("risk_assessment", norm_locale)
    risk_table = Table(
        [
            [
                Paragraph(f"<b>{lbl_risk}: {risk_class}</b>", ParagraphStyle("RiskT", fontName=font_bold, fontSize=11, textColor=colors.white)),
                Paragraph(risk.get("summary", ""), ParagraphStyle("RiskS", fontName=font_name, fontSize=8.5, leading=11, textColor=colors.white)),
            ]
        ],
        colWidths=[160, 370],
    )
    risk_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), risk_bg),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ])
    )
    elements.append(risk_table)
    elements.append(Spacer(1, 12))

    # 3. Vehicle & Inspection Overview
    veh = report_data.get("vehicle", {})
    make = veh.get("make") or "Not Specified"
    model = veh.get("model") or "Not Specified"
    year = str(veh.get("year") or "N/A")
    mileage = f"{veh.get('mileage')} {veh.get('mileage_unit', 'km')}" if veh.get("mileage") else "Not Provided"

    overview_data = [
        [
            Paragraph(f"<b>{_get_pdf_str('vehicle', norm_locale)}:</b>", body_style),
            Paragraph(f"{year} {make} {model}", body_style),
            Paragraph(f"<b>{_get_pdf_str('mileage', norm_locale)}:</b>", body_style),
            Paragraph(mileage, body_style),
        ],
        [
            Paragraph(f"<b>{_get_pdf_str('damage_detected', norm_locale)}:</b>", body_style),
            Paragraph(_assessment_label(report_data.get("overall", {}), norm_locale), body_style),
            Paragraph(f"<b>{_get_pdf_str('severity_level', norm_locale)}:</b>", body_style),
            Paragraph(str(report_data.get("severity", {}).get("level", "N/A")).upper(), body_style),
        ],
    ]
    overview_table = Table(overview_data, colWidths=[110, 155, 110, 155])
    overview_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#F1F5F9")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("FONTNAME", (0, 0), (-1, -1), font_name),
        ])
    )
    elements.append(overview_table)
    elements.append(Spacer(1, 12))

    # 4. Exterior Damage Findings
    elements.append(Paragraph(_get_pdf_str("sec1_vision", norm_locale), h2_style))
    images = report_data.get("images", [])
    if images:
        findings_rows = [[
            _get_pdf_str("col_image_file", norm_locale),
            _get_pdf_str("col_damage_detected", norm_locale),
            _get_pdf_str("col_primary_finding", norm_locale),
            _get_pdf_str("col_all_classes", norm_locale),
            _get_pdf_str("col_detections", norm_locale),
            _get_pdf_str("col_severity", norm_locale),
        ]]
        for img in images:
            classes_str = ", ".join([c["label"] for c in img.get("classifications", [])]) or _get_pdf_str("none", norm_locale)
            dets = img.get("detections", [])
            det_count = len(dets)
            sev_lvl = img.get("severity", {}).get("level", "unavailable").upper()
            if dets:
                first = dets[0]
                comp = (first.get("component") or "").replace("_", " ")
                primary_str = f"{first.get('label', '?')} ({round(float(first.get('confidence', 0)) * 100)}%)"
                if first.get("priority") == "primary":
                    primary_str = "PRIMARY: " + primary_str
                if comp:
                    primary_str += f" [{comp}]"
            else:
                primary_str = _get_pdf_str("none", norm_locale)
            findings_rows.append([
                img.get("filename", "image"),
                _assessment_label(img, norm_locale),
                primary_str,
                classes_str,
                str(det_count),
                sev_lvl,
            ])
        findings_table = Table(findings_rows, colWidths=[100, 70, 150, 100, 55, 55])
        findings_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                ("FONTNAME", (0, 0), (-1, 0), font_bold),
                ("FONTNAME", (0, 1), (-1, -1), font_name),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        elements.append(findings_table)
    else:
        elements.append(Paragraph(_get_pdf_str("no_images", norm_locale), body_style))
    elements.append(Spacer(1, 12))

    # 5. OBD-II Telemetry & Diagnostic Codes
    elements.append(Paragraph(_get_pdf_str("sec2_obd", norm_locale), h2_style))
    obd = report_data.get("obd", {})
    obd_status = obd.get("status", "not_provided")
    if obd_status == "completed":
        dtcs = obd.get("dtcs", [])
        dtc_summary_str = ", ".join([d.get("code", "") for d in dtcs]) if dtcs else _get_pdf_str("none", norm_locale)
        flagged = obd.get("flagged_pids", [])
        flagged_str = ", ".join([f"{f['pid_name']}: {f['observed_value']} {f.get('unit', '')}" for f in flagged[:3]]) if flagged else _get_pdf_str("none", norm_locale)

        obd_data = [
            [Paragraph(f"<b>{_get_pdf_str('status', norm_locale)}:</b>", body_style), Paragraph("Telemetry Analyzed (Isolation Forest)", body_style)],
            [Paragraph(f"<b>{_get_pdf_str('anomaly_flagged', norm_locale)}:</b>", body_style), Paragraph(_get_pdf_str("yes" if obd.get("anomaly_detected") else "no", norm_locale), body_style)],
            [Paragraph(f"<b>{_get_pdf_str('flagged_sensors', norm_locale)}:</b>", body_style), Paragraph(flagged_str, body_style)],
            [Paragraph(f"<b>{_get_pdf_str('active_dtcs', norm_locale)}:</b>", body_style), Paragraph(dtc_summary_str, body_style)],
        ]
        obd_table = Table(obd_data, colWidths=[120, 410])
        obd_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#F1F5F9")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("FONTNAME", (0, 0), (-1, -1), font_name),
            ])
        )
        elements.append(obd_table)
        elements.append(Spacer(1, 8))

        # Render individual plain-English DTC cards
        if dtcs:
            elements.append(Paragraph(f"<b>{_get_pdf_str('dtc_explanations', norm_locale)}:</b>", body_style))
            elements.append(Spacer(1, 4))
            for d in dtcs:
                code = d.get("code", "DTC")
                simple_title = d.get("simple_title") or d.get("description", "Diagnostic Warning")
                what_means = d.get("what_it_means") or d.get("description", "")
                what_to_do = d.get("what_you_should_do", "")
                urgency = d.get("urgency_label") or d.get("severity", "Moderate").title()
                why_matters = d.get("why_it_matters", "")
                symptoms = d.get("what_you_might_notice", [])
                limitations = d.get("limitations", [])
                tech_details = d.get("technical_details") or d.get("description", "")
                source_ref = d.get("source", "SAE J2012 Standard")

                card_rows = [
                    [
                        Paragraph(f"<b>{code}</b> &nbsp;|&nbsp; <b>{simple_title}</b>", ParagraphStyle("DtcH", fontName=font_bold, fontSize=9.5, textColor=colors.HexColor("#0F172A"))),
                        Paragraph(f"<b>{_get_pdf_str('urgency', norm_locale)}:</b> {urgency}", ParagraphStyle("DtcU", fontName=font_bold, fontSize=8.5, textColor=colors.HexColor("#B91C1C") if "stop" in urgency.lower() else (colors.HexColor("#B45309") if "prompt" in urgency.lower() else colors.HexColor("#1D4ED8")), alignment=2)),
                    ],
                    [
                        Paragraph(f"<b>{_get_pdf_str('what_it_means', norm_locale)}:</b> {what_means}", body_style),
                        Paragraph("", body_style),
                    ],
                ]
                if what_to_do:
                    card_rows.append([
                        Paragraph(f"<b>{_get_pdf_str('what_you_should_do', norm_locale)}:</b> {what_to_do}", ParagraphStyle("DtcAct", fontName=font_name, fontSize=8.5, leading=12, textColor=colors.HexColor("#0F766E"))),
                        Paragraph("", body_style),
                    ])
                if symptoms:
                    symptom_str = "; ".join(symptoms)
                    card_rows.append([
                        Paragraph(f"<b>{_get_pdf_str('possible_symptoms', norm_locale)}:</b> <i>{symptom_str}</i>", disclaimer_style),
                        Paragraph("", body_style),
                    ])
                if why_matters:
                    card_rows.append([
                        Paragraph(f"<b>{_get_pdf_str('why_it_matters', norm_locale)}:</b> {why_matters}", disclaimer_style),
                        Paragraph("", body_style),
                    ])
                if limitations:
                    lim_str = " ".join(limitations)
                    card_rows.append([
                        Paragraph(f"<b>{_get_pdf_str('limitations', norm_locale)}:</b> {lim_str}", disclaimer_style),
                        Paragraph("", body_style),
                    ])
                if tech_details or source_ref:
                    card_rows.append([
                        Paragraph(f"<b>{_get_pdf_str('tech_reference', norm_locale)}:</b> {tech_details} — <i>{source_ref}</i>", disclaimer_style),
                        Paragraph("", body_style),
                    ])

                dtc_card_table = Table(card_rows, colWidths=[380, 150])
                dtc_card_table.setStyle(
                    TableStyle([
                        ("SPAN", (0, 1), (1, 1)),
                        *([("SPAN", (0, r), (1, r)) for r in range(2, len(card_rows))]),
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                        ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#E2E8F0")),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("FONTNAME", (0, 0), (-1, -1), font_name),
                    ])
                )
                elements.append(dtc_card_table)
                elements.append(Spacer(1, 5))

        # Render individual plain-English Flagged Telemetry PID cards
        if flagged:
            elements.append(Spacer(1, 4))
            elements.append(Paragraph(f"<b>{_get_pdf_str('flagged_sensor_explanations', norm_locale)}:</b>", body_style))
            elements.append(Spacer(1, 4))
            for f in flagged:
                pid_name = f.get("pid_name", "PID")
                simple_title = f.get("simple_title") or f"{pid_name} Outside Expected Range"
                obs_val = f.get("observed_value")
                unit = f.get("unit", "")
                reading_str = f"{obs_val} {unit}".strip()
                what_found = f.get("what_we_found") or f.get("reason", "")
                val_meaning = f.get("value_meaning", "")
                sample_expl = f.get("sample_explanation") or f.get("reason", "")
                what_to_do = f.get("what_you_should_do", "")
                cross_notice = f.get("cross_finding_notice")
                causes = f.get("possible_causes", [])
                limitations = f.get("limitations", [])
                tech_details = f.get("technical_details", "")
                source_ref = f.get("source", "")

                card_rows = [
                    [
                        Paragraph(f"<b>{simple_title}</b>", ParagraphStyle("PidH", fontName=font_bold, fontSize=9.5, textColor=colors.HexColor("#0F172A"))),
                        Paragraph(f"<b>{_get_pdf_str('reading', norm_locale)}:</b> {reading_str}", ParagraphStyle("PidR", fontName=font_bold, fontSize=8.5, textColor=colors.HexColor("#B45309"), alignment=2)),
                    ],
                    [
                        Paragraph(f"<b>{_get_pdf_str('what_we_found', norm_locale)}:</b> {what_found}", body_style),
                        Paragraph("", body_style),
                    ],
                ]
                if val_meaning:
                    card_rows.append([
                        Paragraph(f"<b>{_get_pdf_str('what_reading_means', norm_locale)}:</b> {val_meaning}", body_style),
                        Paragraph("", body_style),
                    ])
                if sample_expl:
                    card_rows.append([
                        Paragraph(f"<b>{_get_pdf_str('sample_analysis', norm_locale)}:</b> {sample_expl}", disclaimer_style),
                        Paragraph("", body_style),
                    ])
                if what_to_do:
                    card_rows.append([
                        Paragraph(f"<b>{_get_pdf_str('what_you_should_do', norm_locale)}:</b> {what_to_do}", ParagraphStyle("PidAct", fontName=font_name, fontSize=8.5, leading=12, textColor=colors.HexColor("#0F766E"))),
                        Paragraph("", body_style),
                    ])
                if cross_notice:
                    card_rows.append([
                        Paragraph(f"<b>Diagnostic Cross-Finding Notice:</b> {cross_notice}", ParagraphStyle("PidCross", fontName=font_bold, fontSize=8.0, leading=11, textColor=colors.HexColor("#B45309"))),
                        Paragraph("", body_style),
                    ])
                if causes:
                    cause_str = "; ".join(causes)
                    card_rows.append([
                        Paragraph(f"<b>{_get_pdf_str('possible_explanations', norm_locale)}:</b> <i>{cause_str}</i>", disclaimer_style),
                        Paragraph("", body_style),
                    ])
                if limitations:
                    lim_str = " ".join(limitations)
                    card_rows.append([
                        Paragraph(f"<b>{_get_pdf_str('limitations', norm_locale)}:</b> {lim_str}", disclaimer_style),
                        Paragraph("", body_style),
                    ])
                if tech_details or source_ref:
                    tech_line = f"<b>{_get_pdf_str('tech_reference', norm_locale)}:</b> {pid_name} — {tech_details}"
                    if source_ref:
                        tech_line += f" <i>({source_ref})</i>"
                    card_rows.append([
                        Paragraph(tech_line, disclaimer_style),
                        Paragraph("", body_style),
                    ])

                pid_card_table = Table(card_rows, colWidths=[380, 150])
                pid_card_table.setStyle(
                    TableStyle([
                        ("SPAN", (0, 1), (1, 1)),
                        *([("SPAN", (0, r), (1, r)) for r in range(2, len(card_rows))]),
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                        ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#E2E8F0")),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("FONTNAME", (0, 0), (-1, -1), font_name),
                    ])
                )
                elements.append(pid_card_table)
                elements.append(Spacer(1, 5))
    else:
        elements.append(Paragraph(f"<i>{_get_pdf_str('no_obd', norm_locale)}</i>", body_style))
    elements.append(Spacer(1, 10))

    # 6. Verified Repair & Safety Guidance
    elements.append(Paragraph(_get_pdf_str("sec3_guidance", norm_locale), h2_style))
    knowledge = report_data.get("knowledge", {})
    passages = knowledge.get("passages", [])
    if passages:
        for idx, p in enumerate(passages[:3], 1):
            guidance = p.get("guidance") or {}
            cite = p.get("citation", {})
            cite_str = f"Source: {cite.get('document_title', '')} ({cite.get('publisher', '')}), {cite.get('section', '')}"
            if cite.get("url"):
                cite_str += f" — {cite.get('url')}"

            title = guidance.get("title") or f"Finding {idx} Guidance"
            what_found = guidance.get("what_we_found") or p.get("content", "")
            why_matters = guidance.get("why_this_matters", "")
            what_to_do = guidance.get("what_you_should_do_now", "")
            driving_advice = guidance.get("can_i_keep_driving", "")
            mechanic_checks = guidance.get("what_mechanic_may_check", [])
            tech_exp = guidance.get("technical_explanation", "")

            guidance_rows = [
                [
                    Paragraph(f"<b>{title}</b>", ParagraphStyle("GTitle", fontName=font_bold, fontSize=9.5, textColor=colors.HexColor("#0F172A"))),
                    Paragraph(f"<b>{_get_pdf_str('driving_advice', norm_locale)}:</b> {driving_advice}" if driving_advice else "", ParagraphStyle("GDrive", fontName=font_bold, fontSize=8, textColor=colors.HexColor("#B91C1C") if "stop" in driving_advice.lower() else (colors.HexColor("#B45309") if "avoid" in driving_advice.lower() else colors.HexColor("#1D4ED8")), alignment=2)),
                ],
                [
                    Paragraph(f"<b>{_get_pdf_str('what_we_found', norm_locale)}:</b> {what_found}", body_style),
                    Paragraph("", body_style),
                ],
            ]
            if why_matters:
                guidance_rows.append([
                    Paragraph(f"<b>{_get_pdf_str('why_it_matters', norm_locale)}:</b> {why_matters}", body_style),
                    Paragraph("", body_style),
                ])
            if what_to_do:
                guidance_rows.append([
                    Paragraph(f"<b>{_get_pdf_str('what_you_should_do', norm_locale)}:</b> {what_to_do}", ParagraphStyle("GDo", fontName=font_name, fontSize=8.5, leading=12, textColor=colors.HexColor("#0F766E"))),
                    Paragraph("", body_style),
                ])
            if mechanic_checks:
                checks_str = " • " + " • ".join(mechanic_checks)
                guidance_rows.append([
                    Paragraph(f"<b>{_get_pdf_str('mechanic_checks', norm_locale)}:</b> {checks_str}", disclaimer_style),
                    Paragraph("", body_style),
                ])
            if tech_exp:
                guidance_rows.append([
                    Paragraph(f"<b>{_get_pdf_str('tech_reference', norm_locale)}:</b> {tech_exp}", disclaimer_style),
                    Paragraph("", body_style),
                ])
            guidance_rows.append([
                Paragraph(f"<i>{cite_str}</i>", disclaimer_style),
                Paragraph("", body_style),
            ])

            guidance_table = Table(guidance_rows, colWidths=[330, 200])
            guidance_table.setStyle(
                TableStyle([
                    ("SPAN", (0, 1), (1, 1)),
                    *([("SPAN", (0, r), (1, r)) for r in range(2, len(guidance_rows))]),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#E2E8F0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("FONTNAME", (0, 0), (-1, -1), font_name),
                ])
            )
            elements.append(guidance_table)
            elements.append(Spacer(1, 6))
    else:
        elements.append(Paragraph(knowledge.get("summary_guidance") or _get_pdf_str("no_guidance", norm_locale), body_style))
    elements.append(Spacer(1, 10))

    # 7. Indicative Vehicle Repair & Replacement Cost Estimate
    elements.append(Paragraph(_get_pdf_str("sec4_estimate", norm_locale), h2_style))
    estimate_data = report_data.get("estimate")
    if estimate_data:
        dmg = estimate_data.get("damage") or {}
        rep_scen = estimate_data.get("repair_scenario") or {}
        repl_scen = estimate_data.get("replacement_scenario") or {}
        currency = estimate_data.get("vehicle", {}).get("currency", "INR")
        symbol = "₹" if currency == "INR" else f"{currency} "

        # Overview banner
        comp_name = dmg.get("component_display_name", "Component")
        extent_name = (dmg.get("extent_category") or "minor").title()
        conf_level = (estimate_data.get("overall_confidence") or "moderate").upper()

        overview_text = f"<b>Affected Component:</b> {comp_name} &nbsp;|&nbsp; <b>Damage Extent:</b> {extent_name} &nbsp;|&nbsp; <b>Estimate Confidence:</b> {conf_level}"
        elements.append(Paragraph(overview_text, body_style))
        elements.append(Spacer(1, 4))

        # Comparison Table
        rep_rec = " ★ " + _get_pdf_str("recommended", norm_locale) if rep_scen.get("is_recommended") else ""
        repl_rec = " ★ " + _get_pdf_str("recommended", norm_locale) if repl_scen.get("is_recommended") else ""

        comp_rows = [
            [
                Paragraph("<b>Action Scenario</b>", table_header_style),
                Paragraph("<b>Feasibility Status</b>", table_header_style),
                Paragraph(f"<b>{_get_pdf_str('expected_cost', norm_locale)}</b>", table_header_style),
                Paragraph(f"<b>{_get_pdf_str('cost_range', norm_locale)}</b>", table_header_style),
            ],
            [
                Paragraph(f"<b>Scenario A: Repair & Refinish</b>{rep_rec}", body_style),
                Paragraph(rep_scen.get("feasibility_reason") or rep_scen.get("feasibility", "feasible"), disclaimer_style),
                Paragraph(f"<b>{symbol}{rep_scen.get('expected', 0.0):,.2f}</b>" if rep_scen.get("expected", 0) > 0 else "N/A", body_style),
                Paragraph(f"{symbol}{rep_scen.get('minimum', 0.0):,.0f} – {symbol}{rep_scen.get('maximum', 0.0):,.0f}" if rep_scen.get("expected", 0) > 0 else "N/A", disclaimer_style),
            ],
            [
                Paragraph(f"<b>Scenario B: Complete Replacement</b>{repl_rec}", body_style),
                Paragraph(repl_scen.get("feasibility_reason") or repl_scen.get("feasibility", "feasible"), disclaimer_style),
                Paragraph(f"<b>{symbol}{repl_scen.get('expected', 0.0):,.2f}</b>", body_style),
                Paragraph(f"{symbol}{repl_scen.get('minimum', 0.0):,.0f} – {symbol}{repl_scen.get('maximum', 0.0):,.0f}", disclaimer_style),
            ],
        ]

        comp_table = Table(comp_rows, colWidths=[160, 190, 85, 95])
        comp_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (-1, -1), font_name),
            ])
        )
        elements.append(comp_table)
        elements.append(Spacer(1, 6))

        # Itemized breakdown of recommended scenario
        chosen_scen = rep_scen if rep_scen.get("is_recommended") else repl_scen
        items = chosen_scen.get("breakdown") or []
        if items:
            elements.append(Paragraph(f"<b>{_get_pdf_str('itemized_breakdown', norm_locale)}: {chosen_scen.get('title', '')}</b>", ParagraphStyle("BTitle", fontName=font_bold, fontSize=8.5, textColor=colors.HexColor("#0F172A"))))
            elements.append(Spacer(1, 2))

            item_rows = [
                [
                    Paragraph(f"<b>{_get_pdf_str('category', norm_locale)}</b>", table_header_style),
                    Paragraph(f"<b>{_get_pdf_str('description', norm_locale)}</b>", table_header_style),
                    Paragraph(f"<b>{_get_pdf_str('amount', norm_locale)}</b>", table_header_style),
                ]
            ]
            for itm in items:
                cat_display = itm.get("category", "other").upper()
                desc_display = itm.get("description", "")
                if itm.get("labour_hours"):
                    desc_display += f" ({itm.get('labour_hours')} hrs @ {symbol}{itm.get('hourly_rate', 0):,.0f}/hr)"
                cost_display = f"{symbol}{itm.get('total_cost', 0.0):,.2f}"

                item_rows.append([
                    Paragraph(cat_display, disclaimer_style),
                    Paragraph(desc_display, body_style),
                    Paragraph(cost_display, ParagraphStyle("Amt", fontName=font_bold, fontSize=8, alignment=2, textColor=colors.HexColor("#0F172A"))),
                ])

            # Total expected row
            item_rows.append([
                Paragraph("<b>TOTAL</b>", ParagraphStyle("TotCat", fontName=font_bold, fontSize=8.5, textColor=colors.HexColor("#0F172A"))),
                Paragraph(f"<b>Total Indicative Expected Cost ({currency}, GST 18% Included)</b>", ParagraphStyle("TotDesc", fontName=font_bold, fontSize=8.5, textColor=colors.HexColor("#0F172A"))),
                Paragraph(f"<b>{symbol}{chosen_scen.get('expected', 0.0):,.2f}</b>", ParagraphStyle("TotAmt", fontName=font_bold, fontSize=9, alignment=2, textColor=colors.HexColor("#1E3A8A"))),
            ])

            item_table = Table(item_rows, colWidths=[90, 340, 100])
            item_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#F1F5F9")),
                    ("LINEABOVE", (0, -1), (-1, -1), 1.0, colors.HexColor("#94A3B8")),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("FONTNAME", (0, 0), (-1, -1), font_name),
                ])
            )
            elements.append(item_table)
            elements.append(Spacer(1, 6))

        # Sources and provenance
        sources = estimate_data.get("sources") or []
        if sources:
            src_str_list = []
            for s in sources[:2]:
                src_info = f"• <b>{s.get('source_name', 'Online Parts')}</b>: {s.get('product_title', '')} (Part #{s.get('part_number', 'N/A')}) — {symbol}{s.get('advertised_price', 0):,.2f} [Verified: {s.get('retrieved_at', '')[:10]}]"
                src_str_list.append(src_info)
            src_block = "<br/>".join(src_str_list)
            elements.append(Paragraph(f"<b>{_get_pdf_str('sources_provenance', norm_locale)}:</b><br/>{src_block}", disclaimer_style))
            elements.append(Spacer(1, 4))

        elements.append(Paragraph(f"<i>{_get_pdf_str('disclaimer_cost', norm_locale)}</i>", disclaimer_style))
    else:
        elements.append(Paragraph(f"<i>{_get_pdf_str('no_estimate', norm_locale)}</i>", body_style))
    elements.append(Spacer(1, 10))

    # 8. Final Disclaimer
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=6))
    elements.append(Paragraph(f"<b>{_get_pdf_str('notice', norm_locale)}:</b> {report_data.get('disclaimer', '')}", disclaimer_style))

    # Build PDF
    doc.build(elements)

    if buffer:
        buffer.seek(0)
        return buffer.getvalue()
    elif isinstance(output_target, (str, Path)):
        with open(output_target, "rb") as f:
            return f.read()
    return b""
