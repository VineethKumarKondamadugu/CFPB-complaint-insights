"""
Ingestion trigger endpoints.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session

from src.models import get_db
from src.ingestion.file_upload import parse_upload
from src.ingestion.pipeline import ingest_record
from src.api.auth import get_current_user

router = APIRouter(prefix="/ingest", tags=["ingest"])


def _run_cfpb_ingest():
    from src.models.database import get_db as _get_db
    db = next(_get_db())
    try:
        from src.ingestion.cfpb_api import fetch_complaints
        count = 0
        for record in fetch_complaints():
            if ingest_record(db, record):
                count += 1
        return count
    finally:
        db.close()


@router.post("/cfpb")
def trigger_cfpb_ingest(
    background_tasks: BackgroundTasks,
    _user=Depends(get_current_user),
):
    background_tasks.add_task(_run_cfpb_ingest)
    return {"message": "CFPB ingestion started in background"}


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    content = await file.read()
    try:
        records = list(parse_upload(content, file.filename or "upload.csv"))
    except ValueError as exc:
        raise HTTPException(400, str(exc))

    ingested = 0
    for record in records:
        if ingest_record(db, record):
            ingested += 1
    return {"ingested": ingested, "total": len(records)}
