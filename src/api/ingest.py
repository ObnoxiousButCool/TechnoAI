"""Ingestion API routes."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.dependencies import get_ingestion_pipeline, get_vector_store

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


@router.delete("/vectors", response_model=ClearVectorStoreResponse)
def clear_vectors() -> ClearVectorStoreResponse:
    """Clear all previously ingested vector content."""

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
            detail=f"Unable to clear vector store: {exc}",
        ) from exc
