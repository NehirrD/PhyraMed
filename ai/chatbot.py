"""Chatbot iş mantığı — RAG servisine güvenli giriş noktası."""

from ai.rag.service import answer_question


def get_bot_response(question: str, use_groq: bool = True) -> str:
    """Chat router'ının kullandığı geriye uyumlu fonksiyon."""

    return answer_question(question, use_groq=use_groq)
