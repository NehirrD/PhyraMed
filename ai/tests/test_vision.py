"""Vision parse testleri."""

import sys
from pathlib import Path

POC_DIR = Path(__file__).resolve().parents[1] / "poc"
sys.path.insert(0, str(POC_DIR))

from vision import is_uncertain, parse_vision_response, PROMPT_V4


def test_parse_v2_response():
    raw = (
        "Bitki (TR): Zencefil\n"
        "Bitki (EN): Ginger\n"
        "Guven: yuksek\n"
        "Kisa not: Rizom yapisi tipik."
    )
    parsed = parse_vision_response(raw)
    assert "zencefil" in parsed["plant_tr"].lower()
    assert parsed["confidence"] == "yuksek"


def test_parse_v4_response():
    """V4 prompt formatı parse testi."""
    raw = (
        "Bitki (TR): Zerdeçal\n"
        "Bitki (EN): Turmeric\n"
        "Güven: yüksek\n"
        "Kısa not: Turuncu-sarı rizom kesiti, kurkumin pigmenti belirgin."
    )
    parsed = parse_vision_response(raw)
    assert "zerdeçal" in parsed["plant_tr"].lower() or "turmeric" in parsed["plant_en"].lower()
    assert parsed["confidence"] == "yüksek"


def test_uncertain_low_confidence():
    parsed = {"plant_tr": "Zencefil", "confidence": "dusuk"}
    assert is_uncertain(parsed) is True


def test_uncertain_belirsiz_plant():
    parsed = {"plant_tr": "Belirsiz", "confidence": "orta"}
    assert is_uncertain(parsed) is True


def test_confident_result():
    parsed = {"plant_tr": "Nane", "confidence": "yuksek"}
    assert is_uncertain(parsed) is False


def test_prompt_v4_exists():
    """V4 prompt'un tanımlı olduğunu test eder."""
    assert PROMPT_V4 is not None
    assert "ZERDEÇAL" in PROMPT_V4
    assert "ZENCEFİL" in PROMPT_V4
    assert "kritik" in PROMPT_V4.lower()


def test_parse_handles_uncertain_response():
    """Belirsiz yanıt parsing testi."""
    raw = (
        "Bitki (TR): Belirsiz\n"
        "Bitki (EN): Unknown\n"
        "Güven: düşük\n"
        "Kısa not: Işık yetersiz, tanı yapılamaz."
    )
    parsed = parse_vision_response(raw)
    assert parsed["plant_tr"] == "Belirsiz"
    assert parsed["confidence"] == "düşük"
    assert is_uncertain(parsed) is True
