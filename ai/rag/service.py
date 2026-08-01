"""PhyraMed RAG yanıt servisi.

Bu katman semantik retrieval sonucunu güncel SQLAlchemy verileriyle birleştirir.
Dil modeli yalnızca PhyraMed bilgi tabanındaki ürün, risk, etkileşim ve kaynak
bilgilerini kullanır. Bilgi bulunmadığında genel model bilgisine geçilmez.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from openai import OpenAIError

from ai.groq_client import TEXT_MODEL, extract_model_text, get_groq_client
from ai.product_db import get_products_by_ids, search_products
from ai.rag.retriever import retrieve_products
from ai.rag.store import get_product_collection


DISCLAIMER = (
    "Bu bilgiler yalnızca bilgilendirme amaçlıdır; tıbbi tavsiye değildir. "
    "Sağlık kararları için bir sağlık profesyoneline danışın."
)

NO_MATCH_MESSAGE = (
    "PhyraMed'de bu soru için yeterli düzeyde eşleşen, kaynaklandırılmış "
    "içerik bulunmuyor. Bu nedenle doğruluğunu kontrol edemediğimiz genel "
    "yapay zekâ bilgisi sunmuyoruz."
)

SYSTEM_PROMPT = """
Sen PhyraMed'in kaynaklandırılmış bilgi asistanısın.

Zorunlu kurallar:
- Yalnızca sana verilen PhyraMed bilgi tabanı bağlamını kullan.
- Bağlamda bulunmayan hiçbir fayda, risk, etkileşim, doz veya kaynak üretme.
- Tanı koyma, tedavi önerme, doz önerme ve kişisel ürün tavsiyesi verme.
- Kullanıcı ürün önerisi istese bile "öneriyorum" deme; yalnızca PhyraMed'de
  ilgili kayıtları tarafsız biçimde açıkla.
