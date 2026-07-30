"""
Sprint 3 — Chatbot orkestrasyon katmanı.

Akış: oturum hafızası → hibrit RAG retrieval → kaynak seçimi → LLM/şablon yanıt
"""

from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from groq_client import TEXT_MODEL, get_groq_client
from memory import SessionMemory, memory_store
from product_db import format_product_context
from rag.retriever import hybrid_retrieve

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

DISCLAIMER = (
    "Bu bilgiler yalnızca bilgilendirme amaçlıdır; "
    "tıbbi tavsiye değildir. Sağlık kararları için doktorunuza danışın."
)

SYSTEM_PROMPT = """
Sen PhyraMed platformunun bilgilendirme chatbot'usun.

Kurallar:
- Öncelikle verilen ürün veritabanı / retrieval bağlamını kullan.
- Bilmediğin konuda tahmin yürütme.
- Tıbbi teşhis koyma veya tedavi önerme.
- Kısa ve anlaşılır cevap ver.
- Yan etki ve etkileşimleri mutlaka belirt.
- Önceki konuşma bağlamını dikkate al.
"""


def _format_retrieved_context(chunks: list[dict]) -> str:
    if not chunks:
        return "İlgili içerik bulunamadı."

    blocks = []
    for i, chunk in enumerate(chunks, 1):
        # Re-ranking skorunu da ekleyelim
        score = chunk.get("rerank_score", chunk.get("score", 0))
        blocks.append(
            f"[Kaynak {i} — {chunk['product_name']} / {chunk['field']} (Skor: {score:.2f})]\n{chunk['text']}"
        )

    return "\n\n".join(blocks)


def _template_answer(question: str, products: list[dict], source: str) -> str:
    if not products:
        return (
            f'Sorunuz: "{question}"\n\n'
            "Veritabanında uygun ürün bulunamadı.\n"
            "Lütfen daha spesifik bir bitki veya kullanım amacı yazınız.\n\n"
            f"Kaynak: AI Yanıtı\n\n"
            f"UYARI: {DISCLAIMER}"
        )

    lines = [f'Sorunuz: "{question}"', "", "İlgili ürünler:", ""]
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

    label = "Onaylanmış Bilgi" if source == "verified_db" else "AI Yanıtı"
    lines.append(f"Kaynak: {label}")
    lines.append(f"UYARI: {DISCLAIMER}")
    return "\n".join(lines)


def _groq_generate(
    question: str,
    products: list[dict],
    chunks: list[dict],
    history: list[dict],
) -> str:
    from openai import AuthenticationError

    client = get_groq_client()
    if not client:
        source = "verified_db" if products else "ai_generated"
        return _template_answer(question, products, source)

    retrieved = _format_retrieved_context(chunks)
    product_ctx = format_product_context(products)

    if products:
        user_prompt = (
            f"Kullanıcı sorusu:\n{question}\n\n"
            f"Retrieval bağlamı (RAG):\n{retrieved}\n\n"
            f"Ürün özeti:\n{product_ctx}\n\n"
            "Yalnızca verilen kaynaklardaki bilgileri kullanarak cevap ver.\n"
            "Cevabın başına şu ifadeyi ekle:\n"
            "Kaynak: Onaylanmış Bilgi\n\n"
            f"Cevabın sonuna mutlaka şu uyarıyı ekle:\n{DISCLAIMER}"
        )
    else:
        user_prompt = (
            f"Kullanıcı sorusu:\n{question}\n\n"
            "Bu konu ürün veritabanında bulunamadı.\n"
            "Kendi genel bilgini kullanarak bilgilendirici bir cevap ver.\n"
            "Eğer bilimsel kanıtlar sınırlıysa bunu belirt.\n\n"
            "Cevabın başına şu ifadeyi ekle:\n"
            "Kaynak: AI Yanıtı\n\n"
            f"Cevabın sonuna mutlaka şu uyarıyı ekle:\n{DISCLAIMER}"
        )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history[-6:])
    messages.append({"role": "user", "content": user_prompt})

    try:
        response = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=600,
        )
        return response.choices[0].message.content

    except AuthenticationError:
        source = "verified_db" if products else "ai_generated"
        return _template_answer(question, products, source)


def orchestrate(
    question: str,
    *,
    session_id: Optional[str] = None,
    use_groq: bool = True,
    memory: Optional[SessionMemory] = None,
) -> dict:
    """
    Ana orkestrasyon fonksiyonu.

    Dönüş:
        {
            answer, source, sources[], retrieved_chunks[], session_id
        }
    """

    store = memory or memory_store

    if not session_id:
        session_id = store.create_session()

    history = store.get_messages(session_id, max_turns=8)
    retrieval = hybrid_retrieve(question, top_k=5, use_rerank=True)
    products = retrieval["products"]
    chunks = retrieval["chunks"]

    source = "verified_db" if products else "ai_generated"

    if use_groq:
        answer = _groq_generate(question, products, chunks, history)
    else:
        answer = _template_answer(question, products, source)

    store.add_turn(session_id, "user", question)
    store.add_turn(session_id, "assistant", answer)

    sources = [{"id": p["id"], "name": p["name"]} for p in products]

    retrieved_chunks = [
        {
            "chunk_id": c["chunk_id"],
            "product_id": c["product_id"],
            "product_name": c["product_name"],
            "field": c["field"],
            "score": round(c["score"], 3),
            "source": c["source"],
        }
        for c in chunks
    ]

    return {
        "answer": answer,
        "source": source,
        "sources": sources,
        "retrieved_chunks": retrieved_chunks,
        "session_id": session_id,
    }
