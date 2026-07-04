"""
Sprint 1 — basit yorum analizi.
Key yoksa kelime listesi, key varsa Groq.

    python sentiment_test.py
    python sentiment_test.py --groq
"""

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from groq_client import TEXT_MODEL, get_groq_client

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

COMMENTS = json.loads((Path(__file__).parent / "sample_comments.json").read_text(encoding="utf-8"))

POSITIVE = ["iyi", "harika", "fayda", "arttı", "tekrar alacağım", "onayladı", "alternatif"]
NEGATIVE = ["faydasını görmedim", "para boşa", "bıraktım", "yan etki", "alerji", "yetersiz", "garip", "dikkatli"]


def simple_sentiment(text: str) -> str:
    t = text.lower()
    p = sum(1 for w in POSITIVE if w in t)
    n = sum(1 for w in NEGATIVE if w in t)
    if p > n:
        return "Olumlu"
    if n > p:
        return "Olumsuz"
    return "Nötr"


def run_simple():
    counts = {"Olumlu": 0, "Olumsuz": 0, "Nötr": 0}
    print("=== Basit kelime yöntemi (Sprint 1) ===\n")
    for i, c in enumerate(COMMENTS, 1):
        label = simple_sentiment(c)
        counts[label] += 1
        print(f"{i}. [{label}] {c[:70]}")
    print(f"\nÖzet: Olumlu {counts['Olumlu']}, Olumsuz {counts['Olumsuz']}, Nötr {counts['Nötr']}")


def run_groq():
    from openai import AuthenticationError

    client = get_groq_client()
    if not client:
        print("GROQ_API_KEY yok — basit yöntemi kullan: python sentiment_test.py")
        print("Key ekle: ai/.env dosyasında GROQ_API_KEY=gsk_...")
        return

    text = "\n".join(f"- {c}" for c in COMMENTS)
    try:
        r = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[{"role": "user", "content": f"Bu yorumları analiz et (Türkçe, kısa):\n{text}\n\n1) Her yorum sentiment 2) Dağılım 3) Kısa özet"}],
            max_tokens=600,
        )
    except AuthenticationError:
        print("Groq API key geçersiz (401). Kontrol et:")
        print("  1. https://console.groq.com/keys adresinden yeni key kopyala")
        print("  2. ai/.env içinde: GROQ_API_KEY=gsk_... (tırnak yok, boşluk yok)")
        print("  3. Komutu ai/ klasöründen çalıştır: python poc/sentiment_test.py --groq")
        return

    print(f"=== Groq ({TEXT_MODEL}) ===\n")
    print(r.choices[0].message.content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--groq", action="store_true", help="Groq API ile analiz")
    args = parser.parse_args()
    (run_groq if args.groq else run_simple)()
