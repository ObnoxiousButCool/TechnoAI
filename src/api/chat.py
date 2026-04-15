"""Chat API routes."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.dependencies import get_rag_service

LOGGER = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Incoming chat request payload."""

    question: str = Field(..., min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    """Outgoing chat response payload."""

    answer: str
    sources: list[dict]


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    """Answer a question using the RAG pipeline."""

    try:
        rag_service = get_rag_service()
        result = rag_service.answer(payload.question)
        return ChatResponse(**result)
    except Exception as exc:  # pragma: no cover - defensive API boundary
        LOGGER.exception("Chat request failed")
        raise HTTPException(
            status_code=500,
            detail=f"Unable to process chat request: {exc}",
        ) from exc
