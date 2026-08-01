"""Görsel tanımanın güvenlik kapıları için offline kabul testi."""

from __future__ import annotations

import json
import os
import sys
import types
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

try:
    from openai import OpenAI as _OpenAI  # noqa: F401
except (ImportError, ModuleNotFoundError):
    openai_stub = types.ModuleType("openai")
    openai_stub.OpenAI = object
    sys.modules["openai"] = openai_stub

import ai.identify as identify_module
from ai.identify import (
    _parse_response,
    _parse_verification_response,
    _profile_for_identification,
)
from ai.image_validation import detect_image_mime
from schemas.identify import IdentifyResponse


def sample_products() -> list[dict]:
    return [
        {
            "id": 2,
            "name": "Kediotu",
            "category_id": 1,
            "usage_purpose": "Uyku kalitesini destekleme",
            "evidence_level": None,
            "image_url": None,
            "category": {"id": 1, "name": "Uyku ve Dinlenme", "description": "", "search_count": 0},
        },
        {
            "id": 3,
            "name": "Çarkıfelek otu",
            "category_id": 2,
            "usage_purpose": "Stres ve zihinsel iyi oluş desteği",
            "evidence_level": None,
            "image_url": None,
            "category": {"id": 2, "name": "Stres ve Zihinsel İyi Oluş", "description": "", "search_count": 0},
        },
        {
            "id": 7,
            "name": "Aloe vera",
            "category_id": 6,
            "usage_purpose": "Cilt iyileşmesini destekleme",
            "evidence_level": None,
            "image_url": None,
            "category": {"id": 6, "name": "Cilt, Saç ve Tırnak Desteği", "description": "", "search_count": 0},
        },
        {
            "id": 14,
            "name": "Demir",
            "category_id": 5,
            "usage_purpose": "Yorgunluğu destekleme",
            "evidence_level": None,
            "image_url": None,
            "category": {"id": 5, "name": "Enerji ve Yorgunluk", "description": "", "search_count": 0},
        },
    ]


def payload(**overrides):
    value = {
        "is_plant": True,
        "identified_name": "Aloe vera",
        "identified_name_en": "Aloe",
        "scientific_name": "Aloe barbadensis miller",
        "confidence": "yüksek",
        "image_quality": "yeterli",
        "visible_parts": ["yaprak"],
        "distinguishing_features": [
            "Tabandan rozet oluşturan etli yapraklar görülüyor.",
            "Yaprak kenarlarında küçük dişler seçiliyor.",
        ],
        "alternative_candidates": [],
        "ambiguity_detected": False,
        "requires_additional_photo": False,
        "description": "Etli, yeşil ve rozet biçimli yapraklar görülüyor.",
    }
    value.update(overrides)
    return json.dumps(value, ensure_ascii=False)


def verification_payload(**overrides):
    value = {
        "accepted": True,
        "confidence": "yüksek",
        "observed_supporting_features": [
            "Etli rozet yapraklar",
            "Küçük kenar dişleri",
        ],
        "missing_features": [],
        "contradictions": [],
        "needs_second_photo": False,
        "reason": "Görünen özellikler Aloe vera ile uyumlu.",
    }
    value.update(overrides)
    return json.dumps(value, ensure_ascii=False)


class FakeMessage:
    def __init__(self, content: str):
        self.content = content


class FakeChoice:
    def __init__(self, content: str):
        self.message = FakeMessage(content)


class FakeResponse:
    def __init__(self, content: str):
        self.choices = [FakeChoice(content)]


def run_service(first_payload: str, second_payload: str | None, products: list[dict]):
    responses = [FakeResponse(first_payload)]
    if second_payload is not None:
        responses.append(FakeResponse(second_payload))

    original_client = identify_module.get_groq_client
    original_completion = identify_module.vision_completion
    calls = []

    try:
        identify_module.get_groq_client = lambda: object()

        def fake_completion(*args, **kwargs):
            calls.append((args, kwargs))
            if not responses:
                raise AssertionError("Beklenmeyen ek model çağrısı yapıldı.")
            return responses.pop(0)

        identify_module.vision_completion = fake_completion
        result = identify_module.identify_image(
            b"fake-image-bytes",
            "image/jpeg",
            products=products,
        )
    finally:
        identify_module.get_groq_client = original_client
        identify_module.vision_completion = original_completion

    return result, len(calls)


