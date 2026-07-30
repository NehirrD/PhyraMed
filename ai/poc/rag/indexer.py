"""Ürün veritabanını chunk'lara ayırıp vektör indeksine yazar."""

import sys
from pathlib import Path
from typing import List, Dict, Optional

POC_DIR = Path(__file__).resolve().parents[1]
if str(POC_DIR) not in sys.path:
    sys.path.insert(0, str(POC_DIR))

from ..product_db import load_products
from .store import get_collection

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

    keywords = product.get("keywords") or []
    if keywords:
        chunks.append(
            {
                "id": f"{product['id']}:keywords",
                "text": (
                    f"Ürün: {product['name']}\n"
                    f"Anahtar kelimeler: {', '.join(keywords)}"
                ),
                "metadata": {
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "field": "keywords",
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
