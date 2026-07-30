"""Minimal test - import sorunlarını atlar."""

import sys
from pathlib import Path

# Direct path setup
script_dir = Path(__file__).resolve().parent
poc_dir = script_dir.parent / "poc"
sys.path.insert(0, str(poc_dir))

print("=== Test Suite Started ===")
print("Script dir:", script_dir)
print("POC dir:", poc_dir)
print("POC exists:", poc_dir)

# Test 1: RAG Re-ranking
print("\n--- Test 1: RAG Re-ranking ---")
try:
    from rag.retriever import rerank_chunks
    print("[OK] Import successful")
    
    chunks = [
        {"chunk_id": "1", "text": "Zencefil kanıt bilimsel", "product_id": 1, "product_name": "Zencefil", "field": "evidence_summary", "score": 0.8},
        {"chunk_id": "2", "text": "Zencefil isim", "product_id": 1, "product_name": "Zencefil", "field": "name", "score": 0.7},
        {"chunk_id": "3", "text": "Test diger", "product_id": 2, "product_name": "Test", "field": "category", "score": 0.6},
    ]
    result = rerank_chunks("kanıt bilimsel", chunks, top_k=2)
    print("[OK] Function execution successful")
    print("Top results:", len(result))
    for i, r in enumerate(result):
        print(f"  {i+1}. Score: {r['rerank_score']:.3f}, Field: {r['field']}")
    
except Exception as e:
    print("[ERROR] RAG test failed:", e)
    import traceback
    traceback.print_exc()

# Test 2: Sentiment Analysis
print("\n--- Test 2: Sentiment Analysis ---")
try:
    from sentiment_summary import classify_sentiment, _calculate_confidence
    print("[OK] Import successful")
    
    test_cases = [
        ("Cok iyi, harika", "positive"),
        ("Kotu, bozuk, ise yaramadi", "negative"),
        ("Fena degil ama", "neutral"),
    ]
    
    for text, expected in test_cases:
        result = classify_sentiment(text)
        status = "[OK]" if result == expected else "[MISMATCH]"
        print(f"{status} '{text}' -> {result} (expected: {expected})")
    
    # Confidence test
    dist = {"positive": {"count": 10, "ratio": 0.8}, "negative": {"count": 2, "ratio": 0.2}, "neutral": {"count": 0, "ratio": 0.0}, "total_comments": 12}
    conf = _calculate_confidence(dist)
    print(f"[OK] Confidence score: {conf:.2f}")
    
except Exception as e:
    print("[ERROR] Sentiment test failed:", e)
    import traceback
    traceback.print_exc()

# Test 3: Vision
print("\n--- Test 3: Vision ---")
try:
    from vision import PROMPT_V4, parse_vision_response, is_uncertain
    print("[OK] Import successful")
    
    if PROMPT_V4 and "ZERDEÇAL" in PROMPT_V4:
        print("[OK] PROMPT_V4 contains ZERDEÇAL")
    else:
        print("[ERROR] PROMPT_V4 issue")
    
    raw = "Bitki (TR): Zencefil\nBitki (EN): Ginger\nGüven: yüksek\nKısa not: Test"
    parsed = parse_vision_response(raw)
    print(f"[OK] Parsing: {parsed['plant_tr']}")
    
    uncertain = {"plant_tr": "Belirsiz", "confidence": "düşük"}
    if is_uncertain(uncertain):
        print("[OK] Uncertainty detection works")
    
except Exception as e:
    print("[ERROR] Vision test failed:", e)
    import traceback
    traceback.print_exc()

print("\n=== Test Suite Completed ===")