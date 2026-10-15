"""Automotive Inspection PDF Report Renderer.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 14.3 and Master Prompt Step 11.
Renders publication-ready, printable PDF reports with ReportLab.
Includes executive summary, risk banner, damage tables, OBD findings,
grounded repair guidance with citations, and safety disclaimers.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any, Dict, Optional, Union
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _assessment_label(entry: Dict[str, Any]) -> str:
    """Tri-state damage label. INCONCLUSIVE must never print as 'NO'."""
    assessment = str(entry.get("assessment", "")).lower()
    if assessment == "damaged" or entry.get("damage_detected"):
        return "YES"
    if assessment == "no_damage":
        return "NO"
    reason = entry.get("assessment_reason")
    return "UNABLE TO DETERMINE" + (f" ({reason})" if reason else "")


def render_inspection_pdf(
    report_data: Dict[str, Any],
    output_target: Optional[Union[str, Path, io.BytesIO]] = None,
) -> bytes:
    """Generate professional PDF inspection report from structured report payload."""
    buffer = io.BytesIO() if output_target is None or isinstance(output_target, io.BytesIO) else None
    target = buffer if buffer is not None else str(output_target)

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
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A"),
    )
    subtitle_style = ParagraphStyle(
        "DocSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=colors.HexColor("#64748B"),
    )
    h2_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
    )
    disclaimer_style = ParagraphStyle(
        "DisclaimerText",
        parent=styles["Italic"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#64748B"),
    )

    elements = []

    # 1. Header
    elements.append(Paragraph("VEHICLE DAMAGE AI — INSPECTION REPORT", title_style))
    insp_id = report_data.get("inspection_id", "N/A")
    gen_at = report_data.get("generated_at", "N/A")[:19].replace("T", " ")
    elements.append(Paragraph(f"Inspection ID: {insp_id} &nbsp;|&nbsp; Generated: {gen_at} UTC", subtitle_style))
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

    risk_table = Table(
        [
            [
                Paragraph(f"<b>RISK ASSESSMENT: {risk_class}</b>", ParagraphStyle("RiskT", fontName="Helvetica-Bold", fontSize=12, textColor=colors.white)),
                Paragraph(risk.get("summary", ""), ParagraphStyle("RiskS", fontName="Helvetica", fontSize=9, textColor=colors.white)),
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
            Paragraph("<b>Vehicle:</b>", body_style),
            Paragraph(f"{year} {make} {model}", body_style),
            Paragraph("<b>Mileage:</b>", body_style),
            Paragraph(mileage, body_style),
        ],
        [
            Paragraph("<b>Damage Detected:</b>", body_style),
            Paragraph(_assessment_label(report_data.get("overall", {})), body_style),
            Paragraph("<b>Severity Level:</b>", body_style),
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
        ])
    )
    elements.append(overview_table)
    elements.append(Spacer(1, 12))

    # 4. Exterior Damage Findings
    elements.append(Paragraph("1. Exterior Computer Vision Findings", h2_style))
    images = report_data.get("images", [])
    if images:
        findings_rows = [["Image File", "Damage Detected", "Primary Finding", "All Classes", "Detections", "Severity"]]
        for img in images:
            classes_str = ", ".join([c["label"] for c in img.get("classifications", [])]) or "None"
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
                primary_str = "None"
            findings_rows.append([
                img.get("filename", "image"),
                _assessment_label(img),
                primary_str,
                classes_str,
                str(det_count),
                sev_lvl,
            ])
        findings_table = Table(findings_rows, colWidths=[100, 70, 150, 100, 55, 55])
        findings_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        elements.append(findings_table)
    else:
        elements.append(Paragraph("No images were provided or analyzed.", body_style))
    elements.append(Spacer(1, 12))

    # 5. OBD-II Telemetry
    elements.append(Paragraph("2. OBD-II Telemetry & Diagnostic Codes", h2_style))
    obd = report_data.get("obd", {})
    obd_status = obd.get("status", "not_provided")
    if obd_status == "completed":
        dtcs = obd.get("dtcs", [])
        dtc_str = ", ".join([f"{d['code']} ({d.get('description', '')})" for d in dtcs]) if dtcs else "None"
        flagged = obd.get("flagged_pids", [])
        flagged_str = ", ".join([f"{f['pid_name']}: {f['observed_value']} {f.get('unit', '')}" for f in flagged[:3]]) if flagged else "None"

        obd_data = [
            [Paragraph("<b>Status:</b>", body_style), Paragraph("Telemetry Analyzed (Isolation Forest)", body_style)],
            [Paragraph("<b>Anomaly Flagged:</b>", body_style), Paragraph("YES" if obd.get("anomaly_detected") else "NO", body_style)],
            [Paragraph("<b>Flagged Sensors:</b>", body_style), Paragraph(flagged_str, body_style)],
            [Paragraph("<b>Active DTCs:</b>", body_style), Paragraph(dtc_str, body_style)],
        ]
        obd_table = Table(obd_data, colWidths=[120, 410])
        obd_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#F1F5F9")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        elements.append(obd_table)
    else:
        elements.append(Paragraph("<i>No OBD-II telemetry log provided with this inspection.</i>", body_style))
    elements.append(Spacer(1, 12))

    # 6. RAG Guidance & Citations
    elements.append(Paragraph("3. Verified Repair & Safety Guidance", h2_style))
    knowledge = report_data.get("knowledge", {})
    passages = knowledge.get("passages", [])
    if passages:
        for idx, p in enumerate(passages[:2], 1):
            cite = p.get("citation", {})
            cite_str = f"Source: {cite.get('document_title', '')} ({cite.get('publisher', '')}), {cite.get('section', '')}"
            elements.append(Paragraph(f"<b>Guidance {idx}:</b> {p.get('content', '')}", body_style))
            elements.append(Paragraph(f"<i>{cite_str}</i>", disclaimer_style))
            elements.append(Spacer(1, 4))
    else:
        elements.append(Paragraph(knowledge.get("summary_guidance", "No verified guidance available."), body_style))
    elements.append(Spacer(1, 14))

    # 7. Disclaimer
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=6))
    elements.append(Paragraph(f"<b>Notice:</b> {report_data.get('disclaimer', '')}", disclaimer_style))

    # Build PDF
    doc.build(elements)

    if buffer:
        buffer.seek(0)
        return buffer.getvalue()
    elif isinstance(output_target, (str, Path)):
        with open(output_target, "rb") as f:
            return f.read()
    return b""
