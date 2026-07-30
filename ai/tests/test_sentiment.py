"""Sentiment analizi testleri."""

import sys
from pathlib import Path

POC_DIR = Path(__file__).resolve().parents[1] / "poc"
sys.path.insert(0, str(POC_DIR))

from sentiment_summary import (
    build_summary,
    classify_sentiment,
    load_comments,
    summarize_by_product,
)


def test_classify_positive():
    assert classify_sentiment("Cok memnun kaldim, iyi geldi.") == "positive"


def test_classify_negative():
    assert classify_sentiment("Hic faydasini gormedim, para bosa.") == "negative"


def test_classify_negation():
    assert classify_sentiment("Iyi degil, fayda saglamadi.") == "neutral"


def test_classify_contextual_positive():
    """Bağlam tabanlı pozitif analiz testi."""
    assert classify_sentiment("Gerçekten çok etkili, harika bir ürün.") == "positive"


def test_classify_contextual_negative():
    """Bağlam tabanlı negatif analiz testi."""
    assert classify_sentiment("Kesinlikle işe yaramadı, para boşa gitti.") == "negative"


def test_classify_mixed_sentiment():
    """Karışık sentiment için neutral dönmesi beklenir."""
    assert classify_sentiment("Bir kısımda iyi, diğer kısımda kötü.") == "neutral"


def test_enhanced_side_effect_detection():
    """Geliştirilmiş yan etki tespiti testi."""
    test_comment = "Baş dönmesi yaşadım, mide bulantısı başladı."
    from sentiment_summary import extract_side_effects
    comments = [{"comment": test_comment, "product": "Test"}]
    effects = extract_side_effects(comments)
    assert len(effects) > 0
    assert any("baş dönmesi" in effect or "mide" in effect for effect in effects)


def test_summarize_by_product():
    comments = load_comments()
    summaries = summarize_by_product(comments)
    assert "Zencefil" in summaries
    assert summaries["Zencefil"]["product"] == "Zencefil"
    assert summaries["Zencefil"]["sentiment_distribution"]["total_comments"] >= 1


def test_build_summary_structure():
    comments = load_comments()
    summary = build_summary(comments)
    assert "sentiment_distribution" in summary
    assert "side_effects" in summary
    assert "summary_text" in summary
    assert "confidence_score" in summary  # Yeni eklenen alan


def test_build_summary_includes_trend():
    """Trend analizi eklenmiş olmalı."""
    comments = load_comments()
    if len(comments) >= 3:
        summary = build_summary(comments)
        assert "trend" in summary["summary_text"].lower() or "yorumlar" in summary["summary_text"].lower()


def test_confidence_score_calculation():
    """Güven skoru hesaplaması testi."""
    from sentiment_summary import _calculate_confidence
    distribution = {
        "positive": {"count": 10, "ratio": 0.8},
        "negative": {"count": 2, "ratio": 0.2},
        "neutral": {"count": 0, "ratio": 0.0},
        "total_comments": 12
    }
    confidence = _calculate_confidence(distribution)
    assert 0 <= confidence <= 1
    assert confidence > 0.5  # Yüksek dominance, yüksek güven
