"""
CFPB public API ingestion for a rolling 6-month window.
"""
from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Generator

import httpx

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

CFPB_DATE_FORMAT = "%Y-%m-%d"
PAGE_SIZE = 500


def _date_window() -> tuple[str, str]:
    end = date.today()
    start = end - timedelta(days=30 * settings.cfpb_lookback_months)
    return start.strftime(CFPB_DATE_FORMAT), end.strftime(CFPB_DATE_FORMAT)


def fetch_complaints(
    date_received_min: str | None = None,
    date_received_max: str | None = None,
) -> Generator[dict, None, None]:
    """
    Yields raw complaint dicts from the CFPB API page by page.
    """
    if not date_received_min or not date_received_max:
        date_received_min, date_received_max = _date_window()

    page = 1
    while True:
        params = {
            "date_received_min": date_received_min,
            "date_received_max": date_received_max,
            "size": PAGE_SIZE,
            "frm": (page - 1) * PAGE_SIZE,
            "sort": "created_date_desc",
        }
        try:
            resp = httpx.get(
                settings.cfpb_api_base,
                params=params,
                timeout=30.0,
            )
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("CFPB API error: %s", exc)
            break

        data = resp.json()
        hits = data.get("hits", {}).get("hits", [])
        if not hits:
            break

        for hit in hits:
            src = hit.get("_source", {})
            yield _normalize(src)

        total = data.get("hits", {}).get("total", {}).get("value", 0)
        if page * PAGE_SIZE >= total:
            break
        page += 1


def _normalize(src: dict) -> dict:
    return {
        "external_id": src.get("complaint_id"),
        "date_received": src.get("date_received"),
        "product": src.get("product"),
        "sub_product": src.get("sub_product"),
        "issue": src.get("issue"),
        "sub_issue": src.get("sub_issue"),
        "narrative": src.get("consumer_complaint_narrative"),
        "company": src.get("company"),
        "state": src.get("state"),
        "zip_code": src.get("zip_code"),
        "tags": src.get("tags"),
        "consumer_consent": src.get("consumer_consent_provided") == "Consent provided",
        "submitted_via": src.get("submitted_via"),
        "company_response": src.get("company_response_to_consumer"),
        "timely_response": src.get("timely_response") == "Yes",
        "consumer_disputed": src.get("consumer_disputed") == "Yes",
        "source": "cfpb",
    }
