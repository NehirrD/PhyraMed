"""Chatbot iş mantığı — chat.py router'ı tarafından çağrılır."""
from openai import OpenAIError
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
            "PhyraMed'de bu ürün veya konu için henüz "
            "kaynaklandırılmış içerik bulunmuyor.\n"
            "Bu nedenle doğruluğunu kontrol edemediğimiz "
            "genel yapay zekâ bilgisi sunmuyoruz.\n"
            "Ürün adını kontrol edebilir veya bir sağlık "
            "profesyoneline danışabilirsiniz.\n\n"
            f"UYARI: {DISCLAIMER}"
        )

    lines = [
        f'Sorunuz: "{question}"',
        "",
        "İlgili ürünler:",
        "",
    ]

    for product in products:
        lines.extend([
            f"Ürün: {product.get('name') or 'Belirtilmemiş'}",
            (
                "Kullanım amacı: "
                f"{product.get('usage_purpose') or 'Belirtilmemiş'}"
            ),
            (
                "Bilimsel kanıt özeti: "
                f"{product.get('expert_opinion_summary') or 'Belirtilmemiş'}"
            ),
            "-" * 50,
        ])

    lines.append(f"UYARI: {DISCLAIMER}")
    return "\n".join(lines)

def groq_answer(question: str, products: list[dict]) -> str:
    # Veritabanında eşleşme yoksa genel model bilgisi kullanılmaz.
    if not products:
        return template_answer(question, products)

    client = get_groq_client()

    if not client:
        return template_answer(question, products)

    context = format_product_context(products)

    user_prompt = (
        f"Kullanıcı sorusu:\n{question}\n\n"
        f"PhyraMed ürün veritabanı:\n\n{context}\n\n"
        "Yalnızca yukarıdaki ürün veritabanındaki bilgileri kullanarak cevap ver.\n"
        "Veritabanında yer almayan bilgi, doz, tedavi veya kişisel öneri üretme.\n"
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

        content = response.choices[0].message.content

        if not content or not content.strip():
            return template_answer(question, products)

        return content.strip()

    except OpenAIError as error:
        print(f"[chatbot] Yapay zekâ servisine ulaşılamadı: {error}")
        return template_answer(question, products)

def get_bot_response(question: str, use_groq: bool = True) -> str:
    """Chat router'ının çağıracağı ana fonksiyon."""

    clean_question = str(question or "").strip()

    if not clean_question:
        return "Lütfen ürün veya takviye hakkında bir soru yazın."

    products = search_products(clean_question)

    if not products:
        return template_answer(clean_question, products)

    if use_groq:
        return groq_answer(clean_question, products)

    return template_answer(clean_question, products)