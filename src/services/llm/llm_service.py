"""LLM response generation constrained to retrieved context using Ollama."""

from __future__ import annotations

import requests

# Compact prompt tuned for small instruction models: short, direct, hard rules only.
_SYSTEM_PROMPT = """\
You are Techno-AI, the AI assistant for Technossus.
Speak as Technossus. Use "we", "our", "at Technossus". Never say "they" or "the company".
Answer ONLY from the website content below. Do not use outside knowledge.
If the content does not support the answer, reply exactly:
I can help with questions based on Technossus website content. You can ask about our services, industries, case studies, leadership, or AI capabilities.

Banned phrases - never use these:
- according to
- based on
- provided context
- website content says
- it is worth noting
- not exhaustive
- additionally
- furthermore

Format rules:
- Answer in 60-90 words. Be concise.
- Plain text only.
- Never use markdown.
- Never use * or ** for any reason.
- Never number a list. Use only hyphen bullets.
- For service overview questions: maximum 6 hyphen bullets.
- For follow-up questions: answer only the one referenced item, 60-90 words.
- End with one short follow-up question only when it feels natural.\
"""


class LLMService:
    """Wrap Ollama generation with strict grounding instructions."""

    def __init__(
        self,
        base_url: str,
        model: str,
        temperature: float,
        top_p: float,
        num_predict: int,
    ) -> None:
        self._base_url = base_url
        self._model = model
        self._temperature = temperature
        self._top_p = top_p
        self._num_predict = num_predict

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
                "options": {
                    "temperature": self._temperature,
                    "top_p": self._top_p,
                    "num_predict": self._num_predict,
                },
            },
            timeout=120,
        )

        response.raise_for_status()
        data = response.json()

        return data.get("response", "").strip()