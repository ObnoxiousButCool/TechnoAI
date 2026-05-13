from __future__ import annotations

import logging
from typing import List

import chromadb

from src.services.vector_store.base import SearchResult, VectorRecord, VectorStore

LOGGER = logging.getLogger(__name__)


class ChromaStore(VectorStore):
    """ChromaDB implementation of VectorStore."""

    def __init__(self, collection_name: str = "techno_ai") -> None:
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )

    def initialize(self, vector_size: int) -> None:
        """No initialization required for Chroma."""
        pass

    def upsert(self, vectors: List[VectorRecord]) -> None:
        """Insert or update vectors."""

        if not vectors:
            return

        ids = [v.chunk_id for v in vectors]
        documents = [v.content for v in vectors]
        embeddings = [v.embedding for v in vectors]

        metadatas = [
            {
                "source_type": v.source_type,
                "source_id": v.source_id,
                **(v.metadata or {}),
            }
            for v in vectors
        ]

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def search(self, embedding: List[float], top_k: int) -> List[SearchResult]:
        """Search vectors using similarity."""

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]

        output: List[SearchResult] = []

        for i in range(len(documents)):
            score = 1 - distances[i] if distances else 0.0

            output.append(
                SearchResult(
                    chunk_id=ids[i],
                    content=documents[i],
                    metadata=metadatas[i] or {},
                    score=float(score),
                )
            )

        return output

    def delete(self, namespace: str) -> None:
        """Delete vectors by source_id."""

        # Chroma doesn't support direct filtered delete easily (depends on version)
        # So we fetch and delete manually

        results = self.collection.get(where={"source_id": namespace})

        ids = results.get("ids", [])

        if ids:
            self.collection.delete(ids=ids)

    def clear(self) -> int:
        """Delete all vectors in the Chroma collection."""

        deleted_count = self.collection.count()
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )
        return deleted_count
