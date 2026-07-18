"""
Sprint 2 — görsel tanıma doğruluk ölçümü.

Gerçek veri setindeki etiketli fotoğrafları Groq vision ile test eder;
tam/kısmi eşleşme ve genel doğruluk oranını raporlar.

    python poc/image_eval.py
    python poc/image_eval.py --prompt-v2
"""

import argparse
import base64
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from groq_client import (
    VISION_MODEL,
    extract_model_text,
    get_groq_client,
    vision_completion,
)

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

SAMPLE_DIR = Path(__file__).parent / "sample"
DATASET_PATH = Path(__file__).parent / "dataset" / "image_labels.json"
REPORT_DIR = Path(__file__).parent / "reports"

MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
}

PROMPT_V1 = (
    "Bu görseldeki bitkiyi tanımla. Yanıtında bitkinin Türkçe adını açıkça yaz."
)

PROMPT_V2 = (
    "Sen bir botanik tanıma asistanısın.\n"
    "Görseldeki bitkiyi tanımla.\n"
    "Yanıtı TAM olarak aşağıdaki formatta ver:\n\n"
    "Bitki (TR): <Türkçe adı>\n"
    "Bitki (EN): <İngilizce adı>\n"
    "Güven: <yüksek/orta/düşük>\n"
    "Kısa not: <1 cümle>"
)


def load_dataset():
    return json.loads(DATASET_PATH.read_text(encoding="utf-8"))


def normalize(text: str):
    text = text.lower()
    text = (
        text.replace("ç", "c")
        .replace("ğ", "g")
        .replace("ı", "i")
        .replace("ö", "o")
        .replace("ş", "s")
        .replace("ü", "u")
    )
    return re.sub(r"[^a-z0-9\s]", " ", text).strip()


def primary_label(response: str):
    """
    Model cevabından sadece Bitki(TR) bilgisini çıkar.
    """

    clean = extract_model_text(response)

    patterns = [
        r"Bitki\s*\(\s*TR\s*\)\s*:\s*(.+)",
        r"Bitki\s*:\s*(.+)",
    ]

    for pattern in patterns:
        m = re.search(pattern, clean, re.IGNORECASE)
        if m:
            return m.group(1).split("\n")[0].strip()

    return clean.strip()


def classify_prediction(response: str, item: dict):
    """
    exact:
        Bitki(TR) == beklenen

    partial:
        Bitki cevabın başka kısmında geçiyor.

    miss:
        Hiç bulunamadı.
    """

    expected = normalize(item["expected_tr"])
    aliases = [normalize(a) for a in item["aliases"]]

    predicted = normalize(primary_label(response))

    # EXACT
    if predicted == expected:
        return "exact"

    if predicted in aliases:
        return "exact"

    # PARTIAL
    full = normalize(extract_model_text(response))

    for alias in aliases:
        if alias in full:
            return "partial"

    return "miss"


def predict(client, image_path: Path, prompt: str):
    mime = MIME.get(image_path.suffix.lower(), "image/jpeg")
    b64 = base64.b64encode(image_path.read_bytes()).decode()

    r = vision_completion(
        client,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime};base64,{b64}"
                        },
                    },
                ],
            }
        ],
        max_tokens=400,
        temperature=0.1,
    )

    return r.choices[0].message.content or ""


def run_evaluation(use_v2=False):

    client = get_groq_client()

    if not client:
        print("GROQ_API_KEY bulunamadı.")
        sys.exit(1)

    prompt = PROMPT_V2 if use_v2 else PROMPT_V1

    dataset = load_dataset()

    results = []

    print("=== Görsel Tanıma Değerlendirmesi (Sprint 2) ===")
    print(f"Model: {VISION_MODEL}")
    print(f"Prompt: {'v2' if use_v2 else 'v1'}")
    print(f"Veri seti: {len(dataset)} görsel\n")

    for item in dataset:

        img = SAMPLE_DIR / item["file"]

        if not img.exists():
            print(item["file"], "bulunamadı")
            continue

        print(f"  Analiz: {item['file']} (beklenen: {item['expected_tr']})...")

        try:

            response = predict(client, img, prompt)

            prediction = extract_model_text(response)

            match = classify_prediction(response, item)

        except Exception as e:

            prediction = str(e)

            match = "error"

        results.append(
            {
                "file": item["file"],
                "expected": item["expected_tr"],
                "prediction": prediction,
                "match": match,
            }
        )

        icon = {
            "exact": "✓",
            "partial": "~",
            "miss": "✗",
            "error": "!",
        }.get(match, "?")

        print(f"    [{icon} {match}] {prediction[:300].replace(chr(10),' ')}")

    total = len(results)

    exact = sum(r["match"] == "exact" for r in results)
    partial = sum(r["match"] == "partial" for r in results)
    miss = sum(r["match"] == "miss" for r in results)
    error = sum(r["match"] == "error" for r in results)

    strict = exact / total if total else 0
    lenient = (exact + partial) / total if total else 0

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": VISION_MODEL,
        "dataset_size": total,
        "metrics": {
            "exact_matches": exact,
            "partial_matches": partial,
            "misses": miss,
            "errors": error,
            "strict_accuracy": round(strict, 3),
            "lenient_accuracy": round(lenient, 3),
        },
        "results": results,
    }

    REPORT_DIR.mkdir(exist_ok=True)

    report_file = REPORT_DIR / f"image_eval_{'v2' if use_v2 else 'v1'}.json"

    report_file.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\n--- Metrikler ---")
    print(f"Tam eşleşme:    {exact}/{total} ({strict:.0%})")
    print(f"Kısmi eşleşme:  {partial}/{total}")
    print(f"Kaçan:          {miss}/{total}")

    if error:
        print(f"Hata:           {error}/{total}")

    print(f"Esnek doğruluk: {lenient:.0%}")

    print("\nRapor:", report_file)

    return report


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--prompt-v2",
        action="store_true",
        help="Yeni prompt kullan",
    )

    args = parser.parse_args()

    run_evaluation(args.prompt_v2)


if __name__ == "__main__":
    main()