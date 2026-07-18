"""
Sprint 2 — yorum analizi standart özet formatı.

Çıktı JSON şeması:
  - sentiment_distribution (olumlu/olumsuz/nötr oranları)
  - most_reported_side_effect
  - side_effects (sıklık listesi)
  - summary_text

    python poc/sentiment_summary.py
    python poc/sentiment_summary.py --groq
    python poc/sentiment_summary.py --output reports/summary.json
"""

import argparse
import json

import re
from collections import Counter
from pathlib import Path


from dotenv import load_dotenv

from groq_client import TEXT_MODEL, get_groq_client

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

COMMENTS_PATH = Path(__file__).parent / "sample_comments.json"
REPORT_DIR = Path(__file__).parent / "reports"

POSITIVE = ["iyi", "harika", "fayda", "arttı", "tekrar alacağım", "onayladı", "alternatif", "etkili"]
NEGATIVE = [
    "faydasını görmedim",
    "para boşa",
    "bıraktım",
    "yan etki",
    "alerji",
    "yetersiz",
    "garip",
    "dikkatli",
    "boşa gitti",
]

SIDE_EFFECT_PATTERNS = [
    (r"ba[sş]\s*a[gğ]r[ıi]s[ıi]", "baş ağrısı"),
    (r"alerj", "alerjik reaksiyon"),
    (r"mide\s*(ek[sş]imesi|bulant)", "mide rahatsızlığı"),
    (r"uyu[sş]ukluk", "uyuşukluk"),
    (r"ba[sş]\s*d[oö]nmesi", "baş dönmesi"),
    (r"yan\s*etki", "yan etki (belirtilmemiş)"),
]


def load_comments() -> list[dict]:
    return json.loads(COMMENTS_PATH.read_text(encoding="utf-8"))


def classify_sentiment(text: str) -> str:
    t = text.lower()
    p = sum(1 for w in POSITIVE if w in t)
    n = sum(1 for w in NEGATIVE if w in t)
    if p > n:
        return "positive"
    if n > p:
        return "negative"
    return "neutral"


def extract_side_effects(comments: list[str]) -> list[str]:
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


def build_distribution(comments: list[dict]) -> dict:
    counts = Counter(
        classify_sentiment(item["comment"])
        for item in comments
    )

    total = len(comments) or 1

    def bucket(key: str) -> dict:
        count = counts.get(key, 0)
        return {
            "count": count,
            "ratio": round(count / total, 3)
        }

    return {
        "positive": bucket("positive"),
        "negative": bucket("negative"),
        "neutral": bucket("neutral"),
        "total_comments": len(comments),
    }
def build_summary(comments: list[dict]) -> dict:
    distribution = build_distribution(comments)
    side_effects = extract_side_effects(comments)
    side_counter = Counter(side_effects)

    most_reported = side_counter.most_common(1)[0][0] if side_counter else None

    pos_pct = int(distribution["positive"]["ratio"] * 100)
    neg_pct = int(distribution["negative"]["ratio"] * 100)

    summary_text = (
        f"{distribution['total_comments']} yorum analiz edildi. "
        f"Olumlu/olumsuz oranı: %{pos_pct} olumlu, %{neg_pct} olumsuz."
    )
    if most_reported:
        summary_text += f" En sık bildirilen yan etki: {most_reported}."

    return {
        "sentiment_distribution": distribution,
        "most_reported_side_effect": most_reported,
        "side_effects": [
            {"effect": effect, "count": count}
            for effect, count in side_counter.most_common()
        ],
        "summary_text": summary_text,
        "method": "keyword_rules",
    }

def enhance_with_groq(summary: dict, comments: list[dict]) -> dict:
    from openai import AuthenticationError

    client = get_groq_client()
    if not client:
        print("Groq key yok — keyword özeti kullanılıyor.")
        return summary

    text = "\n".join(
        f"- {item['comment']}"
        for item in comments
    )
    schema_hint = (
        'JSON döndür: {"most_reported_side_effect": "...", '
        '"summary_text": "...", "side_effects": [{"effect":"...","count":N}]}'
    )

    try:
        r = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Bu ürün yorumlarını analiz et (Türkçe):\n{text}\n\n"
                        f"{schema_hint}\n"
                        "Sadece JSON yaz, başka metin ekleme."
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
        print(f"Groq katmanı atlandı: {exc}")

    return summary


def print_summary(summary: dict):
    dist = summary["sentiment_distribution"]
    print("=== Yorum Analizi Özeti (Sprint 2) ===\n")
    print("Sentiment dağılımı:")
    for label, tr in [("positive", "Olumlu"), ("negative", "Olumsuz"), ("neutral", "Nötr")]:
        b = dist[label]
        print(f"  {tr}: {b['count']} (%{b['ratio'] * 100:.0f})")

    print(f"\nEn sık bildirilen yan etki: {summary['most_reported_side_effect'] or '—'}")
    if summary["side_effects"]:
        print("Yan etki listesi:")
        for item in summary["side_effects"]:
            print(f"  - {item['effect']}: {item['count']} kez")

    print(f"\nÖzet: {summary['summary_text']}")
    print(f"\nYöntem: {summary['method']}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--groq", action="store_true", help="Groq ile yan etki/özet iyileştir")
    parser.add_argument("--output", type=str, help="JSON rapor dosyası")
    args = parser.parse_args()

    comments = load_comments()
    summary = build_summary(comments)

    if args.groq:
        summary = enhance_with_groq(summary, comments)

    print_summary(summary)

    out_path = Path(args.output) if args.output else REPORT_DIR / "sentiment_summary.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nJSON rapor: {out_path}")


if __name__ == "__main__":
    main()
