"""
CFPB Taxonomy Classifier
Uses TF-IDF + Logistic Regression trained on CFPB category labels.
Falls back to keyword-rule matching when confidence is low.
"""
from __future__ import annotations

import re
from typing import Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

LOW_CONFIDENCE_THRESHOLD = 0.50

CFPB_CATEGORIES = [
    "Mortgage",
    "Debt collection",
    "Credit card or prepaid card",
    "Credit reporting, credit repair services, or other personal consumer reports",
    "Checking or savings account",
    "Student loan",
    "Vehicle loan or lease",
    "Payday loan, title loan, personal loan, or advance loan",
    "Money transfer, virtual currency, or money service",
    "Bank account or service",
    "Consumer Loan",
    "Other financial service",
]

KEYWORD_RULES: dict[str, list[str]] = {
    "Mortgage": ["mortgage", "foreclosure", "escrow", "lien", "refinanc"],
    "Debt collection": ["debt", "collect", "garnish", "repossess"],
    "Credit card or prepaid card": ["credit card", "prepaid card", "chargeback"],
    "Credit reporting, credit repair services, or other personal consumer reports": [
        "credit report", "credit score", "equifax", "experian", "transunion", "credit bureau"
    ],
    "Checking or savings account": ["checking account", "savings account", "overdraft", "atm"],
    "Student loan": ["student loan", "tuition", "fafsa"],
    "Vehicle loan or lease": ["car loan", "auto loan", "vehicle loan", "lease"],
    "Payday loan, title loan, personal loan, or advance loan": ["payday", "title loan", "personal loan", "advance loan"],
    "Money transfer, virtual currency, or money service": ["wire transfer", "money order", "bitcoin", "crypto"],
}


def _rule_based_category(text: str) -> Optional[str]:
    text_lower = text.lower()
    for category, keywords in KEYWORD_RULES.items():
        if any(kw in text_lower for kw in keywords):
            return category
    return None


class TaxonomyClassifier:
    def __init__(self):
        self._pipeline: Optional[Pipeline] = None
        self.model_version = "v1.0-tfidf-lr"

    def _build_pipeline(self) -> Pipeline:
        return Pipeline([
            ("tfidf", TfidfVectorizer(max_features=10000, ngram_range=(1, 2), stop_words="english")),
            ("clf", LogisticRegression(max_iter=500, C=1.0)),
        ])

    def fit(self, texts: list[str], labels: list[str]):
        self._pipeline = self._build_pipeline()
        self._pipeline.fit(texts, labels)

    def predict(self, text: str) -> dict:
        """Returns category, confidence, is_low_confidence."""
        clean = re.sub(r"\s+", " ", text.strip())
        if self._pipeline is not None:
            proba = self._pipeline.predict_proba([clean])[0]
            idx = int(np.argmax(proba))
            confidence = float(proba[idx])
            category = self._pipeline.classes_[idx]
        else:
            # Fallback: rule-based
            category = _rule_based_category(clean) or "Other financial service"
            confidence = 0.60 if category != "Other financial service" else 0.40

        is_low_confidence = confidence < LOW_CONFIDENCE_THRESHOLD
        return {
            "category": category,
            "confidence": round(confidence, 4),
            "is_low_confidence": is_low_confidence,
            "model_version": self.model_version,
        }

    def predict_batch(self, texts: list[str]) -> list[dict]:
        return [self.predict(t) for t in texts]


# Module-level singleton (loaded once per process)
_classifier: Optional[TaxonomyClassifier] = None


def get_classifier() -> TaxonomyClassifier:
    global _classifier
    if _classifier is None:
        _classifier = TaxonomyClassifier()
    return _classifier
