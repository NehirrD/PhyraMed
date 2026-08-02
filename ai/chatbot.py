"""Chatbot iş mantığı — RAG servisine güvenli giriş noktası."""

from collections.abc import Sequence
from typing import Any

from ai.rag.service import answer_question


def get_bot_response(
    question: str,
    *,
    history: Sequence[dict[str, Any]] | None = None,
    use_groq: bool = True,
) -> str:
    """Chat router'ının kullandığı geriye uyumlu fonksiyon."""

    return answer_question(
        question,
        history=history,
        use_groq=use_groq,
    )
