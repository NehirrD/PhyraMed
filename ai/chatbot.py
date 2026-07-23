"""Chatbot iş mantığı — chat.py router'ı tarafından çağrılır."""

from ai.groq_client import TEXT_MODEL, get_groq_client
from ai.product_db import format_product_context, search_products

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
    if not products:
        return (
            f'Sorunuz: "{question}"\n\n'
            "Veritabanında uygun ürün bulunamadı.\n"
            f"UYARI: {DISCLAIMER}"
        )

    lines = [f'Sorunuz: "{question}"', "", "İlgili ürünler:", ""]
    for p in products:
        lines.extend([
            f"Ürün: {p.get('name')}",
            f"Kullanım amacı: {p.get('usage_purpose')}",
            f"Uzman görüşü: {p.get('expert_opinion_summary')}",
            "-" * 50,
        ])
    lines.append(f"UYARI: {DISCLAIMER}")
    return "\n".join(lines)


def groq_answer(question: str, products: list[dict]) -> str:
    from openai import AuthenticationError

    client = get_groq_client()
    if not client:
        return template_answer(question, products)

    context = format_product_context(products)

    if products:
        user_prompt = (
            f"Kullanıcı sorusu:\n{question}\n\nÜrün veritabanı:\n\n{context}\n\n"
            "Yalnızca ürün veritabanındaki bilgileri kullanarak cevap ver.\n"
            f"Cevabın sonuna mutlaka şu uyarıyı ekle:\n{DISCLAIMER}"
        )
    else:
        user_prompt = (
            f"Kullanıcı sorusu:\n{question}\n\nBu konu ürün veritabanında bulunamadı.\n"
            "Genel bilgini kullanarak bilgilendirici bir cevap ver.\n"
            f"Cevabın sonuna mutlaka şu uyarıyı ekle:\n{DISCLAIMER}"
        )

    try:
        response = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        return response.choices[0].message.content
    except AuthenticationError:
        return template_answer(question, products)


def get_bot_response(question: str, use_groq: bool = True) -> str:
    """chat.py router'ının çağıracağı tek fonksiyon."""
    products = search_products(question)
    if use_groq:
        return groq_answer(question, products)
    return template_answer(question, products)