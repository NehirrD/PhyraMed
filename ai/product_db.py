"""Chatbot için ürün veritabanı erişimi.

Ürünler aynı backend'e HTTP isteği gönderilerek değil,
doğrudan SQLAlchemy oturumu üzerinden alınır.
"""

import re

from sqlalchemy.orm import selectinload

import models
from database import SessionLocal


def enum_value(value):
    """SQLAlchemy Enum değerini JSON uyumlu metne dönüştürür."""
    if value is None:
        return None

    return getattr(value, "value", value)


def serialize_product(product: models.Product) -> dict:
    """Product modelini chatbotun kullandığı sözlüğe dönüştürür."""
    category = product.category

    return {
        "id": product.id,
        "name": product.name,
        "category_id": product.category_id,
        "usage_purpose": product.usage_purpose,
        "evidence_level": enum_value(product.evidence_level),
        "expert_opinion_summary": product.expert_opinion_summary,
        "image_url": product.image_url,
        "status": enum_value(product.status),
        "category": (
            {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "search_count": category.search_count,
            }
            if category
            else None
        ),
        "risks": [
            {
                "id": risk.id,
                "product_id": risk.product_id,
                "description": risk.description,
                "severity": enum_value(risk.severity),
            }
            for risk in product.risks
        ],
        "sources": [
            {
                "id": source.id,
                "product_id": source.product_id,
                "type": source.type,
                "url": source.url,
                "title": source.title,
            }
            for source in product.sources
        ],
        "interactions": [
            {
                "id": interaction.id,
                "product_id": interaction.product_id,
                "interacts_with": interaction.interacts_with,
                "description": interaction.description,
            }
            for interaction in product.interactions
        ],
    }


def product_query(db):
    """Chatbot için gerekli ilişkileri tek sorgu akışında yükler."""
    return db.query(models.Product).options(
        selectinload(models.Product.category),
        selectinload(models.Product.risks),
        selectinload(models.Product.sources),
        selectinload(models.Product.interactions),
    )


def load_products() -> list[dict]:
    """Tüm ürünleri doğrudan PhyraMed veritabanından getirir."""
    db = SessionLocal()

    try:
        products = product_query(db).all()
        return [serialize_product(product) for product in products]
    except Exception as error:
        print(
            "[product_db] Veritabanı sorgusu başarısız: "
            f"{error}"
        )
        return []
    finally:
        db.close()


def get_product_by_id(product_id: int) -> dict | None:
    """Kimliği verilen ürünü doğrudan veritabanından getirir."""
    db = SessionLocal()

    try:
        product = (
            product_query(db)
            .filter(models.Product.id == product_id)
            .first()
        )

        if product is None:
            return None

        return serialize_product(product)
    except Exception as error:
        print(
            "[product_db] Ürün sorgusu başarısız: "
            f"{error}"
        )
        return None
    finally:
        db.close()


STOPWORDS = {
    "için",
    "icin",
    "bir",
    "bu",
    "ne",
    "mi",
    "mı",
    "mu",
    "mü",
    "ve",
    "ile",
    "var",
    "olan",
    "gibi",
    "daha",
    "çok",
    "cok",
    "iyi",
    "gelir",
    "önerirsiniz",
    "onerirsiniz",
    "nasıl",
    "nasil",
    "hangi",
    "hakkında",
    "hakkinda",
}


def normalize(text: str) -> str:
    """Türkçe karakterleri arama için normalize eder."""
    text = (text or "").lower()

    replacements = {
        "ç": "c",
        "ğ": "g",
        "ı": "i",
        "ö": "o",
        "ş": "s",
        "ü": "u",
    }

    for turkish_character, latin_character in replacements.items():
        text = text.replace(
            turkish_character,
            latin_character,
        )

    return text


def search_products(
    query: str,
    limit: int = 3,
) -> list[dict]:
    """Kullanıcı sorusuyla ilişkili ürünleri puanlayarak bulur."""
    normalized_query = normalize(query)

    tokens = {
        token
        for token in re.findall(r"\w+", normalized_query)
        if len(token) >= 3 and token not in STOPWORDS
    }

    scored_products = []

    for product in load_products():
        score = 0

        name = normalize(product.get("name", ""))
        usage = normalize(
            product.get("usage_purpose", "")
        )
        summary = normalize(
            product.get(
                "expert_opinion_summary",
                "",
            )
        )

        category = product.get("category") or {}
        category_name = normalize(
            category.get("name", "")
        )

        risk_texts = " ".join(
            normalize(risk.get("description", ""))
            for risk in product.get("risks", [])
        )

        source_texts = " ".join(
            normalize(
                source.get("title")
                or source.get("url")
                or ""
            )
            for source in product.get("sources", [])
        )

        interaction_texts = " ".join(
            (
                normalize(
                    interaction.get(
                        "interacts_with",
                        "",
                    )
                )
                + " "
                + normalize(
                    interaction.get(
                        "description",
                        "",
                    )
                )
            )
            for interaction in product.get(
                "interactions",
                [],
            )
        )

        for token in tokens:
            if token in name:
                score += 10

            if token in category_name:
                score += 8

            if token in usage:
                score += 6

            if token in summary:
                score += 3

            if token in risk_texts:
                score += 1

            if token in source_texts:
                score += 1

            if token in interaction_texts:
                score += 1

        if score >= 6:
            scored_products.append(
                (score, product)
            )

    scored_products.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [
        product
        for _, product in scored_products[:limit]
    ]


def format_product_context(
    products: list[dict],
) -> str:
    """Eşleşen ürünleri yapay zekâ için güvenli bağlama dönüştürür."""
    if not products:
        return "İlgili ürün bulunamadı."

    blocks = []

    for product in products:
        category = product.get("category") or {}

        category_name = category.get(
            "name",
            "Belirtilmemiş",
        )

        risks = ", ".join(
            (
                f"{risk.get('description')} "
                f"(şiddet: "
                f"{risk.get('severity') or 'belirtilmemiş'})"
            )
            for risk in product.get("risks", [])
            if risk.get("description")
        ) or "Belirtilmemiş"

        sources = ", ".join(
            (
                source.get("title")
                or source.get("url")
                or "Başlıksız kaynak"
            )
            for source in product.get("sources", [])
        ) or "Belirtilmemiş"

        interactions = ", ".join(
            (
                f"{interaction.get('interacts_with')}: "
                f"{interaction.get('description') or 'detay yok'}"
            )
            for interaction in product.get(
                "interactions",
                [],
            )
        ) or "Belirtilmemiş"

        evidence_level = (
            product.get("evidence_level")
            or "Değerlendiriliyor"
        )

        blocks.append(
            f"Ürün: {product.get('name')}\n"
            f"Kategori: {category_name}\n"
            f"Kullanım amacı: "
            f"{product.get('usage_purpose')}\n"
            f"Kanıt durumu: {evidence_level}\n"
            f"Bilimsel kanıt özeti: "
            f"{product.get('expert_opinion_summary')}\n"
            f"Riskler: {risks}\n"
            f"Kaynaklar: {sources}\n"
            f"Etkileşimler: {interactions}"
        )

    return "\n\n---\n\n".join(blocks)