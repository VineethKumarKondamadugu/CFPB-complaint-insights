"""
CSV / XLSX file upload ingestion.
"""
from __future__ import annotations

import io
from typing import Generator

import pandas as pd


REQUIRED_COLUMNS = {"date_received", "narrative"}

COLUMN_ALIASES = {
    "date": "date_received",
    "received": "date_received",
    "complaint_date": "date_received",
    "complaint": "narrative",
    "text": "narrative",
    "description": "narrative",
    "feedback": "narrative",
}


def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df.rename(columns=COLUMN_ALIASES, inplace=True)
    return df


def parse_upload(file_bytes: bytes, filename: str) -> Generator[dict, None, None]:
    """Parse CSV or XLSX and yield normalized complaint dicts."""
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext == "csv":
        df = pd.read_csv(io.BytesIO(file_bytes))
    elif ext in ("xlsx", "xls"):
        df = pd.read_excel(io.BytesIO(file_bytes))
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    df = _normalise_columns(df)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    for _, row in df.iterrows():
        rec: dict = {"source": "upload"}
        for col in df.columns:
            val = row[col]
            try:
                rec[col] = None if pd.isna(val) else val
            except (ValueError, TypeError):
                rec[col] = val
        yield rec
