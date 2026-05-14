"""RAG query orchestration."""

from __future__ import annotations

import logging
import re

from src.services.embeddings.embedding_service import EmbeddingService
from src.services.llm.llm_service import LLMService
from src.services.query_resolver import CLARIFY_MSG, resolve
from src.services.vector_store.base import SearchResult, VectorStore

LOGGER = logging.getLogger(__name__)

FALLBACK_RESPONSE = (
    "I can help with questions based on Technossus website content. "
    "You can ask about our services, industries, case studies, leadership, or AI capabilities."
)

# Canonical service list — deterministic, so the answer is always consistent
# and follow-up ordinal resolution ("explain the first point") is reliable.
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

        # Short-circuit for service overview questions — return canonical list so
        # the answer is always consistent and follow-up ordinal resolution works.
        if _is_service_overview(question):
            print(f"[DEBUG] service overview intercept for: {question!r}")
            return {"answer": _SERVICE_OVERVIEW_ANSWER, "sources": []}

        # Resolve follow-up references before vector search
        retrieval_query, needs_clarification = resolve(question, chat_history)
        rewritten = retrieval_query != question

        LOGGER.info("[RAG] original question: %r", question)
        LOGGER.info("[RAG] retrieval query:   %r", retrieval_query)
        print(f"[DEBUG] original question : {question!r}")
        print(f"[DEBUG] retrieval query   : {retrieval_query!r}")

        if needs_clarification:
            return {"answer": CLARIFY_MSG, "sources": []}

        query_embedding = self._embedding_service.embed_text(retrieval_query)
        search_results = self._vector_store.search(
            embedding=query_embedding,
            top_k=self._retrieval_top_k,
        )
        relevant_results = [
            result
            for result in search_results
            if result.score >= self._retrieval_min_score
        ]

        for r in relevant_results:
            src = r.metadata.get("url") or r.metadata.get("file_name", "?")
            LOGGER.info("[RAG] retrieved: score=%.3f  source=%s", r.score, src)
            print(f"[DEBUG] chunk score={r.score:.3f} source={src}")
            print(f"[DEBUG] chunk preview: {r.content[:300]!r}")

        if not relevant_results:
            LOGGER.info("[RAG] no results above min_score threshold")
            return {"answer": FALLBACK_RESPONSE, "sources": []}

        # Use the resolved query as the LLM question when a rewrite happened,
        # so the model answers the specific topic rather than the ambiguous original.
        llm_question = retrieval_query if rewritten else question

        context = self._build_context(relevant_results)
        answer = self._llm_service.answer_question(
            question=llm_question,
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
