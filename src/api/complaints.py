"""
Complaint query endpoints.
"""
from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.models import get_db, Complaint
from src.api.auth import get_current_user

router = APIRouter(prefix="/complaints", tags=["complaints"])


class ComplaintOut(BaseModel):
    id: int
    external_id: Optional[str]
    source: str
    date_received: date
    product: Optional[str]
    issue: Optional[str]
    narrative: Optional[str]
    company: Optional[str]
    state: Optional[str]
    taxonomy_category: Optional[str]
    taxonomy_confidence: Optional[float]
    sentiment: Optional[str]
    sentiment_confidence: Optional[float]
    is_low_confidence: bool
    keywords: Optional[list]

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[ComplaintOut])
def list_complaints(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    category: Optional[str] = Query(None),
    sentiment: Optional[str] = Query(None),
    product: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    low_confidence: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    q = db.query(Complaint)
    if start_date:
        q = q.filter(Complaint.date_received >= start_date)
    if end_date:
        q = q.filter(Complaint.date_received <= end_date)
    if category:
        q = q.filter(Complaint.taxonomy_category == category)
    if sentiment:
        q = q.filter(Complaint.sentiment == sentiment)
    if product:
        q = q.filter(Complaint.product.ilike(f"%{product}%"))
    if source:
        q = q.filter(Complaint.source == source)
    if low_confidence is not None:
        q = q.filter(Complaint.is_low_confidence == low_confidence)
    return q.order_by(Complaint.date_received.desc()).offset(skip).limit(limit).all()


@router.get("/{complaint_id}", response_model=ComplaintOut)
def get_complaint(complaint_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    from fastapi import HTTPException
    c = db.get(Complaint, complaint_id)
    if not c:
        raise HTTPException(404, "Not found")
    return c
