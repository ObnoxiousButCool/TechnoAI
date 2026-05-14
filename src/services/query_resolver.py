"""Lightweight follow-up query resolver.

Rewrites short follow-up questions into standalone retrieval queries by
resolving references like "the first service" or "that case study" using
the most recent assistant response in chat history.
"""

from __future__ import annotations

import re

_ORDINAL_MAP: dict[str, int] = {
    "first": 1, "1st": 1,
    "second": 2, "2nd": 2,
    "third": 3, "3rd": 3,
    "fourth": 4, "4th": 4,
    "fifth": 5, "5th": 5,
}

# Phrases that signal the user is referencing something from history
_VAGUE_REF_RE = re.compile(
    r"\b(that|this|the previous|the last|that one|this one|it)\b",
    re.IGNORECASE,
)

# Verbs that signal a follow-up elaboration request
_ELABORATION_RE = re.compile(
    r"\b(explain|tell me( more)? about|what is|what about|describe|elaborate|more on|"
    r"more about|detail|expand on|go deeper)\b",
    re.IGNORECASE,
)


def _last_assistant_text(history: list[str]) -> str | None:
    """Return the most recent assistant response text from history."""
    for entry in reversed(history):
        if entry.startswith("assistant responded: "):
            return entry[len("assistant responded: "):]
    return None


def _numbered_items(text: str) -> list[str]:
    """Extract items from a numbered list in assistant response text."""
    items = []
    for match in re.finditer(r'(?m)^\s*(\d+)[.)]\s*(.+)', text):
        # Strip markdown bold/italic asterisks
        item = re.sub(r'\*+', '', match.group(2)).strip()
        # Take only up to the first colon or dash (heading part)
        item = re.split(r'\s*[:\-–]\s*', item)[0].strip()
        if item:
            items.append(item)
    return items


def _first_topic(text: str) -> str | None:
    """Extract a short topic label from the first meaningful line."""
    for line in text.splitlines():
        line = re.sub(r'\*+', '', line).strip().lstrip("-•·").strip()
        if len(line) > 8:
            topic = re.split(r'\s*[:\-–,]\s*', line)[0].strip()
            if topic:
                return topic[:80]
    return None


CLARIFY_MSG = (
    "Could you clarify which one you mean? "
    "I mentioned a few items — just let me know which you'd like me to expand on."
)


def resolve(question: str, history: list[str] | None) -> tuple[str, bool]:
    """Rewrite a follow-up question for vector retrieval.

    Returns:
        (retrieval_query, needs_clarification)
        - retrieval_query: rewritten query to embed (original if no rewrite needed)
        - needs_clarification: True if caller should return CLARIFY_MSG as the answer
    """
    if not history:
        return question, False

    lower_q = question.lower().strip()

    # Detect ordinal reference ("first", "second", ...)
    ordinal = None
    for word, idx in _ORDINAL_MAP.items():
        if re.search(r'\b' + re.escape(word) + r'\b', lower_q):
            ordinal = idx
            break

    last_text = _last_assistant_text(history)
    if not last_text:
        return question, False

    if ordinal is not None:
        items = _numbered_items(last_text)
        if items and ordinal <= len(items):
            return f"{items[ordinal - 1]} Technossus", False
        # Ordinal mentioned but no list found — fall through

    # Detect vague reference or elaboration verb
    has_vague = bool(_VAGUE_REF_RE.search(lower_q))
    has_elaboration = bool(_ELABORATION_RE.search(lower_q))

    if has_vague or has_elaboration:
        items = _numbered_items(last_text)
        if len(items) == 1:
            return f"{items[0]} Technossus", False
        if len(items) > 1:
            return question, True  # ambiguous — ask to clarify
        # No numbered list — grab first topic line
        topic = _first_topic(last_text)
        if topic:
            return f"{topic} Technossus", False

    return question, False