def main() -> None:
    products = sample_products()

    parsed = _parse_response(payload())
    assert parsed["identified_name"] == "Aloe vera"
    assert parsed["confidence"] == "yüksek"
    assert parsed["image_quality"] == "yeterli"
    assert parsed["ambiguity_detected"] is False
    assert _profile_for_identification(parsed).product_name == "Aloe vera"

    accepted = _parse_verification_response(verification_payload())
    assert accepted["accepted"] is True

    rejected = _parse_verification_response(
        verification_payload(
            accepted=True,
            contradictions=["Yapraklar agave biçiminde sert ve lifli görünüyor."],
        )
    )
    assert rejected["accepted"] is False

    ambiguous = _parse_response(
        payload(
            identified_name="Çarkıfelek otu",
            scientific_name="Passiflora incarnata",
            confidence="yüksek",
            image_quality="sınırlı",
            alternative_candidates=[
                {"name": "Kediotu", "scientific_name": "Valeriana officinalis"}
            ],
            ambiguity_detected=True,
            requires_additional_photo=True,
        )
    )
    assert ambiguous["confidence"] == "orta"
    assert ambiguous["ambiguity_detected"] is True

    successful_result, successful_calls = run_service(
        payload(),
        verification_payload(),
        products,
    )
    assert successful_calls == 2
    assert successful_result["catalog_match_status"] == "matched"
    assert [item["name"] for item in successful_result["matched_products"]] == ["Aloe vera"]
    assert successful_result["verification"]["accepted"] is True

    uncertain_result, uncertain_calls = run_service(
        payload(
            identified_name="Çarkıfelek otu",
            identified_name_en="Passionflower",
            scientific_name="Passiflora incarnata",
            confidence="orta",
            image_quality="sınırlı",
            alternative_candidates=[
                {"name": "Kediotu", "scientific_name": "Valeriana officinalis"}
            ],
            ambiguity_detected=True,
            requires_additional_photo=True,
            description="Yalnızca küçük pembe çiçek kümeleri seçiliyor.",
        ),
        None,
        products,
    )
    assert uncertain_calls == 1
    assert uncertain_result["matched_products"] == []
    assert uncertain_result["catalog_match_status"] == "needs_more_evidence"
    assert uncertain_result["requires_additional_photo"] is True

    verifier_rejected_result, verifier_calls = run_service(
        payload(),
        verification_payload(
            accepted=False,
            confidence="orta",
            missing_features=["Yaprak kenarı net değil"],
            needs_second_photo=True,
            reason="Tür düzeyinde doğrulama için ikinci açı gerekli.",
        ),
        products,
    )
    assert verifier_calls == 2
    assert verifier_rejected_result["matched_products"] == []
    assert verifier_rejected_result["catalog_match_status"] == "needs_more_evidence"

    non_plant_result, non_plant_calls = run_service(
        payload(
            is_plant=False,
            identified_name="Belirlenemedi",
            identified_name_en=None,
            scientific_name=None,
            confidence="düşük",
            image_quality="yeterli",
            visible_parts=[],
            distinguishing_features=[],
            description="Görselde bir klavye bulunuyor.",
        ),
        None,
        products,
    )
    assert non_plant_calls == 1
    assert non_plant_result["status"] == "not_plant"
    assert non_plant_result["matched_products"] == []

    medical = _parse_response(
        payload(description="Cilt hastalıklarına iyi gelir ve tedavi için kullanılmalıdır.")
    )
    assert medical["description"] == "Görsel özelliklere göre botanik bir tahmin oluşturuldu."

    assert detect_image_mime(b"\xff\xd8\xff\xe0test") == "image/jpeg"
    assert detect_image_mime(b"\x89PNG\r\n\x1a\ntest") == "image/png"
    assert detect_image_mime(b"RIFF1234WEBPtest") == "image/webp"
    assert detect_image_mime(b"not-an-image") is None

    response_payload = {
        **successful_result,
        "disclaimer": "Test uyarısı",
    }
    validated = IdentifyResponse.model_validate(response_payload)
    assert validated.catalog_match_status == "matched"
    assert validated.verification is not None
    assert validated.matched_products[0].name == "Aloe vera"

    project_root = Path(__file__).resolve().parents[1]
    page = (project_root / "pages" / "gorsel-tanima.html").read_text(encoding="utf-8")
    css = (project_root / "css" / "style.css").read_text(encoding="utf-8")

    assert "RECOGNITION_DEMO" not in page
    assert "/products/identify" in page
    assert "İki aşamalı katalog doğrulaması tamamlandı" in page
    assert "Güvenli ürün bağlantısı oluşturulmadı" in page
    assert "alternative_candidates" in page
    assert ".catalog-empty-note--warning" in css

    print("GÖRSEL TANIMA GÜVENLİK KAPISI KABUL TESTİ BAŞARILI")
    print("- İlk botanik tahmin katalogdan bağımsız çalışıyor.")
    print("- Yalnızca yüksek güven ve yeterli kalite ikinci doğrulamaya geçiyor.")
    print("- Kediotu/çarkıfelek belirsizliğinde ürün bağlantısı kapatılıyor.")
    print("- İkinci doğrulama çelişki bulursa katalog eşleşmesi reddediliyor.")
    print("- Doğrulanan Aloe vera doğru ürün kaydına bağlanıyor.")
    print("- Bitki olmayan görsel tek model çağrısıyla güvenli reddediliyor.")
    print("- Tıbbi kullanım cümleleri nötrleştiriliyor.")
    print("- Yeni API yanıt şeması ve frontend güvenlik mesajları doğrulandı.")


if __name__ == "__main__":
    main()
