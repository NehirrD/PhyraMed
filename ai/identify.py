"""Görsel tanıma modülü - backend entegrasyonu için."""

import sys
import base64
import re
from pathlib import Path
from typing import Dict

# AI modülünü path'e ekle
AI_DIR = Path(__file__).resolve().parent
POC_DIR = AI_DIR / "poc"
if str(POC_DIR) not in sys.path:
    sys.path.insert(0, str(POC_DIR))

from groq_client import VISION_MODEL, extract_model_text, get_groq_client, vision_completion
from product_db import search_products

MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
}

PROMPT_V4 = (
    "Sen uzman bir botanik tanıma asistanısın.\n"
    "Görseldeki bitkiyi kesin olarak tanımla.\n\n"
    "KRİTİK ayırım kriterleri:\n"
    "1. ZERDEÇAL (Turmeric):\n"
    "   - Rizom kesitinde yoğun turuncu-sarı renk (kurkumin)\n"
    "   - Parlak, canlı pigment görünümü\n"
    "   - Kesit dokusu daha yoğun ve dolgun\n"
    "   - Genellikle daha küçük parçalar halinde\n\n"
    "2. ZENCEFİL (Ginger):\n"
    "   - Kesit rengi soluk sarı veya krem\n"
    "   - Daha lifli, damarlı görünüm\n"
    "   - Kabuk daha ince ve hafif sarımsı\n"
    "   - Keskin karakteristik aroma (görsel olarak)\n\n"
    "3. NANE (Mint):\n"
    "   - Yapraklı görünümlü, yeşil tonları\n"
    "   - Genellikle yaprak veya küçük filizler\n"
    "   - Keskin yeşil renk\n\n"
    "GÜVEN DEĞERLENDİRME:\n"
    "- yüksek: Özellikler %90+ eşleşiyor, ayırım net\n"
    "- orta: Özellikler %60-90 eşleşiyor, küçük belirsizlik var\n"
    "- düşük: Özellikler %60 altı eşleşiyor veya benzer bitkiler var\n\n"
    "Eğer görsel belirsiz, ışık kötü, veya ayırım mümkün değilse:\n"
    "- Bitki (TR): 'Belirsiz' yaz\n"
    "- Güven: 'düşük' yaz\n"
    "- Kısa not: Belirsizlik nedenini açıkla\n\n"
    "Yanıtı TAM olarak aşağıdaki formatta ver:\n\n"
    "Bitki (TR): <Türkçe adı veya Belirsiz>\n"
    "Bitki (EN): <İngilizce adı veya Unknown>\n"
    "Güven: <yüksek/orta/düşük>\n"
    "Kısa not: <1-2 cümle>"
)

UNCERTAIN_MESSAGE = (
    "Bu görselden bitkiyi kesin olarak tanımlayamıyorum. "
    "Lütfen daha net bir fotoğraf yükleyin veya farklı açıdan çekin."
)

IDENTIFY_DISCLAIMER = (
    "Bu tanıma otomatik bir sistem tarafından yapılmıştır. "
    "Kesin tanı için bir uzmana danışmanız önerilir."
)


def parse_vision_response(raw: str) -> dict:
    """Yapılandırılmış vision yanıtını parse eder."""

    clean = extract_model_text(raw)

    def extract_field(pattern: str, default: str = "") -> str:
        m = re.search(pattern, clean, re.IGNORECASE)
        return m.group(1).strip() if m else default

    plant_tr = extract_field(r"Bitki\s*\(\s*TR\s*\)\s*:\s*(.+)", "")
    plant_en = extract_field(r"Bitki\s*\(\s*EN\s*\)\s*:\s*(.+)", "")
    confidence = extract_field(r"Güven\s*:\s*(.+)", "orta").lower()
    note = extract_field(r"Kısa not\s*:\s*(.+)", "")

    if not plant_tr:
        plant_tr = clean.split("\n")[0].strip()

    return {
        "plant_tr": plant_tr,
        "plant_en": plant_en,
        "confidence": confidence,
        "note": note,
        "raw": clean,
    }


def is_uncertain(parsed: dict) -> bool:
    plant = parsed["plant_tr"].lower()
    confidence = parsed["confidence"]

    if confidence == "düşük" or confidence == "dusuk":
        return True

    if plant in {"belirsiz", "unknown", "tanımlanamadı", "tanımlanamadi", ""}:
        return True

    return False


def identify_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    """Görseli tanır ve yapılandırılmış sonuç döndürür."""

    client = get_groq_client()
    if not client:
        raise RuntimeError("GROQ_API_KEY bulunamadi.")

    prompt = PROMPT_V4

    b64 = base64.b64encode(image_bytes).decode()

    response = vision_completion(
        client,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{b64}"},
                    },
                ],
            }
        ],
        max_tokens=400,
        temperature=0.1,
    )

    raw = response.choices[0].message.content or ""
    parsed = parse_vision_response(raw)

    if is_uncertain(parsed):
        return {
            "identified_name": parsed["plant_tr"],
            "identified_name_en": parsed.get("plant_en"),
            "confidence": parsed["confidence"],
            "description": parsed["note"],
            "matched_products": [],
            "disclaimer": IDENTIFY_DISCLAIMER,
        }

    query = parsed["plant_tr"]
    if parsed["plant_en"]:
        query = f"{query} {parsed['plant_en']}"

    products = search_products(query, limit=3)

    return {
        "identified_name": parsed["plant_tr"],
        "identified_name_en": parsed.get("plant_en"),
        "confidence": parsed["confidence"],
        "description": parsed["note"],
        "matched_products": [
            {"id": p.get("id"), "name": p.get("name"), "category": p.get("category", {}).get("name")}
            for p in products
        ],
        "disclaimer": IDENTIFY_DISCLAIMER,
    }