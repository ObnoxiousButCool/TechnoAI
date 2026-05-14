"""Website ingestion source."""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from urllib.parse import urlparse

from src.services.crawler.sitemap_crawler import SitemapCrawler
from src.services.embeddings.embedding_service import EmbeddingService
from src.services.processing.chunker import chunk_text
from src.services.processing.cleaner import clean_html
from src.services.vector_store.base import VectorRecord, VectorStore

LOGGER = logging.getLogger(__name__)

# URL path segment → page_type label
_PATH_TYPE_MAP: list[tuple[str, str]] = [
    ("/services/", "service"),
    ("/industries/", "industry"),
    ("/case-studies", "case_study"),
    ("/about", "about"),
    ("/careers", "careers"),
    ("/contact", "contact"),
]


def _page_metadata(url: str) -> dict:
    """Return page_type and service_name metadata derived from the URL path."""
    path = urlparse(url).path.rstrip("/")
    page_type = "other"
    for prefix, label in _PATH_TYPE_MAP:
        if prefix in path:
            page_type = label
            break
    if path in ("/", ""):
        page_type = "home"

    meta: dict = {"page_type": page_type}
    if page_type == "service":
        # e.g. /services/data-intelligence-analytics → data-intelligence-analytics
        meta["service_name"] = path.split("/services/", 1)[-1]
    return meta


@dataclass(slots=True)
class IngestionResult:
    """Summarize an ingestion run."""

    source_name: str
    processed_items: int
    stored_chunks: int

    def to_dict(self) -> dict:
        """Convert the result to a plain dictionary."""

        return asdict(self)


class WebsiteIngestor:
    """Crawl a website sitemap and store embedded chunks."""

    source_name = "website"

    def __init__(
        self,
        crawler: SitemapCrawler,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
        chunk_size_words: int,
        chunk_overlap_words: int,
        enabled: bool,
    ) -> None:
        self._crawler = crawler
        self._embedding_service = embedding_service
        self._vector_store = vector_store
        self._chunk_size_words = chunk_size_words
        self._chunk_overlap_words = chunk_overlap_words
        self._enabled = enabled

    def is_enabled(self) -> bool:
        """Return whether website ingestion should run."""

        return self._enabled

    def ingest(self) -> IngestionResult:
        """Run website ingestion and upsert chunks."""

        urls = self._crawler.discover_urls()
        stored_chunks = 0

        for url in urls:
            try:
                html = self._crawler.fetch_page(url)
                cleaned_text = clean_html(html)
                LOGGER.info(
                    "Cleaned text at %s: %d chars", url, len(cleaned_text)
                )
                if not cleaned_text:
                    continue

                source_id = self._normalize_source_id(url)
                self._vector_store.delete(source_id)
                chunks = chunk_text(
                    source_id=source_id,
                    text=cleaned_text,
                    chunk_size_words=self._chunk_size_words,
                    chunk_overlap_words=self._chunk_overlap_words,
                )
                embeddings = self._embedding_service.embed_texts(
                    [chunk.text for chunk in chunks]
                )
                page_meta = _page_metadata(url)
                records = [
                    VectorRecord(
                        source_type=self.source_name,
                        source_id=source_id,
                        chunk_id=chunk.chunk_id,
                        content=chunk.text,
                        metadata={
                            "url": url,
                            "start_word": chunk.start_word,
                            "end_word": chunk.end_word,
                            **page_meta,
                        },
                        embedding=embedding,
                    )
                    for chunk, embedding in zip(chunks, embeddings, strict=False)
                ]
                self._vector_store.upsert(records)
                stored_chunks += len(records)
                LOGGER.info("Ingested %s chunks from %s", len(records), url)
            except Exception:
                LOGGER.exception("Failed to ingest page: %s", url)

        self._crawler.close()
        return IngestionResult(
            source_name=self.source_name,
            processed_items=len(urls),
            stored_chunks=stored_chunks,
        )

    @staticmethod
    def _normalize_source_id(url: str) -> str:
        parsed = urlparse(url)
        path = parsed.path.rstrip("/") or "/"
        return f"{parsed.netloc}{path}"
