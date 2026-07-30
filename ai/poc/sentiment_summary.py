"""
Sprint 2/3 — yorum analizi standart ozet formati.

    python poc/sentiment_summary.py
    python poc/sentiment_summary.py --groq
    python poc/sentiment_summary.py --by-product
    python poc/sentiment_summary.py --product Zencefil
"""

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import List, Dict, Optional

from dotenv import load_dotenv

from groq_client import TEXT_MODEL, get_groq_client

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

COMMENTS_PATH = Path(__file__).parent / "sample_comments.json"
REPORT_DIR = Path(__file__).parent / "reports"

POSITIVE = [
    "iyi", "harika", "fayda", "arttı", "tekrar alacağım", "onayladı",
    "alternatif", "etkili", "memnun", "kolaylaştırdı", "hafifledi", "azaldı",
    "olumlu", "başarılı", "yardımcı", "destek", "rahatlat", "geçti",
    "iyileş", "düzeldi", "kurtar", "çöz", "mükemmel", "süper", "güzel",
]
NEGATIVE = [
    "faydasını görmedim", "para boşa", "bıraktım", "yan etki", "alerji",
    "yetersiz", "garip", "dikkatli", "boşa gitti", "ishal", "sersem",
    "rahatsızlık", "artırdı", "olumsuz", "başarısız", "kötü", "berbat",
    "sorun", "şikayet", "memnun değil", "işe yaramadı", "etkisiz", "kötü",
    "tehlikeli", "zarar", "endişe", "korku", "ters", "felak", "kotu",
    "ise yaramadi", "yaramadi", "calismadi", "fayda yok",
]
NEGATION_MARKERS = [" değil", " degil", " yok", " hiç ", " hic ", "ama", "fakat", "lakin"]

SIDE_EFFECT_PATTERNS = [
    (r"ba[sş]\s*a[gğ]r[ıi]s[ıi]", "baş ağrısı"),
    (r"alerj", "alerjik reaksiyon"),
    (r"mide\s*(ek[sş]imesi|bulant[ıi]|rahatsız)", "mide rahatsızlığı"),
    (r"uyu[sş]ukluk|sersem|dalg[ıi]nl[ıi]k", "uyuşukluk/dalgınlık"),
    (r"ba[sş]\s*d[oö]nmesi", "baş dönmesi"),
    (r"ishal", "ishal"),
    (r"yan\s*etki", "yan etki (belirtilmemiş)"),
    (r"kusmak|kusma", "kusma"),
    (r"kalp\s*(at[ıi][şş]|h[ıi]z)", "kalp ritmi bozukluğu"),
    (r"tansiyon\s*(y[uü]ksel|d[uü][şş])", "tansiyon değişimi"),
    (r"uyku\s*(uyan[ıi]k|sanc[ıi]s[ıi]|bozuk)", "uyku bozukluğu"),
    (r"deri\s*(dök|kaş[ıi]nt[ıi]|k[ıi]z[ıi]lk)", "deri reaksiyonu"),
    (r"nefes\s*(dar|zor)", "nefes darlığı"),
    (r"terleme", "aşırı terleme"),
    (r"titreme|tremor", "titreme"),
    (r"ağız\s*kurulu", "ağız kuruluğu"),
    (r"i[şş]tah\s*(yok|kayb)", "iştah kaybı"),
]


def load_comments() -> List[dict]:
    return json.loads(COMMENTS_PATH.read_text(encoding="utf-8"))


def _has_negation(text: str, keyword: str) -> bool:
    idx = text.find(keyword)
    if idx == -1:
        return False
    window = text[max(0, idx - 15): idx + len(keyword) + 15]
    return any(n in window for n in NEGATION_MARKERS)


