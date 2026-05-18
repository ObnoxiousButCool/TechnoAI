"""Ingestion API routes."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

from src.config.settings import get_settings
from src.dependencies import get_ingestion_pipeline, get_vector_store

_api_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)

LOGGER = logging.getLogger(__name__)
router = APIRouter(prefix="/ingest", tags=["ingestion"])


class IngestResponse(BaseModel):
    """Ingestion run response."""

    status: str
    results: list[dict]


class ClearVectorStoreResponse(BaseModel):
    """Vector store clear response."""

    status: str
    deleted_count: int


@router.post("/run", response_model=IngestResponse)
def run_ingestion(api_key: str | None = Security(_api_key_header)) -> IngestResponse:
    """Execute enabled ingestion sources."""

    if api_key != get_settings().admin_api_key:
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        pipeline = get_ingestion_pipeline()
        results = pipeline.run()
        return IngestResponse(status="success", results=results)
    except Exception as exc:  # pragma: no cover - defensive API boundary
        LOGGER.exception("Ingestion request failed")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again.",
        ) from exc


@router.delete("/vectors", response_model=ClearVectorStoreResponse)
def clear_vectors(api_key: str | None = Security(_api_key_header)) -> ClearVectorStoreResponse:
    """Clear all previously ingested vector content."""

    if api_key != get_settings().admin_api_key:
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        deleted_count = get_vector_store().clear()
        return ClearVectorStoreResponse(
            status="success",
            deleted_count=deleted_count,
        )
    except Exception as exc:  # pragma: no cover - defensive API boundary
        LOGGER.exception("Vector store clear request failed")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again.",
        ) from exc
