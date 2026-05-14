"""LLM response generation constrained to retrieved context using Ollama."""

from __future__ import annotations

import requests

# Compact prompt tuned for Llama 3.2 8B: short, direct, hard rules only.
_SYSTEM_PROMPT = """\
You are Techno-AI, the AI assistant for Technossus.
Speak as Technossus. Use "we", "our", "at Technossus". Never say "they" or "the company".
Answer ONLY from the website content below. Do not use outside knowledge.
Never say "according to the context", "based on the provided context", or mention "context".
If the content does not support the answer, reply exactly:
I can help with questions based on Technossus website content. You can ask about our services, industries, case studies, leadership, or AI capabilities.

Format rules:
- Answer in 80-120 words unless detail is requested.
- Plain text only. No markdown. No asterisks. No bold.
- Use short hyphen bullets only when listing items.
- For service overview questions: list 5-7 concise bullets.
- For follow-up questions: answer only the one referenced item.
- End with one short follow-up question only when it feels natural.\
"""


class LLMService:
    """Wrap Ollama generation with strict grounding instructions."""

    def __init__(self, model: str = "llama3:8b") -> None:
        self._model = model
        self._base_url = "http://10.30.1.34:11434"

    def answer_question(
        self,
        question: str,
        context: str,
        chat_history: list[str] | None = None,
    ) -> str:
        """Generate an answer constrained to retrieved context."""

        history_block = ""
        if chat_history:
            history_block = "Recent conversation:\n" + "\n".join(chat_history) + "\n\n"

        prompt = (
            f"{_SYSTEM_PROMPT}\n\n"
            f"{history_block}"
            f"Website content:\n{context}\n\n"
            f"Question: {question}\n"
            "Answer:"
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