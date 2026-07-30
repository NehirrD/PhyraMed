"""Ürün veritabanını chunk'lara ayırıp vektör indeksine yazar."""

import sys
from pathlib import Path
from typing import List,Optional

# Path manipülasyonu - script olarak çalıştırma için
CURRENT_FILE = Path(__file__).resolve()
POC_DIR = CURRENT_FILE.parents[1]  # ai/poc  

if str(POC_DIR) not in sys.path:
    sys.path.insert(0, str(POC_DIR))

# Local import - script olarak çalıştırma
from product_db import load_products
from rag.store import get_collection

CHUNK_FIELDS = (
    "name",
    "category",
    "plant",
    "usage_purpose",
    "claim",
    "evidence_level",
    "evidence_summary",
    "risk_summary",
    "interaction_summary",
)


def product_to_chunks(product: dict) -> List[dict]:
    """Her ürün alanını ayrı bir retrieval chunk'ına çevirir."""

    chunks = []

    for field in CHUNK_FIELDS:
        value = product.get(field)
        if not value:
            continue

        chunks.append(
            {
                "id": f"{product['id']}:{field}",
                "text": (
                    f"Ürün: {product['name']}\n"
                    f"Alan: {field}\n"
                    f"İçerik: {value}"
                ),
                "metadata": {
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "field": field,
                },
            }
        )

    # Category chunk
    category_obj = product.get("category") or {}
    if category_obj.get("name"):
        chunks.append(
            {
                "id": f"{product['id']}:category",
                "text": (
                    f"Ürün: {product['name']}\n"
                    f"Kategori: {category_obj.get('name')}"
                ),
                "metadata": {
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "field": "category",
                },
            }
        )

    # Risks chunk
    risks = product.get("risks") or []
    if risks:
        risk_texts = [f"{r.get('description')} (şiddet: {r.get('severity')})" for r in risks]
        chunks.append(
            {
                "id": f"{product['id']}:risks",
                "text": (
                    f"Ürün: {product['name']}\n"
                    f"Riskler: {', '.join(risk_texts)}"
                ),
                "metadata": {
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "field": "risks",
                },
            }
        )

    # Sources chunk
    sources = product.get("sources") or []
    if sources:
        source_texts = [s.get("title") or s.get("url") for s in sources]
        chunks.append(
            {
                "id": f"{product['id']}:sources",
                "text": (
                    f"Ürün: {product['name']}\n"
                    f"Kaynaklar: {', '.join(source_texts)}"
                ),
                "metadata": {
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "field": "sources",
                },
            }
        )

    # Interactions chunk
    interactions = product.get("interactions") or []
    if interactions:
        interaction_texts = [
            f"{i.get('interacts_with')}: {i.get('description')}" for i in interactions
        ]
        chunks.append(
            {
                "id": f"{product['id']}:interactions",
                "text": (
                    f"Ürün: {product['name']}\n"
                    f"Etkileşimler: {', '.join(interaction_texts)}"
                ),
                "metadata": {
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "field": "interactions",
                },
            }
        )

    return chunks


def index_products(products: Optional[List[dict]] = None) -> int:
    """Ürünleri vektör store'a yazar; chunk sayısını döndürür."""

    products = products or load_products()
    collection = get_collection()

    all_chunks: List[dict] = []
    for product in products:
        all_chunks.extend(product_to_chunks(product))

    if not all_chunks:
        return 0

    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    collection.add(
        ids=[c["id"] for c in all_chunks],
        documents=[c["text"] for c in all_chunks],
        metadatas=[c["metadata"] for c in all_chunks],
    )

    return len(all_chunks)


def build_index() -> int:
    """CLI/script entry — indeksi oluşturur."""

    count = index_products()
    print(f"Indeks olusturuldu: {count} chunk")
    return count


if __name__ == "__main__":
    build_index()
