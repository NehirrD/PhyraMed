"""Kullanıcı yorumları için açıklanabilir duygu ve yan etki analizi."""

from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any

from openai import OpenAIError

from ai.groq_client import TEXT_MODEL, extract_model_text, get_groq_client


POSITIVE = [
    "iyi",
    "harika",
    "fayda",
    "arttı",
    "tekrar alacağım",
    "onayladı",
    "alternatif",
    "etkili",
]

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


def classify_text_sentiment(text: str) -> str:
    normalized = str(text or "").lower()
    positive_score = sum(
        1 for word in POSITIVE if word in normalized
    )
    negative_score = sum(
        1 for word in NEGATIVE if word in normalized
    )

    if positive_score > negative_score:
        return "positive"
    if negative_score > positive_score:
        return "negative"
    return "neutral"


def classify_comment(item: dict[str, Any]) -> str:
    """Duygu sınıfını öncelikle kullanıcının verdiği yıldızdan çıkarır."""

    try:
        rating = int(item.get("rating"))
    except (TypeError, ValueError):
        rating = 0

    if rating >= 4:
        return "positive"
    if rating == 3:
        return "neutral"
    if 1 <= rating <= 2:
        return "negative"

    return classify_text_sentiment(str(item.get("comment") or ""))


def extract_side_effects(
    comments: list[dict[str, Any]],
) -> list[str]:
    found: list[str] = []

    for item in comments:
        comment = str(item.get("comment") or "")
        lower = comment.lower()
        has_side_effect_context = any(
            keyword in lower
            for keyword in (
                "yan etki",
                "alerj",
                "reaksiyon",
                "bıraktım",
                "yaptı",
                "baş ağrısı",
                "baş dönmesi",
                "mide",
                "uyuşukluk",
            )
        )

        if not has_side_effect_context:
            continue

        for pattern, label in SIDE_EFFECT_PATTERNS:
            if re.search(pattern, lower):
                found.append(label)

    return found


def build_distribution(
    comments: list[dict[str, Any]],
) -> dict[str, Any]:
    counts = Counter(
        classify_comment(item)
        for item in comments
    )
    total = len(comments)

    def bucket(key: str) -> dict[str, float | int]:
        count = counts.get(key, 0)
        ratio = round(count / total, 3) if total else 0.0
        return {
            "count": count,
            "ratio": ratio,
        }

    return {
        "positive": bucket("positive"),
        "negative": bucket("negative"),
        "neutral": bucket("neutral"),
        "total_comments": total,
    }


def _sample_size_warning(total_comments: int) -> str | None:
    if total_comments == 1:
        return (
            "Bu sonuç yalnızca 1 kullanıcı yorumuna dayanmaktadır; "
            "genellenemez."
        )

    if 1 < total_comments < 5:
        return (
            f"Bu sonuç sınırlı sayıdaki {total_comments} kullanıcı yorumuna "
            "dayanmaktadır."
        )

    return None


def build_summary(
    comments: list[dict[str, Any]],
) -> dict[str, Any]:
    distribution = build_distribution(comments)
    side_effects = extract_side_effects(comments)
    side_counter = Counter(side_effects)

    most_reported = (
        side_counter.most_common(1)[0][0]
        if side_counter
        else None
    )

    positive_pct = round(
        distribution["positive"]["ratio"] * 100
    )
    neutral_pct = round(
        distribution["neutral"]["ratio"] * 100
    )
    negative_pct = round(
        distribution["negative"]["ratio"] * 100
    )

    summary_text = (
        f"{distribution['total_comments']} kullanıcı yorumu incelendi. "
        f"Duygu dağılımı: %{positive_pct} olumlu, "
        f"%{neutral_pct} nötr, %{negative_pct} olumsuz."
    )

    if most_reported:
        summary_text += (
            f" En sık bildirilen olası yan etki: {most_reported}."
        )

    return {
        "sentiment_distribution": distribution,
        "most_reported_side_effect": most_reported,
        "side_effects": [
            {
                "effect": effect,
                "count": count,
            }
            for effect, count in side_counter.most_common()
        ],
        "summary_text": summary_text,
        "sample_size_warning": _sample_size_warning(
            distribution["total_comments"]
        ),
        "method": "ratings+keyword_rules",
    }


