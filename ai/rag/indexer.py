"""PhyraMed ürünlerini ChromaDB için güvenli parçalara ayırır ve indeksler."""

from __future__ import annotations

from typing import Any

from ai.product_db import load_products
from ai.rag.store import get_product_collection


def clean_text(value: Any, default: str = "Belirtilmemiş") -> str:
    """Boş ve None değerleri güvenli metne dönüştürür."""

    if value is None:
        return default

    text = str(value).strip()
    return text or default


def add_chunk(
    chunks: list[dict[str, Any]],
    *,
    chunk_id: str,
    document: str,
    product: dict[str, Any],
    chunk_type: str,
    entity_id: int | None = None,
    extra_metadata: dict[str, Any] | None = None,
) -> None:
    """Tek ve benzersiz bir Chroma parçası ekler."""

    metadata: dict[str, str | int | float | bool] = {
        "product_id": int(product["id"]),
        "product_name": clean_text(product.get("name")),
        "chunk_type": chunk_type,
    }

    if entity_id is not None:
        metadata["entity_id"] = int(entity_id)

    if extra_metadata:
        for key, value in extra_metadata.items():
            if value is None:
                continue

            text_value = str(value).strip()
            if text_value:
                metadata[key] = text_value

    chunks.append(
        {
            "id": chunk_id,
            "document": document.strip(),
            "metadata": metadata,
        }
    )


def build_product_chunks(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Güncel PhyraMed ürün şemasından benzersiz RAG parçaları üretir."""

    chunks: list[dict[str, Any]] = []

    for product in products:
        product_id = int(product["id"])
        product_name = clean_text(product.get("name"))

        category = product.get("category") or {}
        category_name = clean_text(category.get("name"))
        category_description = clean_text(
            category.get("description"),
            default="",
        )

        usage_purpose = clean_text(product.get("usage_purpose"))
        evidence_level = clean_text(
            product.get("evidence_level"),
            default="Değerlendiriliyor",
        )
        evidence_summary = clean_text(
            product.get("expert_opinion_summary")
        )

        overview_document = f"""
Ürün: {product_name}
Kategori: {category_name}
Kategori açıklaması: {category_description}
Kullanım amacı: {usage_purpose}
Bilimsel kanıt durumu: {evidence_level}
Bilimsel kanıt özeti: {evidence_summary}
"""

        add_chunk(
            chunks,
            chunk_id=f"product:{product_id}:overview",
            document=overview_document,
            product=product,
            chunk_type="overview",
            extra_metadata={
                "category_name": category_name,
                "evidence_level": evidence_level,
            },
        )

        for index, risk in enumerate(product.get("risks") or [], start=1):
            description = clean_text(
                risk.get("description"),
                default="",
            )
            if not description:
                continue

            risk_id = int(risk.get("id") or index)
            severity = clean_text(
                risk.get("severity"),
                default="Belirtilmemiş",
            )

            add_chunk(
                chunks,
                chunk_id=f"product:{product_id}:risk:{risk_id}",
                document=f"""
Ürün: {product_name}
Risk: {description}
Risk şiddeti: {severity}
""",
                product=product,
                chunk_type="risk",
                entity_id=risk_id,
                extra_metadata={"severity": severity},
            )

        for index, interaction in enumerate(
            product.get("interactions") or [],
            start=1,
        ):
            interacts_with = clean_text(
                interaction.get("interacts_with"),
                default="",
            )
            description = clean_text(
                interaction.get("description"),
                default="",
            )
            if not interacts_with and not description:
                continue

            interaction_id = int(interaction.get("id") or index)

            add_chunk(
                chunks,
                chunk_id=(
                    f"product:{product_id}:interaction:{interaction_id}"
                ),
                document=f"""
Ürün: {product_name}
Etkileşime girdiği madde veya ürün: {interacts_with}
Etkileşim açıklaması: {description}
""",
                product=product,
                chunk_type="interaction",
                entity_id=interaction_id,
                extra_metadata={"interacts_with": interacts_with},
            )

        for index, source in enumerate(product.get("sources") or [], start=1):
            title = clean_text(
                source.get("title"),
                default="Başlıksız kaynak",
            )
            source_type = clean_text(
                source.get("type"),
                default="Belirtilmemiş",
            )
            url = clean_text(
                source.get("url"),
                default="",
            )
            if not title and not url:
                continue

            source_id = int(source.get("id") or index)

            add_chunk(
                chunks,
                chunk_id=f"product:{product_id}:source:{source_id}",
                document=f"""
Ürün: {product_name}
Bilimsel kaynak başlığı: {title}
Kaynak türü: {source_type}
Kaynak bağlantısı: {url}
""",
                product=product,
                chunk_type="source",
                entity_id=source_id,
                extra_metadata={
                    "source_title": title,
                    "source_type": source_type,
                    "source_url": url,
                },
            )

    chunk_ids = [chunk["id"] for chunk in chunks]
    if len(chunk_ids) != len(set(chunk_ids)):
        raise RuntimeError(
            "Aynı Chroma kimliğine sahip birden fazla parça üretildi."
        )

    return chunks


def clear_collection() -> int:
    """Eski RAG indeksini temizler."""

    collection = get_product_collection()
    existing = collection.get(include=[])
    existing_ids = existing.get("ids") or []

    if existing_ids:
        collection.delete(ids=existing_ids)

    return len(existing_ids)


def rebuild_index() -> dict[str, int]:
    """Veritabanındaki tüm ürünlerle RAG indeksini yeniden oluşturur."""

    products = load_products()
    if not products:
        raise RuntimeError(
            "Veritabanından ürün alınamadı. İndeks oluşturulmadı."
        )

    chunks = build_product_chunks(products)
    if not chunks:
        raise RuntimeError(
            "Ürünlerden indekslenecek içerik üretilemedi."
        )

    collection = get_product_collection()
    removed_count = clear_collection()

    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=[chunk["document"] for chunk in chunks],
        metadatas=[chunk["metadata"] for chunk in chunks],
    )

    stored_count = collection.count()
    if stored_count != len(chunks):
        raise RuntimeError(
            "Chroma kayıt sayısı beklenen parça sayısıyla eşleşmiyor. "
            f"Beklenen: {len(chunks)}, kaydedilen: {stored_count}"
        )

    return {
        "product_count": len(products),
        "chunk_count": len(chunks),
        "removed_count": removed_count,
        "stored_count": stored_count,
    }


if __name__ == "__main__":
    result = rebuild_index()

    print("RAG indeksi başarıyla oluşturuldu.")
    print("Ürün sayısı:", result["product_count"])
    print("Oluşturulan parça:", result["chunk_count"])
    print("Silinen eski parça:", result["removed_count"])
    print("Chroma kayıt sayısı:", result["stored_count"])
