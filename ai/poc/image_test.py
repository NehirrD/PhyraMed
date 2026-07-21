"""
Sprint 1 — görsel tanıma POC (Groq vision).

    python image_test.py sample/bitki.jpg
"""

import base64
import sys
from pathlib import Path

from dotenv import load_dotenv

from groq_client import extract_model_text, get_groq_client, vision_completion

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp", ".gif": "image/gif"}


def resolve_image(path_str: str) -> Path:
    candidates = [
        Path(path_str),
        Path(__file__).parent / path_str,
        Path(__file__).parent / "sample" / Path(path_str).name,
    ]
    for p in candidates:
        if p.exists():
            return p.resolve()

    sample_dir = Path(__file__).parent / "sample"
    samples = sorted(sample_dir.glob("*.*"))
    print(f"Dosya bulunamadı: {path_str}")
    if samples:
        print(f"\npoc/sample/ içindeki dosyalar: {', '.join(f.name for f in samples)}")
    else:
        print("\npoc/sample/ klasörü boş. Bir bitki fotoğrafı ekle (ör. ginger.jpg).")
    sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Kullanım: python poc/image_test.py poc/sample/ginger.jpg")
        sys.exit(1)

    client = get_groq_client()
    if not client:
        print("GROQ_API_KEY yok. ai/.env dosyasına key ekle.")
        sys.exit(1)

    img = resolve_image(sys.argv[1])

    mime = MIME.get(img.suffix.lower(), "image/jpeg")
    b64 = base64.b64encode(img.read_bytes()).decode()

    r = vision_completion(
        client,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Bu görseldeki bitkiyi Türkçe tanımla (isim + kısa bilgi)."},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
            ],
        }],
        max_tokens=400,
    )
    print(extract_model_text(r.choices[0].message.content or ""))


if __name__ == "__main__":
    main()
