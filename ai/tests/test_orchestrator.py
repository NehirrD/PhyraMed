"""Orchestrator ve memory testleri."""

import sys
from pathlib import Path

POC_DIR = Path(__file__).resolve().parents[1] / "poc"
sys.path.insert(0, str(POC_DIR))

from memory import SessionMemory
from orchestrator import orchestrate
from rag.indexer import index_products


def test_orchestrate_returns_structured_response():
    index_products()
    result = orchestrate("Zencefil mide bulantisi", use_groq=False)

    assert "answer" in result
    assert "source" in result
    assert "sources" in result
    assert "retrieved_chunks" in result
    assert "session_id" in result
    assert result["source"] == "verified_db"
    assert len(result["sources"]) >= 1


def test_session_memory_persists_turns():
    memory = SessionMemory(max_turns=10)
    session_id = memory.create_session()

    orchestrate("Uyku icin ne var?", session_id=session_id, use_groq=False, memory=memory)
    orchestrate("Yan etkileri neler?", session_id=session_id, use_groq=False, memory=memory)

    turns = memory.get_turns(session_id)
    assert len(turns) == 4  # 2 user + 2 assistant


def test_orchestrate_unknown_product():
    index_products()
    result = orchestrate("Ashwagandha nedir?", use_groq=False)
    assert result["source"] == "ai_generated"
