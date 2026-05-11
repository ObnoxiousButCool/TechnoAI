"""LLM response generation constrained to retrieved context using Ollama."""

from __future__ import annotations

import requests

STRICT_SYSTEM_PROMPT = """
You are Techno-AI, a website knowledge assistant.
Answer the user using only the provided context.
Do not use outside knowledge.
If the context does not contain the answer, reply exactly with:
I can only answer questions based on the website content.
Keep answers concise and factual.
Do not mention the context or say "based on the context". Just provide the answer.
Always assume that you are a part of the company, so say "we" instead of "the company". For example, say "We have a refund policy" instead of "The company has a refund policy".
""".strip()


class LLMService:
    """Wrap Ollama generation with strict grounding instructions."""

    def __init__(self, model: str = "llama3:8b") -> None:
        self._model = model
        self._base_url = "http://10.30.1.34:11434"

    def answer_question(self, question: str, context: str) -> str:
        """Generate an answer constrained to retrieved context."""

        prompt = (
            f"{STRICT_SYSTEM_PROMPT}\n\n"
            "Context:\n"
            f"{context}\n\n"
            "Question:\n"
            f"{question}"
        )

        response = requests.post(
            f"{self._base_url}/api/generate",
            json={
                "model": self._model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
        )

        response.raise_for_status()
        data = response.json()

        return data.get("response", "").strip()