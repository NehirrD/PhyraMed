"""
Sprint 1 — basit yorum analizi (Sprint 3'te guncellendi).

    python sentiment_test.py
    python sentiment_test.py --groq
"""

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from groq_client import TEXT_MODEL, get_groq_client
from sentiment_summary import classify_sentiment, load_comments

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

LABEL_MAP = {"positive": "Olumlu", "negative": "Olumsuz", "neutral": "Nötr"}


def run_simple():
    comments = load_comments()
    counts = {"Olumlu": 0, "Olumsuz": 0, "Nötr": 0}

    print("=== Basit kelime yontemi (Sprint 1) ===\n")
    for i, item in enumerate(comments, 1):
        label_key = classify_sentiment(item["comment"])
        label = LABEL_MAP[label_key]
        counts[label] += 1
        product = item.get("product", "—")
        text = item["comment"][:70]
        print(f"{i}. [{label}] ({product}) {text}")

    print(
        f"\nOzet: Olumlu {counts['Olumlu']}, "
        f"Olumsuz {counts['Olumsuz']}, Notr {counts['Nötr']}"
    )


def run_groq():
    from openai import AuthenticationError

    client = get_groq_client()
    if not client:
        print("GROQ_API_KEY yok — basit yontemi kullan: python sentiment_test.py")
        return

    comments = load_comments()
    text = "\n".join(
        f"- [{item.get('product', '?')}] {item['comment']}"
        for item in comments
    )

    try:
        r = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Bu yorumlari analiz et (Turkce, kisa):\n{text}\n\n"
                        "1) Her yorum sentiment 2) Dagilim 3) Kisa ozet"
                    ),
                }
            ],
            max_tokens=600,
        )
    except AuthenticationError:
        print("Groq API key gecersiz.")
        return

    print(f"=== Groq ({TEXT_MODEL}) ===\n")
    print(r.choices[0].message.content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--groq", action="store_true", help="Groq API ile analiz")
    args = parser.parse_args()
    (run_groq if args.groq else run_simple)()
