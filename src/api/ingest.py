"""Ingestion API routes."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.dependencies import get_ingestion_pipeline

LOGGER = logging.getLogger(__name__)
router = APIRouter(prefix="/ingest", tags=["ingestion"])


class IngestResponse(BaseModel):
    """Ingestion run response."""

    status: str
    results: list[dict]


@router.post("/run", response_model=IngestResponse)
def run_ingestion() -> IngestResponse:
    """Execute enabled ingestion sources."""

    try:
        pipeline = get_ingestion_pipeline()
        results = pipeline.run()
        return IngestResponse(status="success", results=results)
    except Exception as exc:  # pragma: no cover - defensive API boundary
        LOGGER.exception("Ingestion request failed")
        raise HTTPException(
            status_code=500,
            detail=f"Unable to run ingestion: {exc}",
        ) from exc
