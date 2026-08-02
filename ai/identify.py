"""PhyraMed görsel tanıma servisi.

Sistem iki ayrı aşama kullanır:
1. Açık uçlu botanik tahmin: model katalog adlarına zorlanmaz.
2. Katalog doğrulaması: yalnızca güçlü ve tutarlı bir aday için ikinci görsel
   kontrolü yapılır. Belirsizlikte ürün bağlantısı oluşturulmaz.

Bu modül tıbbi kullanım, tanı veya doz önerisi üretmez.
"""

from __future__ import annotations

import base64
import json
import re
from dataclasses import dataclass
from typing import Any

from ai.groq_client import extract_model_text, get_groq_client, vision_completion
from ai.product_db import load_products, normalize

IDENTIFY_DISCLAIMER = (
    "Bu sonuç yapay zekâ destekli bir görsel tahmindir; kesin botanik teşhis "
    "veya tıbbi tavsiye değildir. Bitkiyi tüketmeden ya da cilde uygulamadan "
    "önce uzman görüşü alın."
)

VALID_CONFIDENCE_LEVELS = {"yüksek", "orta", "düşük"}
VALID_IMAGE_QUALITY_LEVELS = {"yeterli", "sınırlı", "yetersiz"}
VALID_CATALOG_MATCH_STATUSES = {
    "matched",
    "not_found",
    "needs_more_evidence",
    "not_applicable",
}


@dataclass(frozen=True)
class PlantProfile:
    product_name: str
    scientific_names: tuple[str, ...]
    common_names: tuple[str, ...]
    distinguishing_features: tuple[str, ...]
    confusion_warning: str


