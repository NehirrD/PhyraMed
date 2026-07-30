"""Hızlı test script - testleri manuel çalıştırır."""

import sys
from pathlib import Path

# Path setup
AI_DIR = Path(__file__).resolve().parents[1]
POC_DIR = AI_DIR / "poc"
sys.path.insert(0, str(POC_DIR))

print("=== Test Başlatılıyor ===")
print(f"POC_DIR: {POC_DIR}")
print(f"AI_DIR: {AI_DIR}\n")

# Test 1: RAG re-ranking
print("1. RAG Re-ranking Testi...")
try:
    from rag.retriever import rerank_chunks, hybrid_retrieve
    from rag.indexer import index_products
    
    # Basit rerank testi
    dummy_chunks = [
        {"chunk_id": "1", "text": "Zencefil kanıt", "product_id": 1, "product_name": "Zencefil", "field": "evidence_summary", "score": 0.8},
        {"chunk_id": "2", "text": "Zencefil isim", "product_id": 1, "product_name": "Zencefil", "field": "name", "score": 0.7},
    ]
    
    reranked = rerank_chunks("kanıt bilimsel", dummy_chunks, top_k=2)
    assert "rerank_score" in reranked[0]
    assert reranked[0]["rerank_score"] >= reranked[1]["rerank_score"]
    print("✓ Re-ranking çalışıyor")
except Exception as e:
    print(f"✗ Re-ranking hatası: {e}")

# Test 2: Sentiment iyileştirmeleri
print("\n2. Sentiment Analizi Testi...")
try:
    from sentiment_summary import classify_sentiment, _calculate_confidence
    
    # Contextual sentiment testi
    assert classify_sentiment("Gerçekten çok etkili, harika bir ürün.") == "positive"
    assert classify_sentiment("Kesinlikle işe yaramadı, para boşa gitti.") == "negative"
    assert classify_sentiment("Bir kısımda iyi, diğer kısımda kötü.") == "neutral"
    
    # Confidence score testi
    distribution = {
        "positive": {"count": 10, "ratio": 0.8},
        "negative": {"count": 2, "ratio": 0.2},
        "neutral": {"count": 0, "ratio": 0.0},
        "total_comments": 12
    }
    confidence = _calculate_confidence(distribution)
    assert 0 <= confidence <= 1
    print("✓ Sentiment iyileştirmeleri çalışıyor")
except Exception as e:
    print(f"✗ Sentiment hatası: {e}")

# Test 3: Vision prompt V4
print("\n3. Vision Prompt V4 Testi...")
try:
    from vision import PROMPT_V4, parse_vision_response, is_uncertain
    
    assert PROMPT_V4 is not None
    assert "ZERDEÇAL" in PROMPT_V4
    assert "ZENCEFİL" in PROMPT_V4
    
    # V4 parsing testi
    raw = "Bitki (TR): Zerdeçal\nBitki (EN): Turmeric\nGüven: yüksek\nKısa not: Test."
    parsed = parse_vision_response(raw)
    assert "zerdeçal" in parsed["plant_tr"].lower()
    
    # Belirsizlik testi
    uncertain_parsed = {"plant_tr": "Belirsiz", "confidence": "düşük"}
    assert is_uncertain(uncertain_parsed) is True
    
    print("✓ Vision V4 çalışıyor")
except Exception as e:
    print(f"✗ Vision hatası: {e}")

# Test 4: Orchestrator entegrasyonu
print("\n4. Orchestrator Testi...")
try:
    from orchestrator import orchestrate
    from memory import SessionMemory
    
    memory = SessionMemory()
    session_id = memory.create_session()
    
    # Basit template test (Groq olmadan)
    result = orchestrate("test", session_id=session_id, use_groq=False, memory=memory)
    
    assert "answer" in result
    assert "session_id" in result
    assert result["session_id"] == session_id
    
    print("✓ Orchestrator çalışıyor")
except Exception as e:
    print(f"✗ Orchestrator hatası: {e}")

print("\n=== Test Tamamlandı ===")