"""RAG destekli chatbot fonksiyonu - backend entegrasyonu için."""

import sys
from pathlib import Path

# AI modülünü path'e ekle
AI_DIR = Path(__file__).resolve().parent
POC_DIR = AI_DIR / "poc"
if str(POC_DIR) not in sys.path:
    sys.path.insert(0, str(POC_DIR))

from orchestrator import orchestrate
from memory import memory_store


def get_bot_response(message: str, session_id: str = "default") -> str:
    """
    Backend chat endpoint'i için RAG destekli yanıt üretir.
    
    Args:
        message: Kullanıcı mesajı
        session_id: Oturum ID'si (hafıza için)
    
    Returns:
        Yanıt metni
    """
    try:
        result = orchestrate(
            question=message,
            session_id=session_id,
            use_groq=True  # Groq kullanımı
        )
        return result["answer"]
    except Exception as e:
        print(f"Chatbot hatası: {e}")
        return "Üzgünüm, bir hata oluştu. Lütfen daha sonra tekrar deneyin."


def clear_session(session_id: str) -> bool:
    """Oturum hafızasını temizler."""
    try:
        memory_store.clear(session_id)
        return True
    except Exception as e:
        print(f"Oturum temizleme hatası: {e}")
        return False