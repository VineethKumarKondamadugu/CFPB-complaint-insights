"""
Trend analytics: compute WoW and MoM deltas for complaint metrics.
"""
from __future__ import annotations

from datetime import date, timedelta
from collections import Counter
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from src.models.models import Complaint, TrendSnapshot, SentimentEnum


def _complaint_count(db: Session, start: date, end: date, category: Optional[str] = None) -> int:
    q = db.query(func.count(Complaint.id)).filter(
        Complaint.date_received >= start,
        Complaint.date_received <= end,
    )
    if category:
        q = q.filter(Complaint.taxonomy_category == category)
    return q.scalar() or 0


def _sentiment_counts(db: Session, start: date, end: date) -> dict:
    rows = (
        db.query(Complaint.sentiment, func.count(Complaint.id))
        .filter(Complaint.date_received >= start, Complaint.date_received <= end)
        .group_by(Complaint.sentiment)
        .all()
    )
    result = {"Positive": 0, "Neutral": 0, "Negative": 0}
    for sentiment, count in rows:
        if sentiment:
            result[sentiment.value] = count
    return result


def compute_wow(db: Session, reference_date: Optional[date] = None) -> dict:
    """Week-over-week delta as of reference_date (defaults to today)."""
    ref = reference_date or date.today()
    current_end = ref
    current_start = ref - timedelta(days=6)
    prev_end = current_start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=6)

    current = _complaint_count(db, current_start, current_end)
    previous = _complaint_count(db, prev_start, prev_end)
    delta = current - previous
    pct = round((delta / previous * 100) if previous else 0.0, 2)

    current_sentiment = _sentiment_counts(db, current_start, current_end)
    prev_sentiment = _sentiment_counts(db, prev_start, prev_end)

    return {
        "period": "weekly",
        "current_period": {"start": str(current_start), "end": str(current_end)},
        "previous_period": {"start": str(prev_start), "end": str(prev_end)},
        "complaint_count": {"current": current, "previous": previous, "delta": delta, "pct_change": pct},
        "sentiment": {
            "current": current_sentiment,
            "previous": prev_sentiment,
        },
    }


def compute_mom(db: Session, reference_date: Optional[date] = None) -> dict:
    """Month-over-month delta as of reference_date (defaults to today)."""
    ref = reference_date or date.today()
    current_end = ref
    current_start = ref.replace(day=1)
    prev_end = current_start - timedelta(days=1)
    prev_start = prev_end.replace(day=1)

    current = _complaint_count(db, current_start, current_end)
    previous = _complaint_count(db, prev_start, prev_end)
    delta = current - previous
    pct = round((delta / previous * 100) if previous else 0.0, 2)

    current_sentiment = _sentiment_counts(db, current_start, current_end)
    prev_sentiment = _sentiment_counts(db, prev_start, prev_end)

    return {
        "period": "monthly",
        "current_period": {"start": str(current_start), "end": str(current_end)},
        "previous_period": {"start": str(prev_start), "end": str(prev_end)},
        "complaint_count": {"current": current, "previous": previous, "delta": delta, "pct_change": pct},
        "sentiment": {
            "current": current_sentiment,
            "previous": prev_sentiment,
        },
    }


def category_trends(db: Session, start: date, end: date) -> list[dict]:
    rows = (
        db.query(Complaint.taxonomy_category, func.count(Complaint.id))
        .filter(Complaint.date_received >= start, Complaint.date_received <= end)
        .group_by(Complaint.taxonomy_category)
        .order_by(func.count(Complaint.id).desc())
        .all()
    )
    return [{"category": cat, "count": cnt} for cat, cnt in rows]
