"""
Sprint 1/3 — gorsel tanima POC (Groq vision + urun eslestirme).

    python image_test.py sample/ginger.jpg
    python image_test.py sample/turmeric.jpg --json
"""

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from vision import identify_and_lookup

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


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
    print(f"Dosya bulunamadi: {path_str}")
    if samples:
        print(f"\npoc/sample/ icindeki dosyalar: {', '.join(f.name for f in samples)}")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Gorsel dosya yolu")
    parser.add_argument("--json", action="store_true", help="JSON cikti")
    parser.add_argument("--prompt", choices=["v1", "v2", "v3"], default="v3")
    args = parser.parse_args()

    img = resolve_image(args.image)

    try:
        result = identify_and_lookup(img, prompt_version=args.prompt)
    except RuntimeError as exc:
        print(exc)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if result["status"] == "uncertain":
        print(result["message"])
        print(f"\nGuven: {result['confidence']}")
        print(f"Not: {result['note']}")
        return

    print(f"Bitki (TR): {result['plant_tr']}")
    print(f"Bitki (EN): {result['plant_en']}")
    print(f"Guven: {result['confidence']}")
    print(f"Not: {result['note']}")

    if result["products"]:
        print("\nEslesen urunler:")
        for p in result["products"]:
            print(f"  - [{p['id']}] {p['name']} ({p['category']})")
    else:
        print("\nUrun veritabaninda eslesme bulunamadi.")


if __name__ == "__main__":
    main()
