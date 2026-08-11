"""
Pipeline: persists ingested complaint records and runs NLP analysis.
"""
from __future__ import annotations

import logging
from datetime import date

from sqlalchemy.orm import Session

from src.models.models import Complaint, AuditLog, SentimentEnum, SourceEnum
from src.nlp.classifier import get_classifier
from src.nlp.sentiment import analyze_sentiment
from src.nlp.keywords import extract_keywords_single

logger = logging.getLogger(__name__)

LOW_CONFIDENCE_THRESHOLD = 0.50


def ingest_record(db: Session, record: dict) -> Complaint | None:
    """
    Persist a single complaint record (if not duplicate) and run NLP.
    Returns the saved Complaint or None if duplicate.
    """
    external_id = str(record.get("external_id") or "")

    # Deduplication
    if external_id:
        existing = db.query(Complaint).filter_by(external_id=external_id).first()
        if existing:
            return None

    narrative = record.get("narrative") or ""
    date_received = record.get("date_received")
    if isinstance(date_received, str):
        try:
            date_received = date.fromisoformat(date_received[:10])
        except ValueError:
            date_received = date.today()
    elif date_received is None:
        date_received = date.today()

    # Taxonomy
    classifier = get_classifier()
    tax_result = classifier.predict(narrative) if narrative else {
        "category": None, "confidence": 0.0, "is_low_confidence": True,
        "model_version": "v1.0",
    }

    # Sentiment
    sent_result = analyze_sentiment(narrative) if narrative else {
        "sentiment": "Neutral", "confidence": 0.60, "model_version": "v1.0-lexicon",
    }

    # Keywords
    keywords = extract_keywords_single(narrative, top_n=10) if narrative else []

    complaint = Complaint(
        external_id=external_id or None,
        source=SourceEnum(record.get("source", "cfpb")),
        date_received=date_received,
        product=record.get("product"),
        sub_product=record.get("sub_product"),
        issue=record.get("issue"),
        sub_issue=record.get("sub_issue"),
        narrative=narrative or None,
        company=record.get("company"),
        state=record.get("state"),
        zip_code=record.get("zip_code"),
        tags=record.get("tags"),
        consumer_consent=record.get("consumer_consent"),
        submitted_via=record.get("submitted_via"),
        company_response=record.get("company_response"),
        timely_response=record.get("timely_response"),
        consumer_disputed=record.get("consumer_disputed"),
        taxonomy_category=tax_result["category"],
        taxonomy_confidence=tax_result["confidence"],
        sentiment=SentimentEnum(sent_result["sentiment"]),
        sentiment_confidence=sent_result["confidence"],
        is_low_confidence=tax_result["is_low_confidence"],
        keywords=keywords,
    )

    db.add(complaint)
    db.flush()

    audit = AuditLog(
        complaint_id=complaint.id,
        action="nlp_analysis",
        model_name="taxonomy+sentiment",
        model_version=tax_result.get("model_version"),
        prompt_version=None,
        details={
            "taxonomy_confidence": tax_result["confidence"],
            "sentiment_confidence": sent_result["confidence"],
        },
    )
    db.add(audit)
    db.commit()
    db.refresh(complaint)
    return complaint