# Yalnızca kaynak bitkisi fotoğraftan anlamlı biçimde değerlendirilebilen
# katalog kayıtları bu kapalı doğrulama listesinde yer alır. Bilimsel adlar exact
# match ile kontrol edilir; tür düzeyi belirsizse ürün bağlantısı oluşturulmaz.
PLANT_PROFILES: tuple[PlantProfile, ...] = (
    PlantProfile(
        product_name="Kediotu",
        scientific_names=("Valeriana officinalis",),
        common_names=("Kediotu", "Valerian", "Garden valerian"),
        distinguishing_features=(
            "çok sayıda küçük beyaz veya soluk pembe çiçekten oluşan yoğun terminal kümeler",
            "karşılıklı dizilen teleksi veya parçalı yapraklar",
            "ince, dik ve dallanan gövde",
        ),
        confusion_warning=(
            "Çarkıfelek otu ile karıştırma. Passiflora türlerinde büyük, tekil ve "
            "radyal ipliksi taç yapılı çiçekler, sülükler ve çoğunlukla loplu yapraklar "
            "beklenir; bunlar yoksa Passiflora doğrulaması verme."
        ),
    ),
    PlantProfile(
        product_name="Çarkıfelek otu",
        scientific_names=("Passiflora incarnata",),
        common_names=("Çarkıfelek otu", "Passionflower", "Purple passionflower"),
        distinguishing_features=(
            "büyük ve tekil, karmaşık yapılı çiçek",
            "çiçeğin merkezinde belirgin radyal corona filamentleri",
            "tırmanıcı gövde, sülük ve çoğunlukla üç loplu yaprak",
        ),
        confusion_warning=(
            "Kediotu ile karıştırma. Valeriana officinalis büyük tekil passionflower "
            "çiçeği oluşturmaz; küçük çiçeklerden oluşan yoğun kümeleri ve parçalı "
            "yaprakları vardır."
        ),
    ),
    PlantProfile(
        product_name="Aloe vera",
        scientific_names=("Aloe vera", "Aloe barbadensis", "Aloe barbadensis miller"),
        common_names=("Aloe vera", "Aloe"),
        distinguishing_features=(
            "tabandan rozet oluşturan kalın etli yapraklar",
            "yaprak kenarlarında küçük dişler",
            "mızraksı, yeşil ve su depolayan yaprak dokusu",
        ),
        confusion_warning=(
            "Agave ve benzeri rozet sukulentlerle karıştırma. Yaprak dokusu ve kenar "
            "dişleri net değilse ikinci fotoğraf iste."
        ),
    ),
    PlantProfile(
        product_name="Zencefil",
        scientific_names=("Zingiber officinale",),
        common_names=("Zencefil", "Ginger"),
        distinguishing_features=(
            "dallanmış, boğumlu ve açık kahverengi rizom",
            "ince uzun mızraksı yapraklar",
            "kamış benzeri yalancı gövde",
        ),
        confusion_warning=(
            "Zerdeçal veya başka Zingiberaceae rizomlarıyla karıştırma. Tür düzeyi "
            "özellikleri görünmüyorsa katalog bağlantısı verme."
        ),
    ),
    PlantProfile(
        product_name="Lavanta",
        scientific_names=("Lavandula angustifolia",),
        common_names=("Lavanta", "English lavender", "Lavender"),
        distinguishing_features=(
            "ince gri-yeşil yapraklar",
            "uzun sap üzerinde başak biçimli mor çiçek kümeleri",
            "odunsu tabanlı çalı formu",
        ),
        confusion_warning=(
            "Salvia ve diğer mor başaklı türlerle karıştırma. Bilimsel tür net değilse "
            "ürün bağlantısı verme."
        ),
    ),
    PlantProfile(
        product_name="Ashwagandha",
        scientific_names=("Withania somnifera",),
        common_names=("Ashwagandha", "Hint ginsengi", "Indian ginseng"),
        distinguishing_features=(
            "oval ve hafif tüylü yapraklar",
            "küçük yeşilimsi çan biçimli çiçekler",
            "kâğıtsı çanak içinde turuncu-kırmızı meyve",
        ),
        confusion_warning=(
            "Physalis türleriyle karıştırma. Yaprak, çiçek ve meyve birlikte görünmüyorsa "
            "yüksek güven verme."
        ),
    ),
    PlantProfile(
        product_name="Ekinezya",
        scientific_names=("Echinacea purpurea",),
        common_names=("Ekinezya", "Purple coneflower", "Echinacea"),
        distinguishing_features=(
            "kabarık ve dikenimsi turuncu-kahverengi merkez",
            "aşağı doğru sarkan mor-pembe taç yapraklar",
            "dik gövde ve kaba dokulu yapraklar",
        ),
        confusion_warning=(
            "Rudbeckia ve benzeri papatyagillerle karıştırma. Merkez ve taç yaprak "
            "biçimi net değilse doğrulama verme."
        ),
    ),
    PlantProfile(
        product_name="Asya ginsengi",
        scientific_names=("Panax ginseng",),
        common_names=("Asya ginsengi", "Asian ginseng", "Korean ginseng"),
        distinguishing_features=(
            "tek noktadan yayılan çoğunlukla beş yaprakçıklı bileşik yaprak",
            "küçük yeşilimsi çiçeklerden oluşan şemsiye",
            "olgunlukta kırmızı meyve kümesi",
        ),
        confusion_warning=(
            "Amerikan ginsengi ve Aralia türleriyle karıştırma. Tür düzeyi kanıtı yoksa "
            "ürün bağlantısı verme."
        ),
    ),
    PlantProfile(
        product_name="Nane yağı",
        scientific_names=("Mentha piperita", "Mentha x piperita"),
        common_names=("Nane", "Peppermint"),
        distinguishing_features=(
            "karşılıklı dizilen dişli yapraklar",
            "kare kesitli gövde",
            "uçta morumsu çiçek başakları",
        ),
        confusion_warning=(
            "Mentha spicata ve diğer nane türleriyle karıştırma. Mentha türü kesin değilse "
            "Nane yağı katalog bağlantısı verme."
        ),
    ),
    PlantProfile(
        product_name="Çay ağacı yağı",
        scientific_names=("Melaleuca alternifolia",),
        common_names=("Çay ağacı", "Tea tree"),
        distinguishing_features=(
            "dar ve iğnemsi yapraklar",
            "beyaz, fırça görünümünde çiçek kümeleri",
            "ince kâğıtsı kabuk",
        ),
        confusion_warning=(
            "Camellia sinensis ile karıştırma. Tea tree yağı kaynağı Melaleuca "
            "alternifolia'dır; tür kesin değilse bağlantı verme."
        ),
    ),
)

