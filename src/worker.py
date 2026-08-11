"""
Celery worker configuration and scheduled tasks.
"""
from __future__ import annotations

import logging
from celery import Celery
from celery.schedules import crontab

from config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

app = Celery("cfpb_insights", broker=settings.redis_url, backend=settings.redis_url)

app.conf.beat_schedule = {
    "weekly-cfpb-ingest": {
        "task": "src.worker.run_cfpb_ingest",
        "schedule": crontab(hour=2, minute=0, day_of_week="monday"),
    },
    "monthly-cfpb-ingest": {
        "task": "src.worker.run_cfpb_ingest",
        "schedule": crontab(hour=3, minute=0, day_of_month="1"),
    },
}
app.conf.timezone = "UTC"
app.conf.task_acks_late = True
app.conf.task_reject_on_worker_lost = True


@app.task(name="src.worker.run_cfpb_ingest", bind=True, max_retries=3, default_retry_delay=300)
def run_cfpb_ingest(self):
    """Ingest rolling 6-month CFPB complaint data."""
    try:
        from src.models.database import get_sessionmaker
        from src.ingestion.cfpb_api import fetch_complaints
        from src.ingestion.pipeline import ingest_record

        SessionLocal = get_sessionmaker()
        db = SessionLocal()
        count = 0
        try:
            for record in fetch_complaints():
                if ingest_record(db, record):
                    count += 1
        finally:
            db.close()

        logger.info("CFPB ingest complete: %d new records", count)
        return {"ingested": count}
    except Exception as exc:
        logger.error("CFPB ingest failed: %s", exc)
        raise self.retry(exc=exc)
