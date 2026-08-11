"""Tests for trend analytics services."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import date, timedelta
import pytest
from unittest.mock import MagicMock

from src.services.trends import compute_wow, compute_mom, category_trends


def _make_mock_db(current_count=10, prev_count=8):
    """Return a mock Session that returns expected complaint counts."""
    db = MagicMock()

    call_count = [0]

    def scalar_side_effect():
        call_count[0] += 1
        if call_count[0] % 2 == 1:
            return current_count
        return prev_count

    # For count queries
    db.query.return_value.filter.return_value.filter.return_value.filter.return_value.scalar.side_effect = scalar_side_effect
    db.query.return_value.filter.return_value.filter.return_value.scalar.side_effect = scalar_side_effect

    # For sentiment queries (group_by)
    db.query.return_value.filter.return_value.filter.return_value.group_by.return_value.all.return_value = []

    return db


class TestTrendAnalytics:
    def test_wow_structure(self):
        db = MagicMock()
        # Mock scalar for complaint counts
        db.query.return_value.filter.return_value.filter.return_value.scalar.return_value = 5
        db.query.return_value.filter.return_value.filter.return_value.group_by.return_value.all.return_value = []

        result = compute_wow(db, reference_date=date(2026, 8, 1))
        assert "period" in result
        assert result["period"] == "weekly"
        assert "current_period" in result
        assert "previous_period" in result
        assert "complaint_count" in result

    def test_mom_structure(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.filter.return_value.scalar.return_value = 100
        db.query.return_value.filter.return_value.filter.return_value.group_by.return_value.all.return_value = []

        result = compute_mom(db, reference_date=date(2026, 8, 15))
        assert result["period"] == "monthly"
        assert "complaint_count" in result

    def test_category_trends(self):
        db = MagicMock()
        mock_rows = [("Mortgage", 50), ("Debt collection", 30)]
        # The chain: db.query(...).filter(...).group_by(...).order_by(...).all()
        db.query.return_value.filter.return_value.group_by.return_value.order_by.return_value.all.return_value = mock_rows
        result = category_trends(db, date(2026, 1, 1), date(2026, 8, 1))
        assert len(result) == 2
        assert result[0]["category"] == "Mortgage"
        assert result[0]["count"] == 50
