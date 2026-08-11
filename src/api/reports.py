"""
Report export endpoints.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.models import get_db, Complaint
from src.reporting.pdf_report import generate_pdf_report
from src.reporting.csv_export import generate_csv
from src.nlp.keywords import extract_keywords
from src.services.trends import category_trends
from src.api.auth import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])


def _build_report_data(db: Session, start: date, end: date, category: Optional[str], source: Optional[str]):
    q = db.query(Complaint).filter(
        Complaint.date_received >= start,
        Complaint.date_received <= end,
    )
    if category:
        q = q.filter(Complaint.taxonomy_category == category)
    if source:
        q = q.filter(Complaint.source == source)

    complaints = q.all()
    cat_rows = category_trends(db, start, end)

    sentiment_q = (
        db.query(Complaint.sentiment, func.count(Complaint.id))
        .filter(Complaint.date_received >= start, Complaint.date_received <= end)
        .group_by(Complaint.sentiment)
    )
    if category:
        sentiment_q = sentiment_q.filter(Complaint.taxonomy_category == category)
    sentiment_summary = {
        (s.value if s else "Unknown"): c for s, c in sentiment_q.all()
    }

    narratives = [c.narrative for c in complaints if c.narrative]
    top_keywords = extract_keywords(narratives, top_n=20)

    return {
        "total": len(complaints),
        "category_rows": cat_rows,
        "sentiment_summary": sentiment_summary,
        "top_keywords": top_keywords,
        "complaints": complaints,
    }


@router.get("/pdf")
def pdf_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    category: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    end = end_date or date.today()
    start = start_date or (end - timedelta(days=180))
    filters = {"start_date": str(start), "end_date": str(end), "category": category, "source": source}
    data = _build_report_data(db, start, end, category, source)

    pdf_bytes = generate_pdf_report(
        title="CFPB Complaint Insights Report",
        filters=filters,
        summary={"Total Complaints": data["total"]},
        category_rows=data["category_rows"],
        sentiment_summary=data["sentiment_summary"],
        top_keywords=data["top_keywords"],
    )
    return Response(content=pdf_bytes, media_type="application/pdf",
                    headers={"Content-Disposition": "attachment; filename=cfpb_report.pdf"})


@router.get("/csv")
def csv_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    category: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    end = end_date or date.today()
    start = start_date or (end - timedelta(days=180))
    data = _build_report_data(db, start, end, category, source)

    rows = [
        {
            "id": c.id,
            "date_received": str(c.date_received),
            "product": c.product,
            "company": c.company,
            "state": c.state,
            "taxonomy_category": c.taxonomy_category,
            "taxonomy_confidence": c.taxonomy_confidence,
            "sentiment": c.sentiment.value if c.sentiment else None,
            "is_low_confidence": c.is_low_confidence,
        }
        for c in data["complaints"]
    ]
    csv_bytes = generate_csv(rows)
    return Response(content=csv_bytes, media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=cfpb_complaints.csv"})
