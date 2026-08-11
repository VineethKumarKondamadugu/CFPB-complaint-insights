"""
3-class Sentiment Analysis
Uses a simple lexicon-based approach; can be swapped for a transformer model.
"""
from __future__ import annotations

import re
from collections import Counter

POSITIVE_WORDS = {
    "resolved", "satisfied", "helpful", "excellent", "great", "fixed",
    "corrected", "approved", "good", "pleased", "thank", "happy", "appreciate",
}
NEGATIVE_WORDS = {
    "fraud", "scam", "harassment", "illegal", "wrong", "error", "issue",
    "problem", "denied", "refused", "unfair", "mislead", "misled", "lost",
    "stolen", "breach", "fail", "failure", "damage", "hurt", "terrible",
    "horrible", "awful", "ridiculous", "unacceptable", "complaint",
}

SENTIMENT_MODEL_VERSION = "v1.0-lexicon"


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-z]+\b", text.lower())


def analyze_sentiment(text: str) -> dict:
    tokens = _tokenize(text)
    pos = sum(1 for t in tokens if t in POSITIVE_WORDS)
    neg = sum(1 for t in tokens if t in NEGATIVE_WORDS)

    total = pos + neg
    if total == 0:
        label = "Neutral"
        confidence = 0.60
    elif pos > neg:
        label = "Positive"
        confidence = round(min(0.95, 0.60 + 0.15 * (pos - neg)), 4)
    else:
        label = "Negative"
        confidence = round(min(0.95, 0.60 + 0.10 * (neg - pos)), 4)

    return {
        "sentiment": label,
        "confidence": confidence,
        "model_version": SENTIMENT_MODEL_VERSION,
    }
