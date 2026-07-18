"""
Sprint 2 — prompt tabanlı chatbot (ürün veritabanına bağlı).

Ürün bilgisini mock JSON DB'den çeker, soruya göre bağlam oluşturur.
Groq key varsa doğal dil cevabı üretir; yoksa şablon tabanlı yanıt verir.

    python poc/chatbot.py
    python poc/chatbot.py --groq
    python poc/chatbot.py --question "Zencefil mide bulantısına iyi gelir mi?"
"""

import argparse
from pathlib import Path

from dotenv import load_dotenv

from groq_client import TEXT_MODEL, get_groq_client
from product_db import format_product_context, search_products

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

DISCLAIMER = (
    "Bu bilgiler yalnızca bilgilendirme amaçlıdır; "
    "tıbbi tavsiye değildir. Sağlık kararları için doktorunuza danışın."
)

SYSTEM_PROMPT = """
Sen PhyraMed platformunun bilgilendirme chatbot'usun.

Kurallar:
- Sadece verilen ürün veritabanındaki bilgileri kullan.
- Bilmediğin konuda tahmin yürütme.
- Tıbbi teşhis koyma.
- Tedavi önerme.
- Kısa ve anlaşılır cevap ver.
- Yan etki ve etkileşimleri mutlaka belirt.
"""


def template_answer(question: str, products: list[dict]) -> str:
    """Groq kullanılmadığında gösterilecek cevap."""

    if not products:
        return (
            f'Sorunuz: "{question}"\n\n'
            "Veritabanında uygun ürün bulunamadı.\n"
            "Lütfen daha spesifik bir bitki veya kullanım amacı yazınız.\n\n"
            f"UYARI: {DISCLAIMER}"
        )

    lines = [
        f'Sorunuz: "{question}"',
        "",
        "İlgili ürünler:",
        ""
    ]

    for p in products:
        lines.extend([
            f"Ürün: {p['name']}",
            f"Kategori: {p['category']}",
            f"Kullanım amacı: {p['usage_purpose']}",
            f"İddia: {p['claim']}",
            f"Kanıt seviyesi: {p['evidence_level']}",
            f"Bilimsel özet: {p['evidence_summary']}",
            f"Riskler: {p['risk_summary']}",
            f"Etkileşimler: {p['interaction_summary']}",
            "-" * 50,
        ])

    lines.append(f"UYARI: {DISCLAIMER}")

    return "\n".join(lines)


def groq_answer(question: str, products: list[dict]) -> str:
    """Groq ile doğal dil cevabı."""

    from openai import AuthenticationError

    client = get_groq_client()

    if not client:
        return template_answer(question, products)

    context = format_product_context(products)

    try:
        response = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": (
                        f"Kullanıcı sorusu:\n{question}\n\n"
                        f"Ürün veritabanı:\n\n{context}\n\n"
                        f"Cevabın sonuna mutlaka şu uyarıyı ekle:\n{DISCLAIMER}"
                    ),
                },
            ],
            temperature=0.3,
            max_tokens=500,
        )

        return response.choices[0].message.content

    except AuthenticationError:
        print("Groq API anahtarı geçersiz. Şablon cevap kullanılıyor.")
        return template_answer(question, products)


def ask(question: str, use_groq: bool) -> str:
    """Kullanıcı sorusunu cevaplar."""

    products = search_products(question)

    if use_groq:
        return groq_answer(question, products)

    return template_answer(question, products)


def interactive(use_groq: bool):
    mode = "Groq" if use_groq else "Şablon"

    print(f"=== PhyraMed Chatbot ({mode}) ===")
    print("Çıkmak için 'quit' yazın.\n")

    while True:
        try:
            question = input("Soru> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGörüşmek üzere.")
            break

        if not question:
            continue

        if question.lower() in {"quit", "exit", "q"}:
            print("Görüşmek üzere.")
            break

        print()
        print(ask(question, use_groq))
        print()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--groq",
        action="store_true",
        help="Groq ile doğal dil cevabı üret"
    )

    parser.add_argument(
        "--question",
        "-q",
        type=str,
        help="Tek soru sor"
    )

    args = parser.parse_args()

    if args.question:
        print(ask(args.question, args.groq))
    else:
        interactive(args.groq)


if __name__ == "__main__":
    main()