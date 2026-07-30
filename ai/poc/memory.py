"""Oturum bazlı konuşma hafızası — çok turlu chatbot için."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4
from typing import List, Optional, Dict


@dataclass
class Turn:
    role: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SessionMemory:
    """In-memory oturum deposu (production'da Redis/DB ile değiştirilebilir)."""

    def __init__(self, max_turns: int = 20):
        self.max_turns = max_turns
        self._sessions: Dict[str, List[Turn]] = {}

    def create_session(self) -> str:
        session_id = str(uuid4())
        self._sessions[session_id] = []
        return session_id

    def add_turn(self, session_id: str, role: str, content: str) -> None:
        if session_id not in self._sessions:
            self._sessions[session_id] = []

        self._sessions[session_id].append(Turn(role=role, content=content))

        if len(self._sessions[session_id]) > self.max_turns:
            self._sessions[session_id] = self._sessions[session_id][-self.max_turns :]

    def get_turns(self, session_id: str) -> List[Turn]:
        return list(self._sessions.get(session_id, []))

    def get_messages(self, session_id: str, max_turns: Optional[int] = None) -> List[dict]:
        """OpenAI/Groq messages formatında geçmiş döndürür."""

        turns = self.get_turns(session_id)
        if max_turns:
            turns = turns[-max_turns:]

        return [{"role": t.role, "content": t.content} for t in turns]

    def clear(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def summarize_context(self, session_id: str) -> str:
        """Uzun oturumlar için kısa bağlam özeti."""

        turns = self.get_turns(session_id)
        if not turns:
            return ""

        user_questions = [t.content for t in turns if t.role == "user"]
        if not user_questions:
            return ""

        return "Önceki konuşma konuları: " + "; ".join(user_questions[-3:])


# Global singleton — API ve CLI paylaşır
memory_store = SessionMemory()
