"""RAG retrieval testleri."""

import sys
from pathlib import Path

POC_DIR = Path(__file__).resolve().parents[1] / "poc"
sys.path.insert(0, str(POC_DIR))

from rag.indexer import index_products
from rag.retriever import hybrid_retrieve, keyword_retrieve, rerank_chunks


def test_index_products():
    count = index_products()
    assert count > 0


def test_keyword_retrieve_finds_zencefil():
    chunks = keyword_retrieve("zencefil mide bulantisi")
    assert len(chunks) >= 1
    assert any("Zencefil" in c["product_name"] for c in chunks)


def test_hybrid_retrieve_returns_products():
    index_products()
    result = hybrid_retrieve("uyku destegi melatonin")
    assert "products" in result
    assert "chunks" in result
    assert len(result["products"]) >= 1


def test_hybrid_retrieve_unknown_query():
    index_products()
    result = hybrid_retrieve("xyzabc123 nonexistent")
    assert result["chunks"] is not None


def test_reranking_improves_relevance():
    """Re-ranking katmanının çalıştığını test eder."""
    index_products()
    result = hybrid_retrieve("mide bulantisi zencefil", use_rerank=True)
    
    # Re-ranking skorları eklenmiş olmalı
    chunks = result["chunks"]
    assert len(chunks) > 0
    
    # İlk chunk'ın rerank_score'u olmalı
    assert "rerank_score" in chunks[0]
    
    # Skorlar sıralı olmalı (yüksekten düşüğe)
    scores = [c["rerank_score"] for c in chunks]
    assert scores == sorted(scores, reverse=True)


def test_reranking_field_weights():
    """Alan ağırlıklarının doğru çalıştığını test eder."""
    index_products()
    result = hybrid_retrieve("kanıt bilimsel evidence", use_rerank=True)
    
    # evidence_summary alanı daha yüksek ağırlığa sahip olmalı
    evidence_chunks = [c for c in result["chunks"] if c.get("field") == "evidence_summary"]
    other_chunks = [c for c in result["chunks"] if c.get("field") != "evidence_summary"]
    
    if evidence_chunks and other_chunks:
        # Evidence chunk'ları genellikle daha yüksek skor almalı
        avg_evidence_score = sum(c["rerank_score"] for c in evidence_chunks) / len(evidence_chunks)
        avg_other_score = sum(c["rerank_score"] for c in other_chunks) / len(other_chunks)
        assert avg_evidence_score >= avg_other_score