def enhance_with_groq(
    summary: dict[str, Any],
    comments: list[dict[str, Any]],
) -> dict[str, Any]:
    """Deterministik analizi Groq ile yalnızca doğal dile dönüştürür.

    Duygu dağılımı ve bildirilen olası yan etkiler kural tabanlı katmanda
    hesaplanır. Model bu alanları değiştiremez; yalnızca mevcut istatistikleri
    tarafsız ve kısa bir özet cümlesine dönüştürür.
    """

    _ = comments  # Geriye uyumlu imza; ham yorumlar modele gönderilmez.
    client = get_groq_client()
    if client is None:
        return summary

    distribution = summary.get("sentiment_distribution") or {}
    total_comments = int(distribution.get("total_comments") or 0)
    side_effects = summary.get("side_effects") or []

    safe_input = {
        "total_comments": total_comments,
        "positive_percent": round(
            float((distribution.get("positive") or {}).get("ratio") or 0) * 100
        ),
        "neutral_percent": round(
            float((distribution.get("neutral") or {}).get("ratio") or 0) * 100
        ),
        "negative_percent": round(
            float((distribution.get("negative") or {}).get("ratio") or 0) * 100
        ),
        "reported_possible_side_effects": [
            {
                "effect": str(item.get("effect") or "").strip(),
                "count": int(item.get("count") or 0),
            }
            for item in side_effects
            if str(item.get("effect") or "").strip()
        ],
        "sample_size_warning": summary.get("sample_size_warning"),
    }

    prompt = (
        "Aşağıdaki yapılandırılmış kullanıcı yorumu istatistiklerini Türkçe, "
        "tarafsız ve en fazla 3 kısa cümleyle özetle. Yeni fayda, yan etki, "
        "tanı, tedavi, doz veya ürün önerisi ekleme. Kullanıcı yorumlarının "
        "bilimsel kanıt olmadığını açıkça belirt. Yalnızca JSON döndür: "
        '{"summary_text":"..."}.\n\n'
        + json.dumps(safe_input, ensure_ascii=False)
    )

    try:
        response = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sen yalnızca verilen istatistikleri özetleyen güvenli "
                        "bir dil katmanısın. Verilmeyen hiçbir sağlık iddiası "
                        "veya tıbbi çıkarım üretme."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=240,
            temperature=0.0,
        )

        raw = extract_model_text(response.choices[0].message.content or "")
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return summary

        groq_data = json.loads(match.group())
        summary_text = str(groq_data.get("summary_text") or "").strip()
        if not summary_text or len(summary_text) > 900:
            return summary

        forbidden_fragments = (
            "kullanmalıs",
            "öneriyorum",
            "tedavi eder",
            "tedavi için",
            "doz",
            "kesinlikle güvenli",
            "doktor yerine",
        )
        normalized = summary_text.casefold()
        if any(fragment in normalized for fragment in forbidden_fragments):
            return summary

        if "bilimsel kanıt" not in normalized:
            summary_text += (
                " Bu özet kullanıcı deneyimlerini yansıtır; bilimsel kanıt "
                "veya tıbbi tavsiye değildir."
            )

        summary["summary_text"] = summary_text
        summary["method"] = "ratings+keyword_rules+groq_summary"
    except (OpenAIError, json.JSONDecodeError, TypeError, ValueError) as error:
        print(f"[sentiment] Groq özet katmanı atlandı: {error}")
    except Exception as error:
        # Harici servis veya istemci uyumsuzluğu yorum endpoint'ini 500'e düşürmez.
        print(f"[sentiment] Groq özet katmanı beklenmeyen hata nedeniyle atlandı: {error}")

    return summary

def analyze_product_comments(
    comments: list,
    use_groq: bool = False,
) -> dict[str, Any]:
    """SQLAlchemy Comment nesnelerini standart analiz çıktısına dönüştürür."""

    comment_dicts = [
        {
            "comment": str(comment.text or "").strip(),
            "rating": comment.rating,
        }
        for comment in comments
    ]

    if not comment_dicts:
        return {
            "sentiment_distribution": {
                "positive": {
                    "count": 0,
                    "ratio": 0.0,
                },
                "negative": {
                    "count": 0,
                    "ratio": 0.0,
                },
                "neutral": {
                    "count": 0,
                    "ratio": 0.0,
                },
                "total_comments": 0,
            },
            "most_reported_side_effect": None,
            "side_effects": [],
            "summary_text": "Henüz kullanıcı yorumu bulunmuyor.",
            "sample_size_warning": None,
            "method": "ratings+keyword_rules",
        }

    summary = build_summary(comment_dicts)

    if use_groq:
        summary = enhance_with_groq(
            summary,
            comment_dicts,
        )

    return summary
