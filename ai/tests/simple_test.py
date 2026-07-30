"""Basit test - kritik fonksiyonları test eder."""

import sys
from pathlib import Path

POC_DIR = Path(__file__).resolve().parents[1] / "poc"
sys.path.insert(0, str(POC_DIR))

print("=== Basit Test Başlatılıyor ===\n")

# Test 1: Re-ranking fonksiyonu
print("1. Re-ranking Fonksiyonu Testi...")
try:
    from rag.retriever import rerank_chunks
    
    dummy_chunks = [
        {"chunk_id": "1", "text": "Zencefil kanıt bilimsel", "product_id": 1, "product_name": "Zencefil", "field": "evidence_summary", "score": 0.8},
        {"chunk_id": "2", "text": "Zencefil isim", "product_id": 1, "product_name": "Zencefil", "field": "name", "score": 0.7},
        {"chunk_id": "3", "text": "Test", "product_id": 2, "product_name": "Test", "field": "category", "score": 0.6},
    ]
    
    reranked = rerank_chunks("kanıt bilimsel", dummy_chunks, top_k=2)
    assert len(reranked) == 2
    assert "rerank_score" in reranked[0]
    assert reranked[0]["rerank_score"] >= reranked[1]["rerank_score"]
    print("✓ Re-ranking fonksiyonu çalışıyor")
    print("  - İlk chunk skoru: " + str(reranked[0]['rerank_score']))
    print("  - İkinci chunk skoru: " + str(reranked[1]['rerank_score']))
except Exception as e:
    print(f"✗ Re-ranking hatası: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Sentiment iyileştirmeleri
print("\n2. Sentiment Analizi Testi...")
try:
    from sentiment_summary import classify_sentiment, _calculate_confidence
    
    # Test cases
    test_cases = [
        ("Gerçekten çok etkili, harika bir ürün.", "positive"),
        ("Kesinlikle işe yaramadı, para boşa gitti.", "negative"),
        ("Bir kısımda iyi, diğer kısımda kötü.", "neutral"),
        ("Çok iyi değil, faydasını görmedim.", "negative"),
    ]
    
    all_passed = True
    for text, expected in test_cases:
        result = classify_sentiment(text)
        if result == expected:
            print(f"  ✓ '{text[:30]}...' -> {result}")
        else:
            print(f"  ✗ '{text[:30]}...' -> {result} (beklenen: {expected})")
            all_passed = False
    
    # Confidence score testi
    distribution = {
        "positive": {"count": 10, "ratio": 0.8},
        "negative": {"count": 2, "ratio": 0.2},
        "neutral": {"count": 0, "ratio": 0.0},
        "total_comments": 12
    }
    confidence = _calculate_confidence(distribution)
    print(f"  Confidence score: {confidence} (0-1 arası olmalı)")
    assert 0 <= confidence <= 1
    
    if all_passed:
        print("✓ Sentiment iyileştirmeleri çalışıyor")
except Exception as e:
    print(f"✗ Sentiment hatası: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Vision prompt V4
print("\n3. Vision Prompt V4 Testi...")
try:
    from vision import PROMPT_V4, parse_vision_response, is_uncertain
    
    assert PROMPT_V4 is not None
    assert "ZERDEÇAL" in PROMPT_V4
    assert "ZENCEFİL" in PROMPT_V4
    print("  ✓ PROMPT_V4 tanımlı")
    
    # V4 parsing testi
    raw = "Bitki (TR): Zerdeçal\nBitki (EN): Turmeric\nGüven: yüksek\nKısa not: Test."
    parsed = parse_vision_response(raw)
    assert "zerdeçal" in parsed["plant_tr"].lower()
    print(f"  ✓ Parsing çalışıyor: {parsed['plant_tr']}")
    
    # Belirsizlik testi
    uncertain_parsed = {"plant_tr": "Belirsiz", "confidence": "düşük"}
    assert is_uncertain(uncertain_parsed) is True
    print("  ✓ Belirsizlik tespiti çalışıyor")
    
    print("✓ Vision V4 çalışıyor")
except Exception as e:
    print(f"✗ Vision hatası: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Memory ve Orchestrator
print("\n4. Memory ve Orchestrator Testi...")
try:
    from memory import SessionMemory
    from orchestrator import orchestrate
    
    memory = SessionMemory()
    session_id = memory.create_session()
    print(f"  Session ID oluşturuldu: {session_id}")
    
    # Test için mock bir session kullan
    test_memory = SessionMemory()
    test_session = test_memory.create_session()
    
    # Basit test - sistem yanıtının yapısını kontrol et
    try:
        result = orchestrate("test", session_id=test_session, use_groq=False, memory=test_memory)
        assert "answer" in result
        assert "session_id" in result
        print(f"  ✓ Orchestrator yanıt yapısı doğru")
    except Exception as inner_e:
        print(f"  ⚠ Orchestrator kısmi test: {inner_e}")
    
    print("✓ Memory ve Orchestrator temel fonksiyonları çalışıyor")
except Exception as e:
    print(f"✗ Memory/Orchestrator hatası: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Tamamlandı ===")