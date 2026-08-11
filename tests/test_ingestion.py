"""Tests for ingestion modules."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import io
import csv
import pytest
from src.ingestion.file_upload import parse_upload


def _make_csv(rows: list[dict], fieldnames=None) -> bytes:
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode()


class TestFileUpload:
    def test_basic_csv(self):
        data = [
            {"date_received": "2026-01-15", "narrative": "My mortgage was denied", "product": "Mortgage"},
            {"date_received": "2026-01-16", "narrative": "Credit card fraud issue", "product": "Credit card"},
        ]
        content = _make_csv(data)
        records = list(parse_upload(content, "test.csv"))
        assert len(records) == 2
        assert records[0]["narrative"] == "My mortgage was denied"
        assert records[0]["source"] == "upload"

    def test_missing_required_column(self):
        data = [{"product": "Mortgage", "company": "Big Bank"}]
        content = _make_csv(data)
        with pytest.raises(ValueError, match="Missing required columns"):
            list(parse_upload(content, "test.csv"))

    def test_unsupported_format(self):
        with pytest.raises(ValueError, match="Unsupported file type"):
            list(parse_upload(b"data", "test.txt"))

    def test_column_alias_date(self):
        data = [{"date": "2026-01-15", "narrative": "Test narrative"}]
        content = _make_csv(data)
        records = list(parse_upload(content, "test.csv"))
        assert len(records) == 1
        assert "date_received" in records[0]

    def test_column_alias_text(self):
        data = [{"date_received": "2026-01-15", "text": "Feedback text"}]
        content = _make_csv(data)
        records = list(parse_upload(content, "test.csv"))
        assert records[0]["narrative"] == "Feedback text"
