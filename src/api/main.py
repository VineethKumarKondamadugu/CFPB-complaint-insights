"""
FastAPI application entry point.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.auth import router as auth_router
from src.api.complaints import router as complaints_router
from src.api.ingest import router as ingest_router
from src.api.analytics import router as analytics_router
from src.api.reports import router as reports_router

app = FastAPI(
    title="CFPB Complaint Insights API",
    description="Internal compliance analytics platform for CFPB complaint data.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Override via ALLOWED_ORIGINS env var in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(complaints_router)
app.include_router(ingest_router)
app.include_router(analytics_router)
app.include_router(reports_router)


@app.get("/health")
def health():
    return {"status": "ok"}
