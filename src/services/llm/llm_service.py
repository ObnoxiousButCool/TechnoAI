"""LLM response generation constrained to retrieved context using Ollama."""

from __future__ import annotations

import json
import logging

import httpx

LOGGER = logging.getLogger(__name__)


def _fix_encoding(text: str) -> str:
    return (
        text.replace("â", "'")
            .replace("â", '"')
            .replace("â", '"')
    )


_SYSTEM_PROMPT = """\
You are Techno-AI, the intelligent assistant built into the Technossus
website. Speak as Technossus — use "we", "our", "at Technossus".
Never say "they" or "the company".

GROUNDING RULE — this is your most important instruction:
Answer ONLY using the website content provided below. Every claim,
statistic, name, percentage, and detail in your response MUST appear
verbatim or be directly inferable from that content. If the content
does not clearly support the answer, you MUST respond with exactly
this message and nothing else:
I can help with questions based on Technossus website content. You can ask about our services, industries, case studies, leadership, or AI capabilities.

CONTACT RULE:
This rule ONLY applies when the user's question explicitly asks for contact information, a phone number, an email address, office locations, or how to get in touch.
For ALL other questions, ignore this rule entirely and do not mention contact details.
When the rule applies, respond with exactly this and nothing else:
You can reach us at contact@technossus.com or call +1 (949) 769-3500. You can also visit our contact page at https://technossus.com/contact to fill out a form and our team will get back to you.

Never invent, estimate, or extrapolate statistics, percentages,
dates, names, or outcomes. If a number is not in the content,
it does not exist.

Banned phrases — never use these:
- according to
- based on
- provided context
- website content says
- it is worth noting
- not exhaustive
- additionally
- furthermore

Format rules:
- Answer in 60-200 words. For questions that require listing multiple items (people,
  services, case studies), use as many words as needed to cover all items completely.
  Never truncate a list.
- Use markdown where it improves readability.
- Use **bold** for names, service names, and key terms worth highlighting.
- Use hyphen bullet points when listing 3 or more items. Never use numbered lists.
- Never mix prose and bullets for the same type of content. If you start listing people,
  services, or case studies as bullets, list ALL of them as bullets — do not put some in
  prose and others in bullets.
- Each bullet must cover exactly one item (one person, one service, one case study).
- Add a blank line between paragraphs.
- Never use headers (# or ##).
- For service overview questions: list all services as hyphen bullets, one per line.
- For follow-up questions: answer only the one referenced item in prose or bullets as appropriate.
- Do not end with a question. Never append a follow-up question to your answer. Follow-up suggestions are handled separately.

If you are ever unsure whether the content supports your answer,
default to the fallback message above. An honest fallback is
better than a plausible-sounding fabrication.\
"""