def _contextual_sentiment(text: str) -> str:
    """
    Bağlam tabanlı sentiment analizi:
    - Cümle bazlı analiz
    - Negation handling
    - Intensity detection
    """
    sentences = [s.strip() for s in text.replace('.', '. ').replace('!', '! ').split('.') if s.strip()]
    
    if not sentences:
        return "neutral"
    
    sentence_scores = []
    for sentence in sentences:
        s_lower = sentence.lower()
        
        # Negation detection - cümle başındaki negation tüm cümleyi etkiler
        has_global_negation = any(n in s_lower[:20] for n in NEGATION_MARKERS)
        
        p_count = sum(1 for w in POSITIVE if w in s_lower and not _has_negation(sentence, w))
        n_count = sum(1 for w in NEGATIVE if w in s_lower and not _has_negation(sentence, w))
        
        if has_global_negation:
            # Global negation varsa skorları ters çevir
            p_count, n_count = n_count, p_count
        
        # Intensity modifiers
        intensity_boost = 0
        if any(w in s_lower for w in ["çok", "cok", "fevkalende", "tamamen", "kesinlikle"]):
            intensity_boost = 1
        
        # Sentence score
        if p_count > n_count:
            sentence_scores.append(1 + intensity_boost)
        elif n_count > p_count:
            sentence_scores.append(-1 - intensity_boost)
        else:
            sentence_scores.append(0)
    
    if not sentence_scores:
        return "neutral"
    
    avg_score = sum(sentence_scores) / len(sentence_scores)
    
    if avg_score > 0.3:
        return "positive"
    elif avg_score < -0.3:
        return "negative"
    return "neutral"


def classify_sentiment(text: str) -> str:
    # Önce basit keyword-based analiz
    t = text.lower()
    p = sum(1 for w in POSITIVE if w in t and not _has_negation(t, w))
    n = sum(1 for w in NEGATIVE if w in t and not _has_negation(t, w))
    
    # Eğer net bir sinyal varsa, doğrudan dön
    if p > n:  # Threshold düşürüldü
        return "positive"
    if n > p:
        return "negative"
    
    # Sinyal zayıfsa veya dengeliyse, contextual analizi kullan
    return _contextual_sentiment(text)


def extract_side_effects(comments: List[dict]) -> List[str]:
    found = []
    for item in comments:
        comment = item["comment"]
        lower = comment.lower()
        is_negative = classify_sentiment(comment) == "negative"
        has_side_effect_context = any(
            kw in lower for kw in ("yan etki", "alerj", "reaksiyon", "bıraktım", "yaptı")
        )
        if not (is_negative or has_side_effect_context):
            continue
        for pattern, label in SIDE_EFFECT_PATTERNS:
            if re.search(pattern, lower):
                found.append(label)
    return found


def build_distribution(comments: List[dict]) -> Dict:
    counts = Counter(classify_sentiment(item["comment"]) for item in comments)
    total = len(comments) or 1

    def bucket(key: str) -> dict:
        count = counts.get(key, 0)
        return {"count": count, "ratio": round(count / total, 3)}

    return {
        "positive": bucket("positive"),
        "negative": bucket("negative"),
        "neutral": bucket("neutral"),
        "total_comments": len(comments),
    }


def build_summary(comments: list[dict], product: str | None = None) -> dict:
    distribution = build_distribution(comments)
    side_effects = extract_side_effects(comments)
    side_counter = Counter(side_effects)
    most_reported = side_counter.most_common(1)[0][0] if side_counter else None

    pos_pct = int(distribution["positive"]["ratio"] * 100)
    neg_pct = int(distribution["negative"]["ratio"] * 100)
    neu_pct = int(distribution["neutral"]["ratio"] * 100)

    scope = f" ({product})" if product else ""
    summary_text = (
        f"{distribution['total_comments']} yorum analiz edildi{scope}. "
        f"Olumlu/olumsuz/notr oranı: %{pos_pct} olumlu, %{neg_pct} olumsuz, %{neu_pct} notr."
    )
    
    # Trend analizi
    if len(comments) >= 3:
        recent_comments = comments[-min(10, len(comments)):]
        recent_dist = build_distribution(recent_comments)
        recent_pos = int(recent_dist["positive"]["ratio"] * 100)
        recent_neg = int(recent_dist["negative"]["ratio"] * 100)
        
        trend = "stabil"
        if recent_pos > pos_pct + 10:
            trend = "olumlu yönde artış"
        elif recent_neg > neg_pct + 10:
            trend = "olumsuz yönde artış"
        
        summary_text += f" Son yorumlar trendi: {trend}."
    
    if most_reported:
        summary_text += f" En sık bildirilen yan etki: {most_reported} ({side_counter[most_reported]} kez)."

    return {
        "product": product,
        "sentiment_distribution": distribution,
        "most_reported_side_effect": most_reported,
        "side_effects": [
            {"effect": effect, "count": count}
            for effect, count in side_counter.most_common()
        ],
        "summary_text": summary_text,
        "method": "enhanced_keyword_rules",
        "confidence_score": _calculate_confidence(distribution),
    }


