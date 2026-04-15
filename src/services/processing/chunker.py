"""Chunk text into overlapping segments."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TextChunk:
    """A chunk of text and its position metadata."""

    chunk_id: str
    text: str
    start_word: int
    end_word: int


def chunk_text(
    source_id: str,
    text: str,
    chunk_size_words: int,
    chunk_overlap_words: int,
) -> list[TextChunk]:
    """Split text into overlapping chunks using words as a token proxy."""

    words = text.split()
    if not words:
        return []

    chunks: list[TextChunk] = []
    step = max(chunk_size_words - chunk_overlap_words, 1)

    for index, start in enumerate(range(0, len(words), step)):
        end = min(start + chunk_size_words, len(words))
        window = words[start:end]
        if not window:
            continue
        chunks.append(
            TextChunk(
                chunk_id=f"{source_id}::chunk::{index}",
                text=" ".join(window),
                start_word=start,
                end_word=end,
            )
        )
        if end >= len(words):
            break
    return chunks
