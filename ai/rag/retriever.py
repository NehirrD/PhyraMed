"""PhyraMed RAG için güvenli semantik ürün bulma katmanı.

Ürün seçimi yalnızca ``overview`` parçaları üzerinden yapılır. Kaynak, risk ve
etkileşim parçaları ürün seçildikten sonra bağlama eklenir. Böylece alakasız bir
kaynak başlığının yanlış ürünü öne çıkarması engellenir.
"""

from __future__ import annotations

import re
from typing import Any

from ai.rag.store import get_product_collection


_TURKISH_MAP = str.maketrans(
    {
        "ç": "c",
        "ğ": "g",
        "ı": "i",
        "ö": "o",
        "ş": "s",
        "ü": "u",
    }
)

_STOPWORDS = {
    "acaba",
    "ama",
    "bir",
    "bu",
    "da",
    "de",
    "gibi",
    "hangi",
    "hakkinda",
    "icin",
    "ile",
    "mi",
    "mu",
    "mı",
    "mü",
    "nasil",
    "ne",
    "nedir",
    "ve",
    "var",
}

# Yalnızca PhyraMed'in sağlık/takviye alanını işaret eden güçlü kökler.
# "ürün", "içerik", "kaynak", "güven" gibi genel kelimeler bilerek burada
# değildir; aksi halde teknoloji veya alışveriş soruları yanlış kabul edilebilir.
_DOMAIN_MARKERS = {
    "bagirsak",
    "bagisik",
    "bitki",
    "cilt",
    "dinlen",
    "enerji",
    "etkilesim",
    "kanit",
    "mide",
    "mineral",
    "rahatla",
    "sac",
    "saglik",
    "sindirim",
    "stres",
    "takviye",
    "tirnak",
    "uyku",
    "uyuma",
    "uyuy",
    "vitamin",
    "yorgun",
    "yan etki",
}

DEFAULT_MIN_SEMANTIC_SIMILARITY = 0.50
DEFAULT_MIN_SCORE = 0.54
DEFAULT_TOP_SCORE_MARGIN = 0.10


def normalize_text(value: Any) -> str:
    """Arama puanlaması için metni sadeleştirir."""

    text = str(value or "").strip().lower().translate(_TURKISH_MAP)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


def token_set(value: Any) -> set[str]:
    """Anlamlı arama kelimelerini döndürür."""

    return {
        token
        for token in normalize_text(value).split()
        if len(token) >= 3 and token not in _STOPWORDS
    }


def _flatten_query_result(result: dict[str, Any]) -> list[dict[str, Any]]:
    """Chroma'nın iç içe query çıktısını düz bir listeye çevirir."""

    ids = (result.get("ids") or [[]])[0]
    documents = (result.get("documents") or [[]])[0]
    metadatas = (result.get("metadatas") or [[]])[0]
    distances = (result.get("distances") or [[]])[0]

    rows: list[dict[str, Any]] = []

    for chunk_id, document, metadata, distance in zip(
        ids,
        documents,
        metadatas,
        distances,
        strict=False,
    ):
        raw_distance = float(distance)
        semantic_similarity = max(0.0, min(1.0, 1.0 - raw_distance))

        rows.append(
            {
                "chunk_id": chunk_id,
                "document": document or "",
                "metadata": metadata or {},
                "distance": raw_distance,
                "semantic_similarity": semantic_similarity,
            }
        )

    return rows


def _flatten_get_result(result: dict[str, Any]) -> list[dict[str, Any]]:
    """Chroma get çıktısını düz parça listesine dönüştürür."""

    ids = result.get("ids") or []
    documents = result.get("documents") or []
    metadatas = result.get("metadatas") or []

    return [
        {
            "chunk_id": chunk_id,
            "document": document or "",
            "metadata": metadata or {},
        }
        for chunk_id, document, metadata in zip(
            ids,
            documents,
            metadatas,
            strict=False,
        )
    ]


def _get_overview_rows() -> list[dict[str, Any]]:
    """İndeksteki bütün ürün özetlerini getirir."""

    collection = get_product_collection()
    result = collection.get(
        where={"chunk_type": "overview"},
        include=["documents", "metadatas"],
    )
    return _flatten_get_result(result)


def _matched_product_ids(query: str) -> set[int]:
    """Sorguda açıkça geçen ürün adlarının kimliklerini bulur."""

    normalized_query = normalize_text(query)
    matched_ids: set[int] = set()

    for row in _get_overview_rows():
        metadata = row["metadata"]
        product_name = normalize_text(metadata.get("product_name"))
        product_id = metadata.get("product_id")

        if product_name and product_id is not None and product_name in normalized_query:
            matched_ids.add(int(product_id))

    return matched_ids


def is_domain_relevant(query: str) -> bool:
    """Sorgunun PhyraMed kapsamıyla ilişkili olup olmadığını kontrol eder."""

    normalized_query = normalize_text(query)
    if not normalized_query:
        return False

    if _matched_product_ids(query):
        return True

    return any(marker in normalized_query for marker in _DOMAIN_MARKERS)


