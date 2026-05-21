"""Embedding generation using Nomic Atlas API."""

from __future__ import annotations

import logging

import httpx

LOGGER = logging.getLogger(__name__)

NOMIC_API_URL = "https://api-atlas.nomic.ai/v1/embedding/text"


class EmbeddingService:
    """Wrap Nomic Atlas embedding API calls."""

    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def embed_text(self, text: str) -> list[float]:
        """Generate a single embedding synchronously."""
        return self.embed_texts([text])[0]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts in one
        API call — Nomic supports batch requests."""
        if not texts:
            return []
        with httpx.Client(timeout=60) as client:
            response = client.post(
                NOMIC_API_URL,
                headers=self._headers,
                json={
                    "model": self._model,
                    "texts": texts,
                    "task_type": "search_document",
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["embeddings"]

    def embed_query(self, text: str) -> list[float]:
        """Embed a search query — uses search_query
        task type for better retrieval performance."""
        with httpx.Client(timeout=60) as client:
            response = client.post(
                NOMIC_API_URL,
                headers=self._headers,
                json={
                    "model": self._model,
                    "texts": [text],
                    "task_type": "search_query",
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["embeddings"][0]
