"""Çalışan backend üzerindeki iki aşamalı görsel tanıma endpointini test eder.

Kullanım:
    python -m ai.inspect_identify_api "C:\\path\\aloe.jpg" "Aloe vera"

İkinci argüman isteğe bağlıdır. Beklenen ad verilirse tahminde veya doğrulanmış
üründe bulunması gerekir.
"""

from __future__ import annotations

import json
import mimetypes
import os
from pathlib import Path
import sys
import time
import unicodedata

import requests

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
VALID_STATUSES = {"identified", "uncertain", "not_plant", "unavailable"}
VALID_CONFIDENCE = {"yüksek", "orta", "düşük"}
VALID_QUALITY = {"yeterli", "sınırlı", "yetersiz"}
VALID_CATALOG_STATUSES = {
    "matched",
    "not_found",
    "needs_more_evidence",
    "not_applicable",
}


def normalize(value: object) -> str:
    text = str(value or "").casefold().replace("ı", "i")
    text = unicodedata.normalize("NFKD", text)
    return "".join(character for character in text if not unicodedata.combining(character))


def fail(message: str) -> None:
    print(f"GÖRSEL TANIMA API TESTİ BAŞARISIZ: {message}")
    raise SystemExit(1)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Kullanım: python -m ai.inspect_identify_api "
            '"C:\\path\\bitki.jpg" "Beklenen ürün adı"'
        )
        raise SystemExit(2)

    image_path = Path(sys.argv[1]).expanduser().resolve()
    expected_name = sys.argv[2].strip() if len(sys.argv) >= 3 else None

    if not image_path.is_file():
        fail(f"Görsel bulunamadı: {image_path}")

    mime_type = mimetypes.guess_type(image_path.name)[0]
    if mime_type not in ALLOWED_MIME_TYPES:
        fail("Dosya uzantısı JPEG, PNG veya WEBP olmalı.")

    api_base = os.getenv("PHYRAMED_API_BASE", "http://127.0.0.1:8000").rstrip("/")
    endpoint = f"{api_base}/products/identify"

    started_at = time.perf_counter()
    try:
        with image_path.open("rb") as image_file:
            response = requests.post(
                endpoint,
                files={"file": (image_path.name, image_file, mime_type)},
                timeout=90,
            )
    except requests.RequestException as error:
        fail(f"Backend isteği tamamlanamadı: {error}")

    elapsed = time.perf_counter() - started_at

    try:
        payload = response.json()
    except ValueError:
        fail(f"API JSON döndürmedi. HTTP {response.status_code}: {response.text[:300]}")

    if response.status_code != 200:
        fail(f"HTTP {response.status_code}: {payload}")

    required_fields = {
        "status",
        "is_plant",
        "identified_name",
        "confidence",
        "image_quality",
        "alternative_candidates",
        "requires_additional_photo",
        "catalog_match_status",
        "match_explanation",
        "description",
        "matched_products",
        "disclaimer",
    }
    missing_fields = sorted(required_fields - payload.keys())
    if missing_fields:
        fail(f"Yanıtta alanlar eksik: {missing_fields}")

    if payload["status"] not in VALID_STATUSES:
        fail(f"Geçersiz status: {payload['status']}")
    if payload["confidence"] not in VALID_CONFIDENCE:
        fail(f"Geçersiz confidence: {payload['confidence']}")
    if payload["image_quality"] not in VALID_QUALITY:
        fail(f"Geçersiz image_quality: {payload['image_quality']}")
    if payload["catalog_match_status"] not in VALID_CATALOG_STATUSES:
        fail(f"Geçersiz catalog_match_status: {payload['catalog_match_status']}")
    if not isinstance(payload["matched_products"], list):
        fail("matched_products liste değil.")
    if not isinstance(payload["alternative_candidates"], list):
        fail("alternative_candidates liste değil.")
    if payload["status"] == "unavailable":
        fail(f"AI servisi kullanılamıyor: {payload['description']}")

    matched_names = [
        str(product.get("name") or "")
        for product in payload["matched_products"]
        if isinstance(product, dict)
    ]

    if payload["catalog_match_status"] == "matched":
        if not matched_names:
            fail("catalog_match_status=matched ancak ürün listesi boş.")
        verification = payload.get("verification")
        if not isinstance(verification, dict) or verification.get("accepted") is not True:
            fail("Doğrulanmış katalog eşleşmesinde accepted=true doğrulaması yok.")
    elif matched_names:
        fail("Güvenlik kapısı geçilmeden katalog ürünü döndürüldü.")

    if expected_name:
        expected_normalized = normalize(expected_name)
        observed_names = [payload.get("identified_name", ""), *matched_names]
        if not any(expected_normalized in normalize(name) for name in observed_names):
            fail(
                "Beklenen ad bulunamadı. "
                f"Beklenen: {expected_name}; gözlenen: {observed_names}"
            )

    print("=" * 72)
    print("GÖRSEL TANIMA API TESTİ BAŞARILI")
    print(f"HTTP: {response.status_code}")
    print(f"Süre: {elapsed:.2f} saniye")
    print(f"Durum: {payload['status']}")
    print(f"Tahmin: {payload['identified_name']}")
    print(f"Güven: {payload['confidence']}")
    print(f"Görsel kalite: {payload['image_quality']}")
    print(f"Katalog kapısı: {payload['catalog_match_status']}")
    print(f"İkinci fotoğraf gerekli: {payload['requires_additional_photo']}")
    print(f"Katalog eşleşmeleri: {matched_names or 'Yok'}")
    print("YANIT:")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
