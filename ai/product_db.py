"""Ürün veritabanı erişimi — backend API'sinden çekiyor (Sprint 2)."""

import os
import re
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def load_products() -> list[dict]:
    """Backend'deki /products endpoint'inden gerçek ürünleri çeker."""
    try:
        resp = requests.get(f"{API_BASE_URL}/products/", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"[product_db] API'ye ulaşılamadı: {e}")
        return []


def get_product_by_id(product_id: int) -> dict | None:
    try:
        resp = requests.get(f"{API_BASE_URL}/products/{product_id}", timeout=5)
        if resp.status_code == 200:
            return resp.json()
        return None
    except requests.RequestException:
        return None


STOPWORDS = {
    "için", "icin", "bir", "bu", "ne", "mi", "mı", "mu", "mü",
    "ve", "ile", "var", "olan", "gibi", "daha", "çok", "cok",
    "iyi", "gelir", "önerirsiniz", "onerirsiniz",
    "nasıl", "nasil", "hangi", "hakkında", "hakkinda"
}


def normalize(text: str) -> str:
    """Türkçe karakterleri normalize eder."""
    text = (text or "").lower()
    replacements = {
        "ç": "c",
        "ğ": "g",
        "ı": "i",
        "ö": "o",
        "ş": "s",
        "ü": "u",
    }
    for tr, en in replacements.items():
        text = text.replace(tr, en)
    return text


def search_products(query: str, limit: int = 3) -> list[dict]:
    """Anahtar kelime bazlı ürün arama (gerçek DB şemasına göre)."""

    q = normalize(query)

    tokens = {
        t
        for t in re.findall(r"\w+", q)
        if len(t) >= 3 and t not in STOPWORDS
    }

    scored = []

    for product in load_products():

        score = 0

        name = normalize(product.get("name", ""))
        usage = normalize(product.get("usage_purpose", ""))
        summary = normalize(product.get("expert_opinion_summary", ""))

        category_obj = product.get("category") or {}
        category_name = normalize(category_obj.get("name", ""))

        risk_texts = " ".join(
            normalize(r.get("description", "")) for r in product.get("risks", [])
        )
        source_texts = " ".join(
            normalize(s.get("title", "")) for s in product.get("sources", [])
        )
        interaction_texts = " ".join(
            normalize(i.get("interacts_with", "")) + " " + normalize(i.get("description", ""))
            for i in product.get("interactions", [])
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
            scored.append((score, product))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [p for score, p in scored[:limit]]


def format_product_context(products: list[dict]) -> str:

    if not products:
        return "İlgili ürün bulunamadı."

    blocks = []

    for p in products:

        category_obj = p.get("category") or {}
        category_name = category_obj.get("name", "Belirtilmemiş")

        risks = ", ".join(
            f"{r.get('description')} (şiddet: {r.get('severity') or 'belirtilmemiş'})"
            for r in p.get("risks", [])
        ) or "Belirtilmemiş"

        sources = ", ".join(
            s.get("title") or s.get("url") for s in p.get("sources", [])
        ) or "Belirtilmemiş"

        interactions = ", ".join(
            f"{i.get('interacts_with')}: {i.get('description') or 'detay yok'}"
            for i in p.get("interactions", [])
        ) or "Belirtilmemiş"

        blocks.append(
            f"Ürün: {p.get('name')}\n"
            f"Kategori: {category_name}\n"
            f"Kullanım amacı: {p.get('usage_purpose')}\n"
            f"Kanıt seviyesi: {p.get('evidence_level')}\n"
            f"Uzman görüşü özeti: {p.get('expert_opinion_summary')}\n"
            f"Riskler: {risks}\n"
            f"Kaynaklar: {sources}\n"
            f"Etkileşimler: {interactions}"
        )

    return "\n\n---\n\n".join(blocks)