"""In-memory session-based chat history store (demo use only)."""

from __future__ import annotations

from collections import deque
from uuid import uuid4

_MAX_TURNS = 6  # keep last 6 messages (3 user + 3 assistant pairs)

# session_id -> deque of formatted history strings
_store: dict[str, deque[str]] = {}


def get_or_create_session(session_id: str | None) -> str:
    """Return existing session_id or create a new one."""
    if not session_id:
        session_id = str(uuid4())
    if session_id not in _store:
        _store[session_id] = deque(maxlen=_MAX_TURNS)
    return session_id


def get_history(session_id: str) -> list[str]:
    """Return the chat history for a session as a list of strings."""
    return list(_store.get(session_id, []))


def append_turn(session_id: str, question: str, answer: str) -> None:
    """Add a user/assistant turn to the session history."""
    if session_id not in _store:
        _store[session_id] = deque(maxlen=_MAX_TURNS)
    _store[session_id].append(f"User: {question}")
    _store[session_id].append(f"Assistant: {answer}")


def clear_session(session_id: str) -> bool:
    """Delete a session's history. Returns True if it existed."""
    if session_id in _store:
        del _store[session_id]
        return True
    return False