PROFILE_BY_PRODUCT = {
    normalize(profile.product_name): profile
    for profile in PLANT_PROFILES
}


def _clean_single_line(value: Any, *, limit: int = 180) -> str | None:
    if value is None:
        return None

    text = " ".join(str(value).strip().split())
    if not text:
        return None

    return text[:limit]


def _clean_text_list(value: Any, *, limit: int = 4, item_limit: int = 140) -> list[str]:
    if not isinstance(value, list):
        return []

    cleaned: list[str] = []
    seen: set[str] = set()

    for item in value:
        text = _clean_single_line(item, limit=item_limit)
        if not text:
            continue
        key = normalize(text)
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(text)
        if len(cleaned) >= limit:
            break

    return cleaned


def _normalize_bool(value: Any) -> bool:
    if value is True:
        return True
    if value is False or value is None:
        return False
    return normalize(str(value)).strip() in {"true", "yes", "evet", "1"}


def _sanitize_description(value: Any) -> str | None:
    text = _clean_single_line(value, limit=280)
    if not text:
        return None

    normalized = normalize(text)
    forbidden_phrases = {
        "tedavi",
        "doz",
        "iyi gelir",
        "tuket",
        "kullanmal",
        "fayda",
        "hastal",
        "saglig",
    }

    if any(phrase in normalized for phrase in forbidden_phrases):
        return "Görsel özelliklere göre botanik bir tahmin oluşturuldu."

    return text


def _normalize_confidence(value: Any) -> str:
    text = normalize(str(value or ""))
    aliases = {
        "yuksek": "yüksek",
        "high": "yüksek",
        "orta": "orta",
        "medium": "orta",
        "moderate": "orta",
        "dusuk": "düşük",
        "low": "düşük",
        "belirsiz": "düşük",
        "uncertain": "düşük",
    }
    for token, normalized_value in aliases.items():
        if token in text:
            return normalized_value
    return "düşük"


def _normalize_image_quality(value: Any) -> str:
    text = normalize(str(value or ""))
    aliases = {
        "yeterli": "yeterli",
        "sufficient": "yeterli",
        "good": "yeterli",
        "sinirli": "sınırlı",
        "limited": "sınırlı",
        "partial": "sınırlı",
        "yetersiz": "yetersiz",
        "insufficient": "yetersiz",
        "poor": "yetersiz",
    }
    for token, normalized_value in aliases.items():
        if token in text:
            return normalized_value
    return "yetersiz"


