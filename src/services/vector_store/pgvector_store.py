"""PostgreSQL vector store implementation using pgvector."""

from __future__ import annotations

import json
import logging
from contextlib import contextmanager
from typing import Iterator

from pgvector.psycopg import register_vector
from psycopg import connect
from psycopg.rows import dict_row

from src.services.vector_store.base import SearchResult, VectorRecord, VectorStore

LOGGER = logging.getLogger(__name__)


class PGVectorStore(VectorStore):
    """Persist vectors in PostgreSQL with pgvector."""

    def __init__(self, database_url: str) -> None:
        self._database_url = database_url

    @contextmanager
    def _connection(self) -> Iterator:
        connection = connect(self._database_url, row_factory=dict_row)
        register_vector(connection)
        try:
            yield connection
        finally:
            connection.close()

    def initialize(self, vector_size: int) -> None:
        """Create required database objects."""

        with self._connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                cursor.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS document_chunks (
                        id TEXT PRIMARY KEY,
                        source_type TEXT NOT NULL,
                        source_id TEXT NOT NULL,
                        content TEXT NOT NULL,
                        metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb,
                        embedding VECTOR({vector_size}) NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                    """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS document_chunks_source_id_idx
                    ON document_chunks (source_id);
                    """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS document_chunks_source_type_idx
                    ON document_chunks (source_type);
                    """
                )
            connection.commit()

    def upsert(self, vectors: list[VectorRecord]) -> None:
        """Insert or update vectors in PostgreSQL."""

        if not vectors:
            return

        query = """
            INSERT INTO document_chunks (
                id,
                source_type,
                source_id,
                content,
                metadata,
                embedding,
                updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (id) DO UPDATE
            SET source_type = EXCLUDED.source_type,
                source_id = EXCLUDED.source_id,
                content = EXCLUDED.content,
                metadata = EXCLUDED.metadata,
                embedding = EXCLUDED.embedding,
                updated_at = NOW();
        """
        rows = [
            (
                record.chunk_id,
                record.source_type,
                record.source_id,
                record.content,
                json.dumps(record.metadata),
                record.embedding,
            )
            for record in vectors
        ]

        with self._connection() as connection:
            with connection.cursor() as cursor:
                cursor.executemany(query, rows)
            connection.commit()

    def search(self, embedding: list[float], top_k: int) -> list[SearchResult]:
        """Search vectors by cosine similarity."""

        query = """
            SELECT
                id,
                content,
                metadata,
                1 - (embedding <=> %s) AS score
            FROM document_chunks
            ORDER BY embedding <=> %s
            LIMIT %s;
        """
        with self._connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (embedding, embedding, top_k))
                rows = cursor.fetchall()

        return [
            SearchResult(
                chunk_id=row["id"],
                content=row["content"],
                metadata=row["metadata"] or {},
                score=float(row["score"]),
            )
            for row in rows
        ]

    def delete(self, namespace: str) -> None:
        """Delete vectors for a given source identifier."""

        with self._connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM document_chunks WHERE source_id = %s;",
                    (namespace,),
                )
            connection.commit()

    def clear(self) -> int:
        """Delete every vector from PostgreSQL."""

        with self._connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM document_chunks;")
                deleted_count = cursor.rowcount
            connection.commit()

        return deleted_count
