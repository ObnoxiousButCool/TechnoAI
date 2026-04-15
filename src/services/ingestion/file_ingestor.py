"""Optional PDF ingestion source."""

from __future__ import annotations

import logging
from pathlib import Path

from pypdf import PdfReader

from src.services.embeddings.embedding_service import EmbeddingService
from src.services.processing.chunker import chunk_text
from src.services.vector_store.base import VectorRecord, VectorStore

LOGGER = logging.getLogger(__name__)


class FileIngestor:
    """Read PDFs from a directory and store embedded chunks."""

    source_name = "file"

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
        pdf_directory: str,
        chunk_size_words: int,
        chunk_overlap_words: int,
        enabled: bool,
    ) -> None:
        self._embedding_service = embedding_service
        self._vector_store = vector_store
        self._pdf_directory = pdf_directory
        self._chunk_size_words = chunk_size_words
        self._chunk_overlap_words = chunk_overlap_words
        self._enabled = enabled

    def is_enabled(self) -> bool:
        """Return whether file ingestion should run."""

        return self._enabled

    def ingest(self) -> dict:
        """Run PDF ingestion for all files in the configured directory."""

        directory = Path(self._pdf_directory)
        if not directory.exists():
            LOGGER.warning("PDF directory does not exist: %s", directory)
            return {
                "source_name": self.source_name,
                "processed_items": 0,
                "stored_chunks": 0,
            }

        pdf_files = sorted(directory.glob("*.pdf"))
        stored_chunks = 0

        for pdf_file in pdf_files:
            try:
                reader = PdfReader(str(pdf_file))
                text = " ".join(
                    page.extract_text() or "" for page in reader.pages
                ).strip()
                if not text:
                    continue

                source_id = f"file::{pdf_file.stem}"
                self._vector_store.delete(source_id)
                chunks = chunk_text(
                    source_id=source_id,
                    text=text,
                    chunk_size_words=self._chunk_size_words,
                    chunk_overlap_words=self._chunk_overlap_words,
                )
                embeddings = self._embedding_service.embed_texts(
                    [chunk.text for chunk in chunks]
                )
                records = [
                    VectorRecord(
                        source_type=self.source_name,
                        source_id=source_id,
                        chunk_id=chunk.chunk_id,
                        content=chunk.text,
                        metadata={"file_name": pdf_file.name},
                        embedding=embedding,
                    )
                    for chunk, embedding in zip(chunks, embeddings, strict=False)
                ]
                self._vector_store.upsert(records)
                stored_chunks += len(records)
                LOGGER.info("Ingested %s chunks from %s", len(records), pdf_file.name)
            except Exception:
                LOGGER.exception("Failed to ingest PDF: %s", pdf_file)

        return {
            "source_name": self.source_name,
            "processed_items": len(pdf_files),
            "stored_chunks": stored_chunks,
        }
