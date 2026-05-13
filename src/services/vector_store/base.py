"""Vector store abstractions."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class VectorRecord:
    """A vector payload ready for storage."""

    source_type: str
    source_id: str
    chunk_id: str
    content: str
    metadata: dict[str, Any]
    embedding: list[float]


@dataclass(slots=True)
class SearchResult:
    """A search result returned from the vector store."""

    chunk_id: str
    content: str
    metadata: dict[str, Any]
    score: float


class VectorStore(ABC):
    """Abstract vector store contract."""

    @abstractmethod
    def upsert(self, vectors: list[VectorRecord]) -> None:
        """Insert or update vectors in the store."""

    @abstractmethod
    def search(self, embedding: list[float], top_k: int) -> list[SearchResult]:
        """Search for the most similar vectors."""

    @abstractmethod
    def delete(self, namespace: str) -> None:
        """Delete vectors associated with a namespace."""

    @abstractmethod
    def clear(self) -> int:
        """Delete every vector from the store and return the deleted count."""