def search_overviews(query: str, n_results: int = 12) -> list[dict[str, Any]]:
    """Soruya en yakın ürün özetlerini puanlarıyla getirir."""

    clean_query = str(query or "").strip()
    if not clean_query:
        return []

    collection = get_product_collection()
    collection_count = collection.count()
    if collection_count == 0:
        return []

    result = collection.query(
        query_texts=[clean_query],
        n_results=min(max(1, n_results), collection_count),
        where={"chunk_type": "overview"},
        include=["documents", "metadatas", "distances"],
    )

    query_tokens = token_set(clean_query)
    normalized_query = normalize_text(clean_query)
    rows = _flatten_query_result(result)

    for row in rows:
        metadata = row["metadata"]
        product_name = normalize_text(metadata.get("product_name"))
        document_tokens = token_set(row["document"])

        lexical_overlap = len(query_tokens & document_tokens)
        exact_name_match = bool(product_name and product_name in normalized_query)

        lexical_bonus = min(0.15, lexical_overlap * 0.03)
        exact_name_bonus = 0.30 if exact_name_match else 0.0

        row["lexical_overlap"] = lexical_overlap
        row["exact_name_match"] = exact_name_match
        row["score"] = min(
            1.0,
            row["semantic_similarity"] + lexical_bonus + exact_name_bonus,
        )

    return sorted(
        rows,
        key=lambda item: (
            item["exact_name_match"],
            item["score"],
            item["semantic_similarity"],
        ),
        reverse=True,
    )


def _get_product_chunks(product_id: int) -> list[dict[str, Any]]:
    """Seçilen ürüne ait özet, risk, etkileşim ve kaynak parçalarını getirir."""

    collection = get_product_collection()
    result = collection.get(
        where={"product_id": int(product_id)},
        include=["documents", "metadatas"],
    )
    return _flatten_get_result(result)


def retrieve_products(
    query: str,
    *,
    max_products: int = 3,
    min_semantic_similarity: float = DEFAULT_MIN_SEMANTIC_SIMILARITY,
    min_score: float = DEFAULT_MIN_SCORE,
    top_score_margin: float = DEFAULT_TOP_SCORE_MARGIN,
) -> list[dict[str, Any]]:
    """Güvenlik kapısından geçen ilgili ürünleri ve tüm bağlamlarını döndürür.

    Kurallar:
    - Ürün adı açıkça geçiyorsa yalnızca adı geçen ürünler kabul edilir.
    - Ürün adı geçmiyorsa sorgu PhyraMed alanıyla ilişkili olmalıdır.
    - Semantik benzerlik ve toplam puan alt sınırları birlikte uygulanır.
    - Alt sıralardaki bir sonuç, en iyi sonuçtan çok uzaktaysa elenir.
    - Alakasız sorgularda boş liste döner; rastgele en yakın ürün verilmez.
    """

    clean_query = str(query or "").strip()
    if not clean_query:
        return []

    exact_product_ids = _matched_product_ids(clean_query)
    domain_relevant = is_domain_relevant(clean_query)

    if not exact_product_ids and not domain_relevant:
        return []

    overview_results = search_overviews(clean_query, n_results=18)
    selected: list[dict[str, Any]] = []
    best_eligible_score: float | None = None

    for row in overview_results:
        metadata = row.get("metadata") or {}
        product_id = metadata.get("product_id")
        if product_id is None:
            continue

        product_id = int(product_id)
        exact_name_match = product_id in exact_product_ids
        semantic_similarity = float(row["semantic_similarity"])
        score = float(row["score"])
        lexical_overlap = int(row.get("lexical_overlap", 0))

        if exact_product_ids and not exact_name_match:
            continue

        if not exact_name_match:
            if semantic_similarity < min_semantic_similarity:
                continue

            # Tek başına zayıf bir vektör yakınlığı yeterli değildir. Ya toplam
            # puan güçlü olmalı ya da sorguyla metin arasında gerçek kelime
            # desteği bulunmalıdır.
            if score < min_score and lexical_overlap == 0:
                continue

            if best_eligible_score is not None and (
                best_eligible_score - score > top_score_margin
            ):
                continue

        if best_eligible_score is None:
            best_eligible_score = score

        selected.append(
            {
                "product_id": product_id,
                "product_name": metadata.get("product_name", "Belirtilmemiş"),
                "category_name": metadata.get("category_name", "Belirtilmemiş"),
                "score": score,
                "semantic_similarity": semantic_similarity,
                "lexical_overlap": lexical_overlap,
                "retrieval_reason": (
                    "exact_product_name" if exact_name_match else "semantic_match"
                ),
                "chunks": _get_product_chunks(product_id),
            }
        )

        if len(selected) >= max(1, max_products):
            break

    return selected
