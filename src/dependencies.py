"""Dependency wiring for the application."""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from src.config.settings import get_settings

if TYPE_CHECKING:
    from src.services.vector_store.azure_search_store import AzureSearchVectorStore
from src.services.crawler.sitemap_crawler import SitemapCrawler
from src.services.embeddings.embedding_service import EmbeddingService
from src.services.ingestion.file_ingestor import FileIngestor
from src.services.ingestion.pipeline import IngestionPipeline
from src.services.ingestion.website_ingestor import WebsiteIngestor
from src.services import chat_memory as _chat_memory_module
from src.services.llm.llm_service import LLMService
from src.services.rag_service import RAGService
from src.services.vector_store.base import VectorStore


@lru_cache(maxsize=1)
def get_vector_store() -> VectorStore:
    from src.services.vector_store.azure_search_store import (
        AzureSearchVectorStore,
    )
    settings = get_settings()
    return AzureSearchVectorStore(
        endpoint=settings.azure_search_endpoint,
        api_key=settings.azure_search_key,
        index_name=settings.azure_search_index,
        vector_size=settings.embedding_dimensions,
    )


@lru_cache(maxsize=1)
def get_azure_search_store() -> "AzureSearchVectorStore":
    from src.services.vector_store.azure_search_store import (
        AzureSearchVectorStore,
    )
    settings = get_settings()
    return AzureSearchVectorStore(
        endpoint=settings.azure_search_endpoint,
        api_key=settings.azure_search_key,
        index_name=settings.azure_search_index,
        vector_size=settings.embedding_dimensions,
    )


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    """Build the embedding service."""

    settings = get_settings()
    if settings.env_mode == "test":
        return EmbeddingService(
            api_key=settings.nomic_api_key,
            model=settings.nomic_embedding_model,
        )
    return EmbeddingService(
        base_url=settings.ollama_base_url,
        model=settings.ollama_embedding_model,
    )


@lru_cache(maxsize=1)
def get_llm_service() -> LLMService:
    """Build the LLM service."""

    settings = get_settings()
    if settings.env_mode == "test":
        return LLMService(
            groq_api_key=settings.groq_api_key,
            answer_model=settings.groq_answer_model,
            rewrite_model=settings.groq_rewrite_model,
            temperature=settings.ollama_temperature,
            top_p=settings.ollama_top_p,
            num_predict=settings.ollama_num_predict,
        )
    return LLMService(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        rewrite_model=settings.ollama_rewrite_model,
        temperature=settings.ollama_temperature,
        top_p=settings.ollama_top_p,
        num_predict=settings.ollama_num_predict,
    )


def get_rag_service() -> RAGService:
    """Build the RAG service."""

    settings = get_settings()
    return RAGService(
        embedding_service=get_embedding_service(),
        vector_store=get_vector_store(),
        llm_service=get_llm_service(),
        retrieval_top_k=settings.retrieval_top_k,
        retrieval_min_score=settings.retrieval_min_score,
    )


def get_chat_memory():
    """Return the chat memory module for use in graph nodes."""
    return _chat_memory_module


def get_ingestion_pipeline() -> IngestionPipeline:
    """Build the ingestion pipeline with enabled sources."""

    settings = get_settings()
    vector_store = get_vector_store()
    embedding_service = get_embedding_service()
    crawler = SitemapCrawler(
        base_url=settings.website_url,
        user_agent=settings.user_agent,
        timeout=settings.request_timeout_seconds,
        manual_urls=settings.website_urls,
    )
    sources = [
        WebsiteIngestor(
            crawler=crawler,
            embedding_service=embedding_service,
            vector_store=vector_store,
            chunk_size_words=settings.chunk_size_words,
            chunk_overlap_words=settings.chunk_overlap_words,
            enabled=settings.enable_website_ingest and bool(settings.website_url),
        ),
        FileIngestor(
            embedding_service=embedding_service,
            vector_store=vector_store,
            pdf_directory=settings.pdf_directory,
            chunk_size_words=settings.chunk_size_words,
            chunk_overlap_words=settings.chunk_overlap_words,
            enabled=settings.enable_file_ingest,
        ),
    ]
    return IngestionPipeline(sources=sources)
