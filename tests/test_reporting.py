"""Tests for reporting modules."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from src.reporting.csv_export import generate_csv
from src.reporting.pdf_report import generate_pdf_report


class TestCsvExport:
    def test_basic_export(self):
        rows = [
            {"id": 1, "date_received": "2026-01-15", "category": "Mortgage", "count": 5},
            {"id": 2, "date_received": "2026-01-16", "category": "Debt collection", "count": 3},
        ]
        result = generate_csv(rows)
        assert isinstance(result, bytes)
        text = result.decode()
        assert "Mortgage" in text
        assert "date_received" in text

    def test_empty_export(self):
        result = generate_csv([])
        assert result == b""

    def test_custom_fieldnames(self):
        rows = [{"id": 1, "extra": "ignored", "name": "test"}]
        result = generate_csv(rows, fieldnames=["id", "name"])
        text = result.decode()
        assert "id" in text
        assert "name" in text
        assert "extra" not in text


class TestPdfReport:
    def test_generates_bytes(self):
        pdf = generate_pdf_report(
            title="Test Report",
            filters={"start_date": "2026-01-01"},
            summary={"Total": 100},
            category_rows=[{"category": "Mortgage", "count": 50}],
            sentiment_summary={"Positive": 20, "Negative": 80},
            top_keywords=[{"keyword": "mortgage", "count": 30}],
        )
        assert isinstance(pdf, bytes)
        assert len(pdf) > 0
        # PDF magic bytes
        assert pdf[:4] == b"%PDF"

    def test_empty_data(self):
        pdf = generate_pdf_report(
            title="Empty Report",
            filters={},
            summary={},
            category_rows=[],
            sentiment_summary={},
            top_keywords=[],
        )
        assert isinstance(pdf, bytes)
        assert pdf[:4] == b"%PDF"
