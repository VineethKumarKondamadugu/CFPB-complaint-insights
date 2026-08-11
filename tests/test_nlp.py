"""Tests for NLP modules."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.nlp.sentiment import analyze_sentiment
from src.nlp.keywords import extract_keywords, extract_keywords_single
from src.nlp.classifier import TaxonomyClassifier, _rule_based_category


class TestSentiment:
    def test_negative_complaint(self):
        result = analyze_sentiment("This is fraud and they stole my money. The problem is terrible.")
        assert result["sentiment"] == "Negative"
        assert 0 < result["confidence"] <= 1.0

    def test_positive_feedback(self):
        result = analyze_sentiment("The issue was resolved quickly. I am satisfied and happy with the service.")
        assert result["sentiment"] == "Positive"
        assert 0 < result["confidence"] <= 1.0

    def test_neutral_empty(self):
        result = analyze_sentiment("I contacted the bank.")
        assert result["sentiment"] in ("Neutral", "Positive", "Negative")
        assert "model_version" in result

    def test_model_version_present(self):
        result = analyze_sentiment("test text")
        assert "model_version" in result


class TestKeywords:
    def test_extract_single(self):
        text = "mortgage foreclosure loan payment bank account"
        keywords = extract_keywords_single(text, top_n=5)
        assert len(keywords) > 0
        assert all(isinstance(k, str) for k in keywords)

    def test_extract_corpus(self):
        texts = [
            "credit card debt collection problem",
            "credit card fraud stolen",
            "debt collector harassment",
        ]
        results = extract_keywords(texts, top_n=10)
        assert len(results) > 0
        assert "keyword" in results[0]
        assert "count" in results[0]
        assert "frequency" in results[0]

    def test_empty_corpus(self):
        results = extract_keywords([], top_n=10)
        assert results == []


class TestClassifier:
    def test_rule_based_mortgage(self):
        cat = _rule_based_category("My mortgage payment was not processed correctly")
        assert cat == "Mortgage"

    def test_rule_based_debt(self):
        cat = _rule_based_category("A debt collector keeps calling me")
        assert cat == "Debt collection"

    def test_rule_based_unknown(self):
        cat = _rule_based_category("Something else entirely unrelated")
        assert cat is None

    def test_predict_fallback(self):
        classifier = TaxonomyClassifier()
        result = classifier.predict("my mortgage was denied")
        assert "category" in result
        assert "confidence" in result
        assert "is_low_confidence" in result
        assert 0 <= result["confidence"] <= 1.0

    def test_predict_with_trained_model(self):
        classifier = TaxonomyClassifier()
        texts = [
            "mortgage foreclosure loan payment",
            "credit card fraud charge dispute",
            "student loan payment deferment",
            "debt collector harassment calls",
            "checking account overdraft fee",
        ]
        labels = [
            "Mortgage",
            "Credit card or prepaid card",
            "Student loan",
            "Debt collection",
            "Checking or savings account",
        ]
        classifier.fit(texts, labels)
        result = classifier.predict("my mortgage payment is overdue")
        assert result["category"] in labels
        assert result["confidence"] > 0