class LLMService:
    """Wrap Ollama generation with strict grounding instructions."""

    def __init__(
        self,
        base_url: str,
        model: str,
        rewrite_model: str,
        temperature: float,
        top_p: float,
        num_predict: int,
    ) -> None:
        self._base_url = base_url
        self._model = model
        self._rewrite_model = rewrite_model
        self._temperature = temperature
        self._top_p = top_p
        self._num_predict = num_predict

    async def answer_question(
        self,
        question: str,
        context: str,
        chat_history: list[str] | None = None,
    ) -> str:
        """Generate an answer constrained to retrieved context."""

        history_block = ""
        if chat_history:
            history_block = "Conversation history:\n" + "\n".join(chat_history) + "\n\n"

        prompt = (
            f"{_SYSTEM_PROMPT}\n\n"
            f"{history_block}"
            f"Website content:\n{context}\n\n"
            "CRITICAL FORMAT ENFORCEMENT:\n"
            "- Use markdown: **bold** for key terms, hyphen "
            "bullets for lists of 3+ items.\n"
            "- Never use numbered lists or headers.\n"
            "- Do not repeat yourself — say each thing once.\n"
            "- Add blank lines between paragraphs.\n"
            "- No strict word limit for list-based answers. "
            "Cover all items completely. For prose answers "
            "stay under 120 words.\n"
            "- Do not start your answer with 'At Technossus'.\n\n"
            f"Question: {question}\n"
            "Answer:"
        )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
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
                return _fix_encoding(data.get("response", "").strip())
        except Exception as exc:
            LOGGER.error("[LLM] answer_question failed: %s", exc)
            return "I'm having trouble connecting right now. Please try again in a moment."

    async def generate_follow_ups(
        self,
        question: str,
        context: str,
        chat_history: list[str] | None = None,
    ) -> list[str]:
        """Generate 2-3 contextually relevant follow-up suggestions."""
        prompt = (
            "You generate follow-up topic chips for the "
            "Technossus website chatbot. These are short "
            "labels users click to explore related topics.\n\n"
            "The user just asked: " + question + "\n\n"
            "The website content used to answer was:\n"
            + context[:800] + "\n\n"
            "Generate exactly 3 follow-up topic chips.\n\n"
            "Rules:\n"
            "1. Each chip must be a natural next thing the "
            "user would want to explore after this answer\n"
            "2. 2-5 words maximum\n"
            "3. Must relate to Technossus services, "
            "industries, case studies, or leadership\n"
            "4. Each chip covers a different topic\n"
            "5. No question marks or punctuation\n"
            "6. Sound like something a user would click, "
            "not a tagline or internal term\n"
            "7. Never suggest a chip that repeats or closely "
            "rephrases what the user just asked. The user "
            "just asked: " + question + " — do not suggest "
            "anything similar to this.\n\n"
            "Context-specific guidance:\n"
            "- After a services answer → suggest specific "
            "service deep-dives or industries served\n"
            "- After a leadership answer → suggest a "
            "specific leader, case studies, or services\n"
            "- After a case study answer → suggest another "
            "industry, a specific service, or contact\n"
            "- After a contact answer → suggest services "
            "or case studies\n\n"
            "GOOD examples for a services question:\n"
            "[\"AI transformation\", \"Healthcare work\", "
            "\"Case studies\"]\n\n"
            "GOOD examples for a leadership question:\n"
            "[\"Kumar Gaurav\", \"Our case studies\", "
            "\"AI services\"]\n\n"
            "BAD examples: [\"Accelerate Vision\", "
            "\"Strategy Technology Execution\", "
            "\"Investment Accountability\"]\n\n"
            "Return ONLY a JSON array of 3 strings.\n"
            "JSON array:"
        )
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self._base_url}/api/generate",
                    json={
                        "model": self._rewrite_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.4,
                            "num_predict": 80,
                        },
                    },
                    timeout=15,
                )
                response.raise_for_status()
                raw = response.json().get("response", "").strip()
                raw = raw.strip("```json").strip("```").strip()
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [_fix_encoding(str(s)) for s in parsed[:3]]
                return []
        except Exception as exc:
            LOGGER.warning("[LLM] follow_ups generation failed: %s", exc)
            return []

    async def rewrite_query(self, question: str, chat_history: list[str]) -> str | None:
        """Rewrite a vague follow-up into a standalone search query.

        Returns a short query string, or None if the call fails or returns empty.
        Uses temperature=0 and a small token budget — this is a lookup, not generation.
        """
        FOLLOW_UP_SIGNALS = (
            "first", "second", "third", "fourth", "fifth", "sixth",
            "that", "this", "it", "the one", "previous", "last",
            "more", "tell me more", "explain", "elaborate", "expand",
            "which", "what about", "how about",
        )
        question_lower = question.lower()
        if not any(signal in question_lower for signal in FOLLOW_UP_SIGNALS):
            return None

        history_text = "\n".join(chat_history)
        prompt = (
            "Given the conversation history and the latest user message, "
            "rewrite the latest user message into a short, specific, "
            "standalone search query. Resolve any pronouns or references "
            "like 'the first one', 'that service', 'it' using the "
            "conversation above.\n\n"
            "Return only the search query.\n"
            "No explanation.\n"
            "No markdown.\n\n"
            f"Conversation so far:\n{history_text}\n\n"
            f"Latest message:\n{question}\n\n"
            "Search query:"
        )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self._base_url}/api/generate",
                    json={
                        "model": self._rewrite_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.0,
                            "num_predict": 50,
                        },
                    },
                    timeout=30,
                )
            response.raise_for_status()
            result = response.json().get("response", "").strip()
            # Take only the first line and strip stray quotes/backticks
            result = result.split("\n")[0].strip().strip("\"'`")
            return result or None
        except Exception as exc:
            LOGGER.warning("[LLM] query rewrite failed: %s", exc)
            return None
