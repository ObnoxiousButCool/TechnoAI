"""RAG query orchestration."""

from __future__ import annotations
from venv import logger

from src.services.embeddings.embedding_service import EmbeddingService
from src.services.llm.llm_service import LLMService
from src.services.vector_store.base import SearchResult, VectorStore

FALLBACK_RESPONSE = "I can only answer questions based on the website content."


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

    def answer(self, question: str) -> dict:
        """Run the RAG pipeline and return the assistant answer."""

        query_embedding = self._embedding_service.embed_text(question)
        search_results = self._vector_store.search(
            embedding=query_embedding,
            top_k=self._retrieval_top_k,
        )
        relevant_results = [
            result
            for result in search_results
            if result.score >= self._retrieval_min_score
        ]
        # logger.info(
        #     "RAG search found %d relevant results for question: %s. Results: %s",
        #     len(relevant_results),
        #     question,
        #     relevant_results,
        # )
        if not relevant_results:
            return {
                "answer": FALLBACK_RESPONSE,
                "sources": [],
            }

        context = self._build_context(relevant_results)
        answer = self._llm_service.answer_question(question=question, context=context)
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
