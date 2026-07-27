"""Görsel tanıma — poc/image_eval.py'deki PROMPT_V2 formatına göre (Sprint 2, %80 strict accuracy)."""

import base64
import re

from ai.groq_client import get_groq_client, vision_completion, extract_model_text
from ai.product_db import search_products

IDENTIFY_DISCLAIMER = (
    "Bu tanımlama yapay zeka tahminidir, kesin doğruluk garanti edilmez; "
    "tıbbi tavsiye değildir. Emin olmak için bir uzmana danışın."
)

# poc/image_eval.py PROMPT_V2 ile birebir aynı — %80 strict accuracy ile test edilmiş.
IDENTIFY_PROMPT = (
    "Sen bir botanik tanıma asistanısın.\n"
    "Görseldeki bitkiyi tanımla.\n"
    "Yanıtı TAM olarak aşağıdaki formatta ver:\n\n"
    "Bitki (TR): <Türkçe adı>\n"
    "Bitki (EN): <İngilizce adı>\n"
    "Güven: <yüksek/orta/düşük>\n"
    "Kısa not: <1 cümle>"
)


def _parse_response(text: str) -> dict:
    """poc/image_eval.py'deki primary_label() mantığıyla aynı parsing."""
    clean = extract_model_text(text)

    name_tr = None
    for pattern in [r"Bitki\s*\(\s*TR\s*\)\s*:\s*(.+)", r"Bitki\s*:\s*(.+)"]:
        m = re.search(pattern, clean, re.IGNORECASE)
        if m:
            name_tr = m.group(1).split("\n")[0].strip()
            break

    name_en_match = re.search(r"Bitki\s*\(\s*EN\s*\)\s*:\s*(.+)", clean, re.IGNORECASE)
    name_en = name_en_match.group(1).split("\n")[0].strip() if name_en_match else None

    confidence_match = re.search(r"Güven\s*:\s*(.+)", clean, re.IGNORECASE)
    confidence = confidence_match.group(1).split("\n")[0].strip() if confidence_match else "belirtilmemiş"

    note_match = re.search(r"Kısa not\s*:\s*(.+)", clean, re.IGNORECASE | re.DOTALL)
    note = note_match.group(1).strip() if note_match else clean.strip()

    return {
        "name_tr": name_tr or "Belirlenemedi",
        "name_en": name_en,
        "confidence": confidence,
        "note": note,
    }


def identify_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    client = get_groq_client()
    if not client:
        return {
            "identified_name": "Belirlenemedi",
            "confidence": "belirtilmemiş",
            "description": "AI servisi şu anda kullanılamıyor (API anahtarı eksik).",
            "matched_products": [],
        }

    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{b64_image}"

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": IDENTIFY_PROMPT},
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        }
    ]

    try:
        response = vision_completion(client, messages, max_tokens=400, temperature=0.1)
        raw_text = response.choices[0].message.content or ""
    except Exception as e:
        return {
            "identified_name": "Belirlenemedi",
            "confidence": "belirtilmemiş",
            "description": f"Görsel analiz sırasında hata oluştu: {e}",
            "matched_products": [],
        }

    parsed = _parse_response(raw_text)

    matched_products = []
    if parsed["name_tr"] != "Belirlenemedi":
        matched_products = search_products(parsed["name_tr"], limit=3)
        if not matched_products and parsed["name_en"]:
            matched_products = search_products(parsed["name_en"], limit=3)

    return {
        "identified_name": parsed["name_tr"],
        "identified_name_en": parsed["name_en"],
        "confidence": parsed["confidence"],
        "description": parsed["note"],
        "matched_products": matched_products,
    }