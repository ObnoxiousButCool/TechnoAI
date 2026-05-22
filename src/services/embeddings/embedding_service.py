"""Embedding generation — supports Ollama (dev) and Nomic Atlas (test/prod)."""

from __future__ import annotations

import logging

import httpx

LOGGER = logging.getLogger(__name__)

_NOMIC_API_URL = "https://api-atlas.nomic.ai/v1/embedding/text"


class EmbeddingService:
    """Wrap embedding calls — Ollama when base_url set, Nomic when api_key set."""

    def __init__(
        self,
        base_url: str = "",
        model: str = "",
        api_key: str = "",
    ) -> None:
        self._nomic_mode = bool(api_key)
        self._base_url = base_url
        self._model = model
        # Headers only used in Nomic mode; set unconditionally for mypy.
        self._headers: dict[str, str] = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def embed_text(self, text: str) -> list[float]:
        """Generate a single embedding (document task type)."""
        return self.embed_texts([text])[0]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Nomic supports true batch requests; Ollama is called once per text.
        """
        if not texts:
            return []

        if self._nomic_mode:
            with httpx.Client(timeout=60) as client:
                response = client.post(
                    _NOMIC_API_URL,
                    headers=self._headers,
                    json={
                        "model": self._model,
                        "texts": texts,
                        "task_type": "search_document",
                    },
                )
                response.raise_for_status()
                return response.json()["embeddings"]
        else:
            embeddings = []
            for text in texts:
                with httpx.Client(timeout=60) as client:
                    response = client.post(
                        f"{self._base_url}/api/embeddings",
                        json={"model": self._model, "prompt": text},
                    )
                    response.raise_for_status()
                    embeddings.append(response.json().get("embedding", []))
            return embeddings

    def embed_query(self, text: str) -> list[float]:
        """Embed a search query.

        Uses Nomic's search_query task type for better retrieval performance.
        Falls back to embed_text for Ollama (no query-specific endpoint).
        """
        if not self._nomic_mode:
            return self.embed_text(text)

        with httpx.Client(timeout=60) as client:
            response = client.post(
                _NOMIC_API_URL,
                headers=self._headers,
                json={
                    "model": self._model,
                    "texts": [text],
                    "task_type": "search_query",
                },
            )
            response.raise_for_status()
            return response.json()["embeddings"][0]
