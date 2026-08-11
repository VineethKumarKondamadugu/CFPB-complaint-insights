"""
CSV export generation.
"""
from __future__ import annotations

import csv
import io
from typing import Iterable


def generate_csv(
    rows: Iterable[dict],
    fieldnames: list[str] | None = None,
) -> bytes:
    """Generate CSV bytes from a list of dicts."""
    rows_list = list(rows)
    if not rows_list:
        return b""

    if fieldnames is None:
        fieldnames = list(rows_list[0].keys())

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows_list)
    return buffer.getvalue().encode("utf-8")