def _build_identification_prompt() -> str:
    """Katalogdan bağımsız, açık uçlu botanik tahmin promptu."""

    return """
Sen PhyraMed için çalışan temkinli bir botanik görsel analiz asistanısın.
Görevin yalnızca fotoğrafta görülen ana bitkiyi değerlendirmektir.
Sana katalog listesi verilmez; bir ürüne uydurmak için tahmin yapma.
Dosya adı, ekran yazısı, etiket, çevre metni ve kullanıcı beklentisini yok say.

GÜVENLİK KURALLARI:
1. Görsel bitki değilse is_plant=false döndür.
2. Şişe, kapsül, tablet, toz, yağ şişesi, paket veya bitki çizimini canlı bitki
   olarak kabul etme.
3. Tür düzeyinde ayırt edici özellikler görünmüyorsa identified_name alanını
   "Belirlenemedi" yap, confidence="düşük" ve requires_additional_photo=true döndür.
4. Yalnızca çiçek görünüyor, yaprak/gövde görünmüyorsa ve çiçek tür için benzersiz
   değilse image_quality="sınırlı" ve requires_additional_photo=true döndür.
5. Birden fazla makul tür varsa ambiguity_detected=true yap ve en fazla iki
   alternative_candidates yaz. Böyle durumda yüksek güven verme.
6. Kediotu (Valeriana officinalis) ile çarkıfelek otunu (Passiflora incarnata)
   özellikle ayır:
   - Kediotu: çok sayıda küçük beyaz/pembe çiçekten oluşan yoğun kümeler,
     parçalı/teleksi karşılıklı yapraklar.
   - Çarkıfelek: büyük tekil karmaşık çiçek, radyal corona filamentleri,
     sülükler ve çoğunlukla loplu yapraklar.
   Bu ayırt edici yapılar görünmüyorsa iki türden biri için yüksek güven verme.
7. Sağlık faydası, tedavi, doz veya tüketim önerisi yazma.
8. Yanıt yalnızca geçerli JSON nesnesi olmalı; markdown veya ek açıklama ekleme.

JSON ŞEMASI:
{
  "is_plant": true,
  "identified_name": "Türkçe yaygın ad veya Belirlenemedi",
  "identified_name_en": "İngilizce yaygın ad veya null",
  "scientific_name": "Tür düzeyinde bilimsel ad veya null",
  "confidence": "yüksek|orta|düşük",
  "image_quality": "yeterli|sınırlı|yetersiz",
  "visible_parts": ["çiçek", "yaprak", "gövde"],
  "distinguishing_features": ["yalnızca görüntüde gerçekten görülen özellik"],
  "alternative_candidates": [
    {"name": "Alternatif yaygın ad", "scientific_name": "Bilimsel ad veya null"}
  ],
  "ambiguity_detected": false,
  "requires_additional_photo": false,
  "description": "Yalnızca görünür botanik özellikleri anlatan kısa cümle"
}
""".strip()


def _build_verification_prompt(profile: PlantProfile) -> str:
    features = "\n".join(f"- {item}" for item in profile.distinguishing_features)
    scientific = ", ".join(profile.scientific_names)

    return f"""
Bu ikinci ve bağımsız bir katalog doğrulama adımıdır.
Fotoğrafın şu PhyraMed katalog kaydıyla gerçekten uyumlu olup olmadığını denetle:

KATALOG ÜRÜNÜ: {profile.product_name}
KABUL EDİLEN BİLİMSEL TÜRLER: {scientific}
BEKLENEN AYIRT EDİCİ ÖZELLİKLER:
{features}

KRİTİK KARIŞIKLIK UYARISI:
{profile.confusion_warning}

KURALLAR:
1. Sadece fotoğrafta açıkça görülen özellikleri kullan.
2. Tür düzeyinde yeterli kanıt yoksa accepted=false döndür.
3. Çiçek, yaprak veya gövde gibi gerekli ayırt edici parçalar eksikse
   needs_second_photo=true döndür.
4. Herhangi bir çelişki varsa accepted=false döndür ve contradictions listesine yaz.
5. accepted=true yalnızca confidence="yüksek", contradictions boş ve
   needs_second_photo=false olduğunda kullanılabilir.
6. Yanıt yalnızca geçerli JSON nesnesi olmalı.

JSON ŞEMASI:
{{
  "accepted": false,
  "confidence": "yüksek|orta|düşük",
  "observed_supporting_features": ["fotoğrafta görülen destekleyici özellik"],
  "missing_features": ["görülmeyen gerekli özellik"],
  "contradictions": ["adayla çelişen görünür özellik"],
  "needs_second_photo": true,
  "reason": "Kısa ve tarafsız doğrulama gerekçesi"
}}
""".strip()


