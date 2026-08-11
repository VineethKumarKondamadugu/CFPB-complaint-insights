import enum
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Integer, Float, Text, DateTime, Date,
    Boolean, ForeignKey, Enum as SAEnum, JSON
)
from sqlalchemy.orm import relationship

from src.models.database import Base


class SentimentEnum(str, enum.Enum):
    positive = "Positive"
    neutral = "Neutral"
    negative = "Negative"


class SourceEnum(str, enum.Enum):
    cfpb = "cfpb"
    upload = "upload"


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(64), unique=True, nullable=True, index=True)
    source = Column(SAEnum(SourceEnum), nullable=False, default=SourceEnum.cfpb)
    date_received = Column(Date, nullable=False, index=True)
    product = Column(String(256), nullable=True, index=True)
    sub_product = Column(String(256), nullable=True)
    issue = Column(String(512), nullable=True)
    sub_issue = Column(String(512), nullable=True)
    narrative = Column(Text, nullable=True)
    company = Column(String(256), nullable=True, index=True)
    state = Column(String(8), nullable=True)
    zip_code = Column(String(16), nullable=True)
    tags = Column(String(128), nullable=True)
    consumer_consent = Column(Boolean, nullable=True)
    submitted_via = Column(String(64), nullable=True)
    company_response = Column(Text, nullable=True)
    timely_response = Column(Boolean, nullable=True)
    consumer_disputed = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # NLP outputs
    taxonomy_category = Column(String(256), nullable=True, index=True)
    taxonomy_confidence = Column(Float, nullable=True)
    sentiment = Column(SAEnum(SentimentEnum), nullable=True, index=True)
    sentiment_confidence = Column(Float, nullable=True)
    is_low_confidence = Column(Boolean, default=False, nullable=False)
    keywords = Column(JSON, nullable=True)   # list of strings
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)

    topic = relationship("Topic", back_populates="complaints")
    audit_logs = relationship("AuditLog", back_populates="complaint")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    top_keywords = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    complaints = relationship("Complaint", back_populates="topic")


class TrendSnapshot(Base):
    """Stores aggregated weekly/monthly trend metrics."""
    __tablename__ = "trend_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    period_type = Column(String(16), nullable=False)   # 'weekly' | 'monthly'
    period_start = Column(Date, nullable=False, index=True)
    period_end = Column(Date, nullable=False)
    category = Column(String(256), nullable=True, index=True)
    complaint_count = Column(Integer, default=0)
    positive_count = Column(Integer, default=0)
    neutral_count = Column(Integer, default=0)
    negative_count = Column(Integer, default=0)
    top_keywords = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=True)
    action = Column(String(128), nullable=False)
    model_name = Column(String(128), nullable=True)
    model_version = Column(String(64), nullable=True)
    prompt_version = Column(String(64), nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    complaint = relationship("Complaint", back_populates="audit_logs")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(256), unique=True, nullable=False, index=True)
    hashed_password = Column(String(256), nullable=False)
    full_name = Column(String(256), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
