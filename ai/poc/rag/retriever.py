"""Hibrit retrieval — semantik (Chroma) + anahtar kelime (product_db)."""

import sys
from pathlib import Path
from typing import List, Set

POC_DIR = Path(__file__).resolve().parents[1]
if str(POC_DIR) not in sys.path:
    sys.path.insert(0, str(POC_DIR))

from product_db import get_product_by_id, search_products
from .indexer import index_products
from .store import get_collection


def _ensure_index():
    collection = get_collection()
    if collection.count() == 0:
        index_products()


def semantic_retrieve(query: str, top_k: int = 5) -> List[dict]:
    """ChromaDB ile semantik arama."""

    _ensure_index()
    collection = get_collection()

    results = collection.query(
        query_texts=[query],
        n_results=min(top_k, max(collection.count(), 1)),
    )

    chunks = []
    for i, doc_id in enumerate(results["ids"][0]):
        metadata = results["metadatas"][0][i]
        chunks.append(
            {
                "chunk_id": doc_id,
                "text": results["documents"][0][i],
                "score": 1.0 - (results["distances"][0][i] if results["distances"] else 0),
                "product_id": metadata["product_id"],
                "product_name": metadata["product_name"],
                "field": metadata["field"],
                "source": "semantic",
            }
        )

    return chunks


def keyword_retrieve(query: str, limit: int = 3) -> List[dict]:
    """Anahtar kelime tabanlı ürün arama."""

    products = search_products(query, limit=limit)
    chunks = []

    for rank, product in enumerate(products):
        chunks.append(
            {
                "chunk_id": f"kw:{product['id']}",
                "text": (
                    f"Ürün: {product['name']}\n"
                    f"Kategori: {product['category']}\n"
                    f"Kullanım: {product['usage_purpose']}\n"
                    f"İddia: {product['claim']}\n"
                    f"Kanıt: {product['evidence_summary']}\n"
                    f"Riskler: {product['risk_summary']}"
                ),
                "score": 1.0 - (rank * 0.1),
                "product_id": product["id"],
                "product_name": product["name"],
                "field": "full_product",
                "source": "keyword",
            }
        )

    return chunks


def rerank_chunks(query: str, chunks: List[dict], top_k: int = 5) -> List[dict]:
    """
    Re-ranking: semantik benzerlik + query-keyword overlap + field importance.
    
    Args:
        query: Kullanıcı sorgusu
        chunks: Retrieved chunk'lar
        top_k: Dönecek chunk sayısı
        
    Returns:
        Re-ranked chunk listesi
    """
    query_lower = query.lower()
    query_terms: Set[str] = set(query_lower.split())
    
    # Alan ağırlıkları (evidence_summary daha önemli)
    field_weights = {
        "evidence_summary": 1.5,
        "claim": 1.3,
        "risk_summary": 1.2,
        "usage_purpose": 1.1,
        "name": 1.0,
        "category": 0.9,
        "plant": 0.8,
        "keywords": 0.7,
        "interaction_summary": 1.2,
    }
    
    for chunk in chunks:
        # Semantic skor (mevcut)
        semantic_score = chunk["score"]
        
        # Keyword overlap skoru
        chunk_text_lower = chunk["text"].lower()
        overlap = len(query_terms & set(chunk_text_lower.split())) / max(len(query_terms), 1)
        
        # Alan ağırlığı
        field_weight = field_weights.get(chunk.get("field", ""), 1.0)
        
        # Combined skor
        chunk["rerank_score"] = (
            semantic_score * 0.6 +          # Semantic %60
            overlap * 0.3 +                 # Keyword overlap %30  
            field_weight * 0.1              # Field importance %10
        )
    
    # Re-ranking
    reranked = sorted(chunks, key=lambda c: c["rerank_score"], reverse=True)
    return reranked[:top_k]


def hybrid_retrieve(query: str, top_k: int = 5, use_rerank: bool = True) -> dict:
    """
    Semantik + keyword sonuçlarını birleştirir ve re-ranking yapar.
    Dönüş: { chunks, products, product_ids }
    """

    semantic = semantic_retrieve(query, top_k=top_k * 2)  # Re-ranking için daha fazla al
    keyword = keyword_retrieve(query, limit=3)

    seen_chunks: Set[str] = set()
    merged_chunks: List[dict] = []

    for chunk in keyword + semantic:
        key = f"{chunk['product_id']}:{chunk.get('field', '')}"
        if key in seen_chunks:
            continue
        seen_chunks.add(key)
        merged_chunks.append(chunk)

    if use_rerank:
        merged_chunks = rerank_chunks(query, merged_chunks, top_k)
    else:
        merged_chunks.sort(key=lambda c: c["score"], reverse=True)
        merged_chunks = merged_chunks[:top_k]

    product_ids = list(dict.fromkeys(c["product_id"] for c in merged_chunks))
    products = [p for pid in product_ids if (p := get_product_by_id(pid))]

    return {
        "chunks": merged_chunks,
        "products": products,
        "product_ids": product_ids,
    }