def _extract_json_object(text: str) -> dict[str, Any]:
    clean = extract_model_text(text).strip()
    clean = re.sub(r"^```(?:json)?\s*", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\s*```$", "", clean)

    try:
        value = json.loads(clean)
    except json.JSONDecodeError:
        start = clean.find("{")
        end = clean.rfind("}")
        if start == -1 or end <= start:
            raise ValueError("Model geçerli JSON üretmedi.")
        value = json.loads(clean[start : end + 1])

    if not isinstance(value, dict):
        raise ValueError("Model yanıtı JSON nesnesi değil.")

    return value


def _parse_alternatives(value: Any) -> list[dict[str, str | None]]:
    if not isinstance(value, list):
        return []

    alternatives: list[dict[str, str | None]] = []
    seen: set[str] = set()

    for item in value:
        if not isinstance(item, dict):
            continue
        name = _clean_single_line(item.get("name"), limit=100)
        scientific_name = _clean_single_line(item.get("scientific_name"), limit=120)
        if not name:
            continue
        key = normalize(f"{name} {scientific_name or ''}")
        if key in seen:
            continue
        seen.add(key)
        alternatives.append({"name": name, "scientific_name": scientific_name})
        if len(alternatives) >= 2:
            break

    return alternatives


def _parse_response(text: str, catalog_names: list[str] | None = None) -> dict[str, Any]:
    """İlk model JSON'unu doğrular ve güvenli alanlara dönüştürür.

    ``catalog_names`` geriye dönük test uyumluluğu için tutulur; açık uçlu ilk
    aşamada katalog bilgisi kullanılmaz.
    """

    del catalog_names
    raw = _extract_json_object(text)

    is_plant = _normalize_bool(raw.get("is_plant"))
    identified_name = _clean_single_line(raw.get("identified_name"), limit=100)
    identified_name_en = _clean_single_line(raw.get("identified_name_en"), limit=100)
    scientific_name = _clean_single_line(raw.get("scientific_name"), limit=120)
    confidence = _normalize_confidence(raw.get("confidence"))
    image_quality = _normalize_image_quality(raw.get("image_quality"))
    visible_parts = _clean_text_list(raw.get("visible_parts"), limit=6, item_limit=60)
    distinguishing_features = _clean_text_list(
        raw.get("distinguishing_features"),
        limit=5,
        item_limit=160,
    )
    alternatives = _parse_alternatives(raw.get("alternative_candidates"))
    ambiguity_detected = _normalize_bool(raw.get("ambiguity_detected")) or bool(alternatives)
    requires_additional_photo = _normalize_bool(raw.get("requires_additional_photo"))
    description = _sanitize_description(raw.get("description"))

    if image_quality == "yetersiz":
        confidence = "düşük"
        requires_additional_photo = True

    if ambiguity_detected and confidence == "yüksek":
        confidence = "orta"

    if not is_plant:
        return {
            "is_plant": False,
            "identified_name": "Belirlenemedi",
            "identified_name_en": None,
            "scientific_name": None,
            "confidence": "düşük",
            "image_quality": image_quality,
            "visible_parts": visible_parts,
            "distinguishing_features": distinguishing_features,
            "alternative_candidates": [],
            "ambiguity_detected": False,
            "requires_additional_photo": False,
            "description": description or "Görselde güvenilir biçimde tanımlanabilen bir bitki bulunamadı.",
        }

    if not identified_name or normalize(identified_name) in {"belirlenemedi", "unknown"}:
        return {
            "is_plant": True,
            "identified_name": "Belirlenemedi",
            "identified_name_en": identified_name_en,
            "scientific_name": scientific_name,
            "confidence": "düşük",
            "image_quality": image_quality,
            "visible_parts": visible_parts,
            "distinguishing_features": distinguishing_features,
            "alternative_candidates": alternatives,
            "ambiguity_detected": ambiguity_detected,
            "requires_additional_photo": True,
            "description": description or "Görsel bir bitki içeriyor ancak tür güvenilir biçimde belirlenemedi.",
        }

    return {
        "is_plant": True,
        "identified_name": identified_name,
        "identified_name_en": identified_name_en,
        "scientific_name": scientific_name,
        "confidence": confidence,
        "image_quality": image_quality,
        "visible_parts": visible_parts,
        "distinguishing_features": distinguishing_features,
        "alternative_candidates": alternatives,
        "ambiguity_detected": ambiguity_detected,
        "requires_additional_photo": requires_additional_photo,
        "description": description or "Görsel özelliklere göre botanik bir tahmin oluşturuldu.",
    }


def _parse_verification_response(text: str) -> dict[str, Any]:
    raw = _extract_json_object(text)
    confidence = _normalize_confidence(raw.get("confidence"))
    contradictions = _clean_text_list(raw.get("contradictions"), limit=4, item_limit=160)
    missing_features = _clean_text_list(raw.get("missing_features"), limit=4, item_limit=160)
    supporting_features = _clean_text_list(
        raw.get("observed_supporting_features"),
        limit=4,
        item_limit=160,
    )
    needs_second_photo = _normalize_bool(raw.get("needs_second_photo"))
    accepted = _normalize_bool(raw.get("accepted"))
    reason = _clean_single_line(raw.get("reason"), limit=280)

    accepted = bool(
        accepted
        and confidence == "yüksek"
        and not contradictions
        and not needs_second_photo
    )

    return {
        "accepted": accepted,
        "confidence": confidence,
        "observed_supporting_features": supporting_features,
        "missing_features": missing_features,
        "contradictions": contradictions,
        "needs_second_photo": needs_second_photo,
        "reason": reason or "Katalog doğrulaması için yeterli açıklama üretilemedi.",
    }


def _profile_for_identification(parsed: dict[str, Any]) -> PlantProfile | None:
    """Bilimsel veya yaygın ad üzerinden exact profile adayı bulur."""

    scientific = normalize(parsed.get("scientific_name") or "").strip()
    common_candidates = {
        normalize(parsed.get("identified_name") or "").strip(),
        normalize(parsed.get("identified_name_en") or "").strip(),
    }

    for profile in PLANT_PROFILES:
        scientific_names = {normalize(name) for name in profile.scientific_names}
        common_names = {normalize(name) for name in profile.common_names}

        if scientific and scientific in scientific_names:
            return profile

        if not scientific and any(candidate in common_names for candidate in common_candidates if candidate):
            return profile

    return None


def _catalog_product_for_profile(profile: PlantProfile, products: list[dict]) -> dict | None:
    expected_name = normalize(profile.product_name)
    for product in products:
        if normalize(product.get("name", "")) == expected_name:
            return product
    return None


def _can_attempt_catalog_verification(parsed: dict[str, Any]) -> bool:
    return bool(
        parsed.get("is_plant")
        and parsed.get("identified_name") != "Belirlenemedi"
        and parsed.get("confidence") == "yüksek"
        and parsed.get("image_quality") == "yeterli"
        and not parsed.get("ambiguity_detected")
        and not parsed.get("requires_additional_photo")
    )


def _verify_candidate(
    client: Any,
    data_url: str,
    profile: PlantProfile,
) -> dict[str, Any]:
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": _build_verification_prompt(profile)},
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        }
    ]
    response = vision_completion(
        client,
        messages,
        max_tokens=500,
        temperature=0.0,
        response_format={"type": "json_object"},
    )
    raw_text = response.choices[0].message.content or ""
    return _parse_verification_response(raw_text)


def identify_image(
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
    *,
    products: list[dict] | None = None,
) -> dict[str, Any]:
    """Görseli analiz eder ve yalnızca doğrulanmış katalog bağlantısı döndürür."""

    catalog_products = products if products is not None else load_products()
    client = get_groq_client()

    if not client:
        return {
            "status": "unavailable",
            "is_plant": False,
            "identified_name": "Belirlenemedi",
            "identified_name_en": None,
            "scientific_name": None,
            "confidence": "düşük",
            "image_quality": "yetersiz",
            "visible_parts": [],
            "distinguishing_features": [],
            "alternative_candidates": [],
            "requires_additional_photo": False,
            "catalog_match_status": "not_applicable",
            "match_explanation": "Görsel analiz servisi şu anda kullanılamıyor.",
            "description": "Görsel analiz servisi şu anda kullanılamıyor. API anahtarı yapılandırmasını kontrol edin.",
            "matched_products": [],
        }

    b64_image = base64.b64encode(image_bytes).decode("ascii")
    data_url = f"data:{mime_type};base64,{b64_image}"

    identification_messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": _build_identification_prompt()},
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        }
    ]

    try:
        response = vision_completion(
            client,
            identification_messages,
            max_tokens=650,
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        raw_text = response.choices[0].message.content or ""
        parsed = _parse_response(raw_text)
    except Exception as error:
        print(f"[identify] İlk görsel analiz başarısız: {error}")
        return {
            "status": "unavailable",
            "is_plant": False,
            "identified_name": "Belirlenemedi",
            "identified_name_en": None,
            "scientific_name": None,
            "confidence": "düşük",
            "image_quality": "yetersiz",
            "visible_parts": [],
            "distinguishing_features": [],
            "alternative_candidates": [],
            "requires_additional_photo": False,
            "catalog_match_status": "not_applicable",
            "match_explanation": "Görsel analiz geçici bir hata nedeniyle tamamlanamadı.",
            "description": "Görsel analiz sırasında geçici bir sorun oluştu. Lütfen tekrar deneyin.",
            "matched_products": [],
        }

    matched_products: list[dict] = []
    profile = _profile_for_identification(parsed)
    verification: dict[str, Any] | None = None

    if not parsed["is_plant"]:
        catalog_match_status = "not_applicable"
        match_explanation = "Görselde katalog eşleştirmesi yapılabilecek bir bitki tespit edilmedi."
    elif not profile:
        catalog_match_status = "not_found"
        match_explanation = "Botanik tahmin PhyraMed kataloğundaki tür düzeyinde bir kayıtla eşleşmedi."
    elif not _can_attempt_catalog_verification(parsed):
        catalog_match_status = "needs_more_evidence"
        match_explanation = (
            "Tahmin ürün bağlantısı oluşturmak için yeterince kesin değil. "
            "Yaprak, çiçek ve gövdeyi birlikte gösteren daha net bir fotoğraf deneyin."
        )
        parsed["requires_additional_photo"] = True
    else:
        try:
            verification = _verify_candidate(client, data_url, profile)
        except Exception as error:
            print(f"[identify] Katalog doğrulaması başarısız: {error}")
            verification = {
                "accepted": False,
                "confidence": "düşük",
                "observed_supporting_features": [],
                "missing_features": [],
                "contradictions": [],
                "needs_second_photo": True,
                "reason": "İkinci katalog doğrulaması tamamlanamadı.",
            }

        if verification["accepted"]:
            product = _catalog_product_for_profile(profile, catalog_products)
            if product:
                matched_products = [product]
                catalog_match_status = "matched"
                match_explanation = (
                    "Botanik tahmin, tür düzeyindeki bilimsel ad ve ikinci görsel "
                    "doğrulama ile PhyraMed kaydına bağlandı."
                )
            else:
                catalog_match_status = "not_found"
                match_explanation = "Doğrulanan bitki için güncel PhyraMed ürün kaydı bulunamadı."
        else:
            catalog_match_status = "needs_more_evidence"
            match_explanation = (
                verification.get("reason")
                or "İkinci doğrulama katalog bağlantısı için yeterli kanıt bulamadı."
            )
            parsed["requires_additional_photo"] = True

    if not parsed["is_plant"]:
        status = "not_plant"
    elif (
        parsed["identified_name"] == "Belirlenemedi"
        or parsed["confidence"] == "düşük"
        or parsed["image_quality"] == "yetersiz"
        or parsed.get("ambiguity_detected")
    ):
        status = "uncertain"
    else:
        status = "identified"

    return {
        "status": status,
        "is_plant": parsed["is_plant"],
        "identified_name": parsed["identified_name"],
        "identified_name_en": parsed["identified_name_en"],
        "scientific_name": parsed["scientific_name"],
        "confidence": parsed["confidence"],
        "image_quality": parsed["image_quality"],
        "visible_parts": parsed["visible_parts"],
        "distinguishing_features": parsed["distinguishing_features"],
        "alternative_candidates": parsed["alternative_candidates"],
        "requires_additional_photo": parsed["requires_additional_photo"],
        "catalog_match_status": catalog_match_status,
        "match_explanation": match_explanation,
        "description": parsed["description"],
        "matched_products": matched_products,
        "verification": verification,
    }
