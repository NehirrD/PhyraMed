"""PhyraMed /chat/ endpoint acceptance test.

Uses only the Python standard library and decodes the HTTP response explicitly as
UTF-8 so Windows PowerShell 5.1 cannot corrupt Turkish characters.
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

CHAT_URL = "http://127.0.0.1:8000/chat/"
TIMEOUT_SECONDS = 45
MOJIBAKE_MARKERS = ("Ã", "Ä", "Å", "Â")


@dataclass(frozen=True)
class ChatTest:
    name: str
    message: str
    required: tuple[str, ...] = ()
    any_of: tuple[str, ...] = ()
    history: tuple[dict[str, str], ...] = ()


def contains_casefold(text: str, expected: str) -> bool:
    return expected.casefold() in text.casefold()


def require_all(answer: str, required: Iterable[str], test_name: str) -> None:
    missing = [item for item in required if not contains_casefold(answer, item)]
    if missing:
        raise AssertionError(
            f"{test_name}: cevapta beklenen ifadeler eksik: {missing}"
        )


def require_any(answer: str, options: Iterable[str], test_name: str) -> None:
    options = tuple(options)
    if options and not any(contains_casefold(answer, item) for item in options):
        raise AssertionError(
            f"{test_name}: beklenen seçeneklerden hiçbiri bulunamadı: {options}"
        )


def post_chat(
    message: str,
    history: tuple[dict[str, str], ...] = (),
) -> tuple[str, float]:
    payload = json.dumps(
        {
            "message": message,
            "history": list(history),
        },
        ensure_ascii=False,
    ).encode("utf-8")
    request = Request(
        CHAT_URL,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
        },
    )

    started = time.perf_counter()
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            raw = response.read()
            status = response.status
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {error.code}: {body}") from error
    except URLError as error:
        raise RuntimeError(
            "Backend'e ulaşılamadı. Uvicorn'un 127.0.0.1:8000 adresinde "
            "çalıştığını kontrol edin."
        ) from error

    elapsed = time.perf_counter() - started
    if status != 200:
        raise RuntimeError(f"Beklenmeyen HTTP durumu: {status}")

    decoded = raw.decode("utf-8")
    data = json.loads(decoded)
    answer = str(data.get("response") or "").strip()
    if not answer:
        raise AssertionError("API boş cevap döndürdü.")
    return answer, elapsed


def main() -> None:
    tests = (
        ChatTest(
            name="Açık ürün adı",
            message="Melatonin hakkında hangi bilgiler bulunuyor?",
            required=("Melatonin", "Kaynaklar", "UYARI"),
        ),
        ChatTest(
            name="Doğal dilde uyku sorgusu",
            message="Gece uykuya dalmakta zorlanıyorum, hangi içerikler ilgili?",
            required=("Kaynaklar", "UYARI"),
            any_of=("Kediotu", "Çarkıfelek otu", "Magnezyum"),
        ),
        ChatTest(
            name="Konuşma bağlamı",
            message="Bu ürünün yan etkileri neler?",
            history=(
                {
                    "role": "user",
                    "content": "Melatonin hakkında hangi bilgiler bulunuyor?",
                },
                {
                    "role": "assistant",
                    "content": "Melatonin için kaynaklandırılmış bilgiler gösterildi.",
                },
            ),
            required=("Melatonin", "UYARI"),
            any_of=("baş ağrısı", "baş dönmesi", "bulantı", "uyku hali"),
        ),
        ChatTest(
            name="Kanıt seviyesi açıklaması",
            message="Kanıt seviyesi ne demek?",
            required=("kanıt seviyesi", "Değerlendiriliyor", "UYARI"),
        ),
        ChatTest(
            name="Alakasız sorgu güvenliği",
            message="Araba motoru nasıl çalışır?",
            required=(
                "yeterli düzeyde eşleşen",
                "genel yapay zekâ bilgisi sunmuyoruz",
                "UYARI",
            ),
        ),
    )

    for test in tests:
        print("\n" + "=" * 72)
        print(f"TEST: {test.name}")
        print(f"SORU: {test.message}")
        answer, elapsed = post_chat(
            test.message,
            history=test.history,
        )

        require_all(answer, test.required, test.name)
        require_any(answer, test.any_of, test.name)

        bad_markers = [marker for marker in MOJIBAKE_MARKERS if marker in answer]
        if bad_markers:
            raise AssertionError(
                f"{test.name}: UTF-8 bozulma işaretleri bulundu: {bad_markers}"
            )

        print(f"SÜRE: {elapsed:.2f} saniye")
        print("CEVAP:")
        print(answer)
        print("SONUÇ: BAŞARILI")

    print("\n" + "=" * 72)
    print("TÜM CHAT API TESTLERİ BAŞARILI")
    print("Türkçe karakterler UTF-8 olarak doğru çözüldü.")


if __name__ == "__main__":
    main()
