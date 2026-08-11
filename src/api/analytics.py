"""
Analytics / trends endpoints.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.models import get_db, Complaint
from src.services.trends import compute_wow, compute_mom, category_trends
from src.nlp.keywords import extract_keywords
from src.api.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/wow")
def wow(db: Session = Depends(get_db), _user=Depends(get_current_user)):
    return compute_wow(db)


@router.get("/mom")
def mom(db: Session = Depends(get_db), _user=Depends(get_current_user)):
    return compute_mom(db)


@router.get("/categories")
def categories(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    end = end_date or date.today()
    start = start_date or (end - timedelta(days=180))
    return category_trends(db, start, end)


@router.get("/keywords")
def keywords(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    category: Optional[str] = Query(None),
    top_n: int = Query(20, le=100),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    end = end_date or date.today()
    start = start_date or (end - timedelta(days=180))
    q = db.query(Complaint.narrative).filter(
        Complaint.date_received >= start,
        Complaint.date_received <= end,
        Complaint.narrative.isnot(None),
    )
    if category:
        q = q.filter(Complaint.taxonomy_category == category)
    texts = [row[0] for row in q.all()]
    return extract_keywords(texts, top_n=top_n)


@router.get("/sentiment")
def sentiment_summary(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    end = end_date or date.today()
    start = start_date or (end - timedelta(days=180))
    q = db.query(Complaint.sentiment, func.count(Complaint.id)).filter(
        Complaint.date_received >= start,
        Complaint.date_received <= end,
    )
    if category:
        q = q.filter(Complaint.taxonomy_category == category)
    rows = q.group_by(Complaint.sentiment).all()
    return [{"sentiment": s.value if s else None, "count": c} for s, c in rows]


@router.get("/low-confidence")
def low_confidence_queue(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    items = (
        db.query(Complaint)
        .filter(Complaint.is_low_confidence == True)  # noqa: E712
        .order_by(Complaint.date_received.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        {
            "id": c.id,
            "date_received": str(c.date_received),
            "taxonomy_category": c.taxonomy_category,
            "taxonomy_confidence": c.taxonomy_confidence,
            "narrative_snippet": (c.narrative or "")[:200],
        }
        for c in items
    ]
