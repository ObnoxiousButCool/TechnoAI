"""RAG query orchestration."""

from __future__ import annotations

import logging
import re

from src.services.embeddings.embedding_service import EmbeddingService
from src.services.llm.llm_service import LLMService
from src.services.vector_store.base import SearchResult, VectorStore

LOGGER = logging.getLogger(__name__)

FALLBACK_RESPONSE = (
    "I can help with questions based on Technossus website content. "
    "You can ask about our services, industries, case studies, leadership, or AI capabilities."
)

# Canonical service list — deterministic, so the answer is always consistent
# and follow-up ordinal resolution works reliably.
_CANONICAL_SERVICES = [
    "AI Business Transformation",
    "Cloud & Product Modernization",
    "Data Intelligence & Analytics",
    "Digital Experience Design",
    "Product Engineering",
    "Quality Engineering",
]

_SERVICE_OVERVIEW_ANSWER = (
    "At Technossus, we offer six core service areas:\n\n"
    + "\n".join(f"{i + 1}. {s}" for i, s in enumerate(_CANONICAL_SERVICES))
    + "\n\nWould you like me to go deeper into any of these?"
)

# Matches common ways a user asks for the services list
_SERVICE_OVERVIEW_RE = re.compile(
    r"\b("
    r"what services|which services|list (your |the )?services|"
    r"services (do you|does technossus|you) offer|"
    r"what do you offer|what (can|does) technossus (do|offer|help)|"
    r"(your |the )?services (you |technossus )?(provide|have)|"
    r"tell me (about )?(your |the )?services|"
    r"overview of (your |the )?services"
    r")\b",
    re.IGNORECASE,
)


def _is_service_overview(question: str) -> bool:
    return bool(_SERVICE_OVERVIEW_RE.search(question))


# Maps canonical service name substrings → URL slug fragment.
# Used to boost retrieval precision when a rewrite query names a specific service.
_SERVICE_SLUG_MAP: list[tuple[str, str]] = [
    ("ai business transformation", "ai-business-transformation"),
    ("cloud & product modernization", "cloud-product-modernization"),
    ("cloud and product modernization", "cloud-product-modernization"),
    ("data intelligence & analytics", "data-intelligence-analytics"),
    ("data intelligence and analytics", "data-intelligence-analytics"),
    ("digital experience design", "digital-experience-design"),
    ("product engineering", "product-engineering"),
    ("quality engineering", "quality-engineering"),
]


def _service_slug_for_query(query: str) -> str | None:
    """Return the URL slug if the query clearly names one specific service."""
    lower = query.lower()
    for name, slug in _SERVICE_SLUG_MAP:
        if name in lower:
            return slug
    return None


class RAGService:
    """Retrieve relevant chunks and generate grounded responses."""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
        llm_service: LLMService,
        retrieval_top_k: int,
        retrieval_min_score: float,
    ) -> None:
        self._embedding_service = embedding_service
        self._vector_store = vector_store
        self._llm_service = llm_service
        self._retrieval_top_k = retrieval_top_k
        self._retrieval_min_score = retrieval_min_score

    def answer(self, question: str, chat_history: list[str] | None = None) -> dict:
        """Run the RAG pipeline and return the assistant answer."""

        # Deterministic intercept — always consistent, no LLM needed.
        if _is_service_overview(question):
            LOGGER.info("[RAG] service overview intercept")
            print(f"[DEBUG] service overview intercept for: {question!r}")
            return {"answer": _SERVICE_OVERVIEW_ANSWER, "sources": []}

        history = chat_history or []

        LOGGER.info("[RAG] user message: %r", question)
        print(f"[DEBUG] user message        : {question!r}")
        print(f"[DEBUG] history passed      : {len(history)} entries")
        for entry in history:
            print(f"[DEBUG]   {entry[:120]!r}")

        # SLM rewrite — always fires before retrieval.
        # The SLM resolves ordinals ("3rd one"), vague refs ("yes please",
        # "tell me more"), and explicit questions alike. Falls back to the
        # raw user message if the call fails or returns empty output.
        retrieval_query = (
            self._llm_service.rewrite_query(question, history) or question
        )
        LOGGER.info("[RAG] retrieval query: %r", retrieval_query)
        print(f"[DEBUG] retrieval query     : {retrieval_query!r}")

        query_embedding = self._embedding_service.embed_text(retrieval_query)
        search_results = self._vector_store.search(
            embedding=query_embedding,
            top_k=self._retrieval_top_k,
        )

        # Debug: show all raw results before any filtering
        print(f"[DEBUG] raw results ({len(search_results)} chunks):")
        for r in search_results:
            src = r.metadata.get("url") or r.metadata.get("file_name", "?")
            print(f"[DEBUG]   score={r.score:.4f}  url={src}")
            print(f"[DEBUG]   preview: {r.content[:250]!r}")

        relevant_results = [
            r for r in search_results if r.score >= self._retrieval_min_score
        ]

        # URL-based service boost: when the rewrite query names a specific service,
        # prefer chunks from that service's page. Falls back to all relevant results
        # if no matching chunks are found (e.g. page not yet ingested).
        service_slug = _service_slug_for_query(retrieval_query)
        if service_slug:
            service_chunks = [
                r for r in relevant_results
                if service_slug in (r.metadata.get("url") or "")
            ]
            if service_chunks:
                LOGGER.info(
                    "[RAG] url-boost: slug=%s narrowed %d → %d chunks",
                    service_slug, len(relevant_results), len(service_chunks),
                )
                print(
                    f"[DEBUG] url-boost: slug={service_slug!r} "
                    f"narrowed {len(relevant_results)} → {len(service_chunks)} chunks"
                )
                relevant_results = service_chunks
            else:
                LOGGER.info("[RAG] url-boost: slug=%s not found in results, keeping all", service_slug)
                print(f"[DEBUG] url-boost: slug={service_slug!r} not found, keeping all results")

        if not relevant_results:
            LOGGER.info("[RAG] no results above min_score threshold")
            return {"answer": FALLBACK_RESPONSE, "sources": []}

        print(f"[DEBUG] final chunks passed to LLM ({len(relevant_results)}):")
        for r in relevant_results:
            src = r.metadata.get("url") or r.metadata.get("file_name", "?")
            LOGGER.info("[RAG] retrieved: score=%.4f  source=%s", r.score, src)
            print(f"[DEBUG]   score={r.score:.4f}  url={src}")

        context = self._build_context(relevant_results)
        # Original question goes to the answer prompt; the SLM rewrite was
        # retrieval-only. Chat history gives the LLM enough context to understand
        # what the user meant by vague follow-ups.
        answer = self._llm_service.answer_question(
            question=question,
            context=context,
            chat_history=chat_history,
        )
        if not answer:
            answer = FALLBACK_RESPONSE
        return {
            "answer": answer,
            "sources": [
                {
                    "chunk_id": result.chunk_id,
                    "score": result.score,
                    "metadata": result.metadata,
                }
                for result in relevant_results
            ],
        }

    @staticmethod
    def _build_context(results: list[SearchResult]) -> str:
        context_parts = []
        for result in results:
            source_ref = result.metadata.get("url") or result.metadata.get(
                "file_name",
                "",
            )
            context_parts.append(f"Source: {source_ref}\nContent: {result.content}")
        return "\n\n".join(context_parts)
