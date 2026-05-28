"""Embedding generation service supporting Ollama and Nomic Atlas."""

from __future__ import annotations

import requests


_NOMIC_API_URL = "https://api-atlas.nomic.ai/v1/embedding/text"


class EmbeddingService:
    """Generate embeddings via Ollama (prod) or Nomic Atlas (dev)."""

    def __init__(
        self,
        provider: str,
        model: str,
        base_url: str = "",
        api_key: str = "",
    ) -> None:
        self._provider = provider
        self._model = model
        self._base_url = base_url
        self._api_key = api_key

    def embed_text(self, text: str) -> list[float]:
        """Generate a single embedding."""
        if self._provider == "nomic":
            return self._embed_nomic([text])[0]
        return self._embed_ollama(text)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        if not texts:
            return []
        if self._provider == "nomic":
            return self._embed_nomic(texts)
        return [self._embed_ollama(t) for t in texts]

    def _embed_ollama(self, text: str) -> list[float]:
        response = requests.post(
            f"{self._base_url}/api/embeddings",
            json={"model": self._model, "prompt": text},
            timeout=60,
        )
        response.raise_for_status()
        return response.json().get("embedding", [])

    def _embed_nomic(self, texts: list[str]) -> list[list[float]]:
        response = requests.post(
            _NOMIC_API_URL,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self._model,
                "texts": texts,
                "task_type": "search_document",
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json().get("embeddings", [])
