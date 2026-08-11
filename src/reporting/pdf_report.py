"""
PDF report generation using ReportLab.
"""
from __future__ import annotations

import io
from datetime import date
from typing import Optional

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def generate_pdf_report(
    title: str,
    filters: dict,
    summary: dict,
    category_rows: list[dict],
    sentiment_summary: dict,
    top_keywords: list[dict],
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(title, styles["Title"]))
    elements.append(Spacer(1, 12))

    # Generated date
    elements.append(Paragraph(f"Generated: {date.today()}", styles["Normal"]))
    if filters:
        filter_str = ", ".join(f"{k}={v}" for k, v in filters.items() if v)
        elements.append(Paragraph(f"Filters: {filter_str}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Summary
    elements.append(Paragraph("Summary", styles["Heading2"]))
    for k, v in summary.items():
        elements.append(Paragraph(f"<b>{k}:</b> {v}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Category table
    if category_rows:
        elements.append(Paragraph("Complaints by Category", styles["Heading2"]))
        table_data = [["Category", "Count"]] + [
            [r.get("category", ""), str(r.get("count", 0))] for r in category_rows[:20]
        ]
        t = Table(table_data, colWidths=[380, 80])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 12))

    # Sentiment
    if sentiment_summary:
        elements.append(Paragraph("Sentiment Distribution", styles["Heading2"]))
        for label, count in sentiment_summary.items():
            elements.append(Paragraph(f"<b>{label}:</b> {count}", styles["Normal"]))
        elements.append(Spacer(1, 12))

    # Keywords
    if top_keywords:
        elements.append(Paragraph("Top Keywords", styles["Heading2"]))
        kw_data = [["Keyword", "Count"]] + [
            [r.get("keyword", ""), str(r.get("count", 0))] for r in top_keywords[:20]
        ]
        kt = Table(kw_data, colWidths=[380, 80])
        kt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(kt)

    doc.build(elements)
    return buffer.getvalue()
