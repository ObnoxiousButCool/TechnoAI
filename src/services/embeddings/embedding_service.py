"""Embedding generation service using Ollama."""

from __future__ import annotations

import requests


class EmbeddingService:
    """Wrap embedding model calls using Ollama."""

    def __init__(self, base_url: str, model: str) -> None:
        self._base_url = base_url
        self._model = model

    def embed_text(self, text: str) -> list[float]:
        """Generate a single embedding."""

        response = requests.post(
            f"{self._base_url}/api/embeddings",
            json={
                "model": self._model,
                "prompt": text,
            },
            timeout=60,
        )

        response.raise_for_status()
        data = response.json()

        return data.get("embedding", [])

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""

        if not texts:
            return []

        embeddings = []
        for text in texts:
            embeddings.append(self.embed_text(text))

        return embeddings