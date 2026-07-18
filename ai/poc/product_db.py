"""Ürün veritabanı erişimi — Sprint 2 chatbot için mock JSON DB."""

import json
import re
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "products_db.json"


def load_products() -> list[dict]:
    return json.loads(DB_PATH.read_text(encoding="utf-8"))


def get_product_by_id(product_id: int) -> dict | None:
    for p in load_products():
        if p["id"] == product_id:
            return p
    return None


STOPWORDS = {
    "için", "icin", "bir", "bu", "ne", "mi", "mı", "mu", "mü",
    "ve", "ile", "var", "olan", "gibi", "daha", "çok", "cok",
    "iyi", "gelir", "önerirsiniz", "onerirsiniz",
    "nasıl", "nasil", "hangi", "hakkında", "hakkinda"
}


def normalize(text: str) -> str:
    """Türkçe karakterleri normalize eder."""
    text = text.lower()
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
    """Anahtar kelime bazlı ürün arama."""

    q = normalize(query)

    tokens = {
        t
        for t in re.findall(r"\w+", q)
        if len(t) >= 3 and t not in STOPWORDS
    }

    scored = []

    for product in load_products():

        score = 0

        name = normalize(product["name"])
        category = normalize(product["category"])
        usage = normalize(product["usage_purpose"])
        claim = normalize(product["claim"])
        evidence = normalize(product["evidence_summary"])
        risk = normalize(product["risk_summary"])
        interaction = normalize(product["interaction_summary"])
        keywords = [normalize(k) for k in product.get("keywords", [])]

        for token in tokens:

            if token in name:
                score += 10

            if token in keywords:
                score += 8

            if token in usage:
                score += 6

            if token in claim:
                score += 5

            if token in category:
                score += 4

            if token in evidence:
                score += 2

            if token in risk:
                score += 1

            if token in interaction:
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
        blocks.append(
            f"Ürün: {p['name']}\n"
            f"Kategori: {p['category']}\n"
            f"Kullanım amacı: {p['usage_purpose']}\n"
            f"İddia: {p['claim']}\n"
            f"Kanıt seviyesi: {p['evidence_level']}\n"
            f"Bilimsel özet: {p['evidence_summary']}\n"
            f"Riskler: {p['risk_summary']}\n"
            f"Etkileşimler: {p['interaction_summary']}"
        )

    return "\n\n---\n\n".join(blocks)