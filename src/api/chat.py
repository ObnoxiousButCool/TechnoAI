"""Chat API routes."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from src.dependencies import get_rag_service
from src.limiter import limiter
from src.services import chat_memory

LOGGER = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Incoming chat request payload."""

    question: str = Field(..., min_length=1, max_length=4000)
    session_id: str | None = Field(default=None)


class ChatResponse(BaseModel):
    """Outgoing chat response payload."""

    answer: str
    sources: list[dict]
    session_id: str
    follow_ups: list[str] = Field(default_factory=list)


@router.post("", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat(request: Request, payload: ChatRequest) -> ChatResponse:
    """Answer a question using the RAG pipeline, with optional session memory."""

    LOGGER.info("[chat] incoming session_id=%r", payload.session_id)
    session_id = chat_memory.get_or_create_session(payload.session_id)
    history = chat_memory.get_history(session_id)
    LOGGER.info("[chat] resolved session_id=%s  history_len=%d", session_id, len(history))

    try:
        rag_service = get_rag_service()
        result = await rag_service.answer(
            question=payload.question,
            chat_history=history or None,
        )
    except Exception as exc:  # pragma: no cover - defensive API boundary
        LOGGER.exception("Chat request failed")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again.",
        ) from exc

    chat_memory.append_turn(session_id, payload.question, result["answer"])
    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        session_id=session_id,
        follow_ups=result.get("follow_ups", []),
    )


@router.delete("/session/{session_id}", tags=["chat"])
def clear_session(session_id: str) -> dict[str, str]:
    """Clear chat memory for a given session."""

    found = chat_memory.clear_session(session_id)
    if not found:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "cleared", "session_id": session_id}