def _calculate_confidence(distribution: dict) -> float:
    """
    Analiz güven skorunu hesaplar:
    - Dengeli dağılım = düşük güven
    - Yönlü dağılım = yüksek güven
    - Yüksek yorum sayısı = yüksek güven
    """
    total = distribution["total_comments"]
    if total < 3:
        return 0.3
    
    pos_ratio = distribution["positive"]["ratio"]
    neg_ratio = distribution["negative"]["ratio"]
    
    # Dominance: ne kadar yönlü?
    dominance = max(pos_ratio, neg_ratio)
    
    # Volume: kaç yorum?
    volume_factor = min(1.0, total / 20)  # 20+ yorum = max volume
    
    confidence = (dominance * 0.7) + (volume_factor * 0.3)
    return round(confidence, 2)


def summarize_by_product(comments: list[dict]) -> dict[str, dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in comments:
        grouped[item.get("product", "Genel")].append(item)

    return {
        product: build_summary(items, product=product)
        for product, items in sorted(grouped.items())
    }


def enhance_with_groq(summary: dict, comments: list[dict]) -> dict:
    from openai import AuthenticationError

    client = get_groq_client()
    if not client:
        print("Groq key yok — keyword ozeti kullaniliyor.")
        return summary

    text = "\n".join(f"- {item['comment']}" for item in comments)
    schema_hint = (
        'JSON dondur: {"most_reported_side_effect": "...", '
        '"summary_text": "...", "side_effects": [{"effect":"...","count":N}]}'
    )

    try:
        r = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Bu urun yorumlarini analiz et (Turkce):\n{text}\n\n"
                        f"{schema_hint}\n"
                        "Sadece JSON yaz, baska metin ekleme."
                    ),
                }
            ],
            max_tokens=400,
            temperature=0.1,
        )
        raw = r.choices[0].message.content or ""
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            groq_data = json.loads(match.group())
            summary["most_reported_side_effect"] = groq_data.get(
                "most_reported_side_effect", summary["most_reported_side_effect"]
            )
            summary["summary_text"] = groq_data.get("summary_text", summary["summary_text"])
            if groq_data.get("side_effects"):
                summary["side_effects"] = groq_data["side_effects"]
            summary["method"] = "keyword_rules+groq"
    except (AuthenticationError, json.JSONDecodeError) as exc:
        print(f"Groq katmani atlandi: {exc}")

    return summary


def print_summary(summary: dict):
    dist = summary["sentiment_distribution"]
    title = summary.get("product") or "Tum urunler"
    print(f"=== Yorum Analizi Ozeti — {title} ===\n")
    print("Sentiment dagilimi:")
    for label, tr in [("positive", "Olumlu"), ("negative", "Olumsuz"), ("neutral", "Notr")]:
        b = dist[label]
        print(f"  {tr}: {b['count']} (%{b['ratio'] * 100:.0f})")

    print(f"\nEn sik bildirilen yan etki: {summary['most_reported_side_effect'] or '—'}")
    if summary["side_effects"]:
        print("Yan etki listesi:")
        for item in summary["side_effects"]:
            print(f"  - {item['effect']}: {item['count']} kez")

    print(f"\nOzet: {summary['summary_text']}")
    print(f"\nYontem: {summary['method']}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--groq", action="store_true", help="Groq ile yan etki/ozet iyilestir")
    parser.add_argument("--by-product", action="store_true", help="Urun bazli ozet")
    parser.add_argument("--product", type=str, help="Tek urun filtresi")
    parser.add_argument("--output", type=str, help="JSON rapor dosyasi")
    args = parser.parse_args()

    all_comments = load_comments()

    if args.product:
        comments = [c for c in all_comments if c.get("product") == args.product]
        if not comments:
            print(f"'{args.product}' icin yorum bulunamadi.")
            return
        summary = build_summary(comments, product=args.product)
        if args.groq:
            summary = enhance_with_groq(summary, comments)
        print_summary(summary)
        out_data = summary
    elif args.by_product:
        summaries = summarize_by_product(all_comments)
        for product, summary in summaries.items():
            if args.groq:
                product_comments = [c for c in all_comments if c.get("product") == product]
                summary = enhance_with_groq(summary, product_comments)
            print_summary(summary)
            print()
        out_data = {"by_product": summaries}
    else:
        summary = build_summary(all_comments)
        if args.groq:
            summary = enhance_with_groq(summary, all_comments)
        print_summary(summary)
        out_data = summary

    out_path = Path(args.output) if args.output else REPORT_DIR / "sentiment_summary.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nJSON rapor: {out_path}")


if __name__ == "__main__":
    main()