- Kanıt durumu boşsa "Değerlendiriliyor" olarak belirt.
- Risk veya etkileşim kaydı yoksa bunu açıkça söyle; güvenli olduğu sonucunu çıkarma.
- Kaynakları yalnızca bağlamda verilen başlık ve bağlantılarla göster.
- Kısa, anlaşılır ve Türkçe cevap ver.
""".strip()


@dataclass
class ProductResolution:
    """Bir sorunun hangi stratejiyle hangi ürünlere bağlandığını taşır."""

    products: list[dict[str, Any]]
    strategy: str
    rag_results: list[dict[str, Any]]


def _clean_text(value: Any, default: str = "Belirtilmemiş") -> str:
    if value is None:
        return default

    text = str(value).strip()
    return text or default


def _format_sources(product: dict[str, Any]) -> list[str]:
    lines: list[str] = []

    for source in product.get("sources") or []:
        title = _clean_text(source.get("title"), "Başlıksız kaynak")
        url = _clean_text(source.get("url"), "")
        source_type = _clean_text(source.get("type"), "")

        detail = title
        if source_type:
            detail += f" ({source_type})"
        if url:
            detail += f" — {url}"
        lines.append(detail)

    return lines


def build_context(products: list[dict[str, Any]]) -> str:
    """Ürünleri model için kaynakları korunmuş, yapılandırılmış bağlama çevirir."""

    blocks: list[str] = []

    for product in products:
        category = product.get("category") or {}
        risks = product.get("risks") or []
        interactions = product.get("interactions") or []
        sources = _format_sources(product)

        risk_lines = [
            (
                f"- {_clean_text(risk.get('description'))} "
                f"(şiddet: {_clean_text(risk.get('severity'), 'Belirtilmemiş')})"
            )
            for risk in risks
            if _clean_text(risk.get("description"), "")
        ] or ["- Kayıtlı risk bilgisi bulunmuyor."]

        interaction_lines = [
            (
                f"- {_clean_text(interaction.get('interacts_with'))}: "
                f"{_clean_text(interaction.get('description'), 'Ayrıntı bulunmuyor')}"
            )
            for interaction in interactions
            if _clean_text(interaction.get("interacts_with"), "")
            or _clean_text(interaction.get("description"), "")
        ] or ["- Kayıtlı etkileşim bilgisi bulunmuyor."]

        source_lines = [f"- {source}" for source in sources] or [
            "- Kayıtlı bilimsel kaynak bulunmuyor."
        ]

        blocks.append(
            "\n".join(
                [
                    f"Ürün: {_clean_text(product.get('name'))}",
                    f"Kategori: {_clean_text(category.get('name'))}",
                    f"Kullanım amacı: {_clean_text(product.get('usage_purpose'))}",
                    (
                        "Bilimsel kanıt durumu: "
                        f"{_clean_text(product.get('evidence_level'), 'Değerlendiriliyor')}"
                    ),
                    (
                        "Bilimsel kanıt özeti: "
                        f"{_clean_text(product.get('expert_opinion_summary'))}"
                    ),
                    "Riskler:",
                    *risk_lines,
                    "Etkileşimler:",
                    *interaction_lines,
                    "Kaynaklar:",
                    *source_lines,
                ]
            )
        )

    return "\n\n---\n\n".join(blocks)


def _is_index_ready() -> bool:
    try:
        return get_product_collection().count() > 0
    except Exception as error:
        print(f"[rag] Chroma indeksi kontrol edilemedi: {error}")
        return False


def resolve_products(question: str, max_products: int = 3) -> ProductResolution:
    """Önce RAG, gerekirse güvenli kelime aramasıyla ürünleri çözümler."""

    clean_question = str(question or "").strip()
    if not clean_question:
        return ProductResolution([], "none", [])

    rag_results: list[dict[str, Any]] = []

    if _is_index_ready():
        try:
            rag_results = retrieve_products(
                clean_question,
                max_products=max_products,
            )
            product_ids = [
                int(result["product_id"])
                for result in rag_results
                if result.get("product_id") is not None
            ]
            products = get_products_by_ids(product_ids)

            if products:
                return ProductResolution(products, "rag", rag_results)
        except Exception as error:
            print(f"[rag] Retrieval başarısız, güvenli fallback kullanılacak: {error}")

    # Chroma indeksi yoksa veya teknik hata oluşursa yalnızca mevcut veritabanı
    # üzerinde çalışan güvenli kelime araması kullanılır. Genel model bilgisine
    # hiçbir koşulda geçilmez.
    fallback_products = search_products(clean_question, limit=max_products)
    if fallback_products:
        return ProductResolution(fallback_products, "keyword_fallback", rag_results)

    return ProductResolution([], "none", rag_results)


def _platform_knowledge_answer(question: str) -> str | None:
    normalized = str(question or "").strip().lower()

    if "kanıt seviyesi" not in normalized and "kanit seviyesi" not in normalized:
        return None

    return (
        "PhyraMed'de kanıt seviyesi, bir ürünle ilgili bilimsel bilginin gücünü "
        "özetler. Güçlü, Orta ve Zayıf düzeyleri kullanılabilir. Değerlendirme "
        "tamamlanmamışsa ürün 'Değerlendiriliyor' olarak gösterilir. Bu seviye "
        "tek başına ürünün herkes için uygun veya güvenli olduğu anlamına gelmez.\n\n"
        f"UYARI: {DISCLAIMER}"
    )


def template_answer(question: str, products: list[dict[str, Any]]) -> str:
    """Model kullanılamadığında da kaynaklı ve güvenli cevap üretir."""

    if not products:
        return f"{NO_MATCH_MESSAGE}\n\nUYARI: {DISCLAIMER}"

    sections: list[str] = [f'Sorunuz: "{question}"', ""]

    for product in products:
        category = product.get("category") or {}
        risks = product.get("risks") or []
        interactions = product.get("interactions") or []
        sources = _format_sources(product)

        sections.extend(
            [
                f"Ürün: {_clean_text(product.get('name'))}",
                f"Kategori: {_clean_text(category.get('name'))}",
                f"Kullanım amacı: {_clean_text(product.get('usage_purpose'))}",
                (
                    "Bilimsel kanıt durumu: "
                    f"{_clean_text(product.get('evidence_level'), 'Değerlendiriliyor')}"
                ),
                (
                    "Bilimsel kanıt özeti: "
                    f"{_clean_text(product.get('expert_opinion_summary'))}"
                ),
                "Riskler: "
                + (
                    "; ".join(
                        _clean_text(risk.get("description"))
                        for risk in risks
                        if _clean_text(risk.get("description"), "")
                    )
                    or "Kayıtlı risk bilgisi bulunmuyor."
                ),
                "Etkileşimler: "
                + (
                    "; ".join(
                        (
                            f"{_clean_text(interaction.get('interacts_with'))}: "
                            f"{_clean_text(interaction.get('description'), 'Ayrıntı bulunmuyor')}"
                        )
                        for interaction in interactions
                        if _clean_text(interaction.get("interacts_with"), "")
                        or _clean_text(interaction.get("description"), "")
                    )
                    or "Kayıtlı etkileşim bilgisi bulunmuyor."
                ),
                "Kaynaklar: " + ("; ".join(sources) or "Kayıtlı kaynak bulunmuyor."),
                "-" * 50,
            ]
        )

    sections.extend(["", f"UYARI: {DISCLAIMER}"])
    return "\n".join(sections)


def _source_appendix(products: list[dict[str, Any]]) -> str:
    unique_sources: list[str] = []
    seen: set[str] = set()

    for product in products:
        for source in _format_sources(product):
            if source not in seen:
                seen.add(source)
                unique_sources.append(source)

    if not unique_sources:
        return "Kaynaklar:\n- Kayıtlı bilimsel kaynak bulunmuyor."

    return "Kaynaklar:\n" + "\n".join(
        f"- {source}" for source in unique_sources
    )


def _ensure_answer_contract(
    answer: str,
    products: list[dict[str, Any]],
) -> str:
    clean_answer = str(answer or "").strip()
    if not clean_answer:
        return template_answer("", products)

    if "kaynaklar" not in clean_answer.lower():
        clean_answer += f"\n\n{_source_appendix(products)}"

    if DISCLAIMER not in clean_answer:
        clean_answer += f"\n\nUYARI: {DISCLAIMER}"

    return clean_answer


def groq_answer(question: str, products: list[dict[str, Any]]) -> str:
    """Groq ile yalnızca getirilen PhyraMed bağlamından cevap üretir."""

    if not products:
        return template_answer(question, products)

    client = get_groq_client()
    if client is None:
        return template_answer(question, products)

    context = build_context(products)
    user_prompt = (
        f"Kullanıcı sorusu:\n{question}\n\n"
        f"PhyraMed bilgi tabanı bağlamı:\n\n{context}\n\n"
        "Yalnızca bu bağlamdaki bilgileri kullan. Cevapta ilgili ürünleri, "
        "bilimsel kanıt özetini, kayıtlı riskleri, etkileşimleri ve kaynakları "
        "açıkça belirt. Bağlamın dışına çıkma."
    )

    try:
        response = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            max_tokens=700,
        )
        content = response.choices[0].message.content
        return _ensure_answer_contract(
            extract_model_text(content or ""),
            products,
        )
    except OpenAIError as error:
        print(f"[rag] Groq servisi kullanılamadı: {error}")
        return template_answer(question, products)
    except Exception as error:
        # Beklenmeyen model cevabı veya istemci uyumsuzluğu demo sırasında 500
        # üretmemeli; güvenli, veritabanı tabanlı şablona dönülür.
        print(f"[rag] Yanıt üretimi beklenmeyen biçimde başarısız: {error}")
        return template_answer(question, products)


def answer_question(question: str, use_groq: bool = True) -> str:
    """Chat router'ının çağıracağı güvenli RAG giriş noktası."""

    clean_question = str(question or "").strip()
    if not clean_question:
        return "Lütfen ürün veya takviye hakkında bir soru yazın."

    platform_answer = _platform_knowledge_answer(clean_question)
    if platform_answer is not None:
        return platform_answer

    resolution = resolve_products(clean_question)
    if not resolution.products:
        return template_answer(clean_question, [])

    if use_groq:
        return groq_answer(clean_question, resolution.products)

    return template_answer(clean_question, resolution.products)
