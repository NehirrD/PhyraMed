"""Final kalite düzeltmeleri için çevrimdışı kabul testleri."""

from __future__ import annotations

import sys
import types
from dataclasses import dataclass
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from pydantic import ValidationError


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# Bu test, yalnızca yorum analizi yardımcılarını sınarken API istemcisi
# kurulu olmayan yalın ortamlarda da çalışabilsin.
try:
    import openai  # noqa: F401
except ModuleNotFoundError:
    openai_stub = types.ModuleType("openai")

    class OpenAIError(Exception):
        pass

    class OpenAI:
        def __init__(self, *args, **kwargs):
            pass

    openai_stub.OpenAI = OpenAI
    openai_stub.OpenAIError = OpenAIError
    sys.modules["openai"] = openai_stub


from ai.chat_context import (  # noqa: E402
    looks_like_context_follow_up,
    resolve_history_context,
)
from ai.sentiment import analyze_product_comments  # noqa: E402


def load_comment_schema():
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "schemas"
        / "comment.py"
    )
    spec = spec_from_file_location(
        "phyra_comment_schema",
        schema_path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Yorum şeması yüklenemedi.")

    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.CommentCreate


CommentCreate = load_comment_schema()


@dataclass
class FakeComment:
    text: str
    rating: int


def sample_product(
    name: str,
    product_id: int,
) -> dict:
    return {
        "id": product_id,
        "name": name,
    }


def expect_validation_error(**payload) -> None:
    try:
        CommentCreate(**payload)
    except ValidationError:
        return
    raise AssertionError(
        f"Doğrulama hatası bekleniyordu: {payload}"
    )


def test_comment_validation() -> None:
    valid = CommentCreate(
        user_name="   ",
        text="  Faydalı buldum.  ",
        rating=5,
    )
    assert valid.user_name == "Anonim Kullanıcı"
    assert valid.text == "Faydalı buldum."

    expect_validation_error(
        user_name="Test",
        text="   ",
        rating=5,
    )
    expect_validation_error(
        user_name="Test",
        text="Yorum",
        rating=0,
    )
    expect_validation_error(
        user_name="Test",
        text="Yorum",
        rating=6,
    )
    expect_validation_error(
        user_name="x" * 61,
        text="Yorum",
        rating=5,
    )
    expect_validation_error(
        user_name="Test",
        text="x" * 501,
        rating=5,
    )


def test_comment_analysis() -> None:
    single = analyze_product_comments(
        [
            FakeComment(
                text="Yanıklara iyi geldi.",
                rating=4,
            )
        ]
    )

    distribution = single["sentiment_distribution"]
    assert distribution["positive"]["count"] == 1
    assert distribution["neutral"]["count"] == 0
    assert distribution["negative"]["count"] == 0
    assert single["sample_size_warning"]
    assert single["method"] == "ratings+keyword_rules"
    assert "Duygu dağılımı" in single["summary_text"]

    mixed = analyze_product_comments(
        [
            FakeComment(
                text="İyi geldi.",
                rating=5,
            ),
            FakeComment(
                text="Kararsızım.",
                rating=3,
            ),
            FakeComment(
                text="Baş ağrısı yaptı.",
                rating=1,
            ),
        ]
    )

    mixed_distribution = mixed["sentiment_distribution"]
    assert mixed_distribution["positive"]["count"] == 1
    assert mixed_distribution["neutral"]["count"] == 1
    assert mixed_distribution["negative"]["count"] == 1
    assert mixed["most_reported_side_effect"] == "baş ağrısı"


def test_chat_context() -> None:
    melatonin = sample_product(
        "Melatonin",
        1,
    )
    valerian = sample_product(
        "Kediotu",
        2,
    )

    assert looks_like_context_follow_up(
        "Bu ürünün yan etkileri neler?"
    )
    assert not looks_like_context_follow_up(
        "Ispanak ne için kullanılır?"
    )

    def single_product_resolver(question: str):
        if "melatonin" in question.casefold():
            return [melatonin]
        return []

    resolved = resolve_history_context(
        [
            {
                "role": "user",
                "content": "Melatonin hakkında bilgi ver.",
            },
            {
                "role": "assistant",
                "content": "Melatonin bilgisi gösterildi.",
            },
        ],
        single_product_resolver,
    )

    assert resolved.products == [melatonin]
    assert not resolved.ambiguous_product_names

    def ambiguous_resolver(question: str):
        if "uyku" in question.casefold():
            return [melatonin, valerian]
        return []

    ambiguous = resolve_history_context(
        [
            {
                "role": "user",
                "content": "Uyku için hangi ürünler var?",
            }
        ],
        ambiguous_resolver,
    )

    assert not ambiguous.products
    assert ambiguous.ambiguous_product_names == [
        "Melatonin",
        "Kediotu",
    ]


def test_static_integration() -> None:
    root = Path(__file__).resolve().parents[1]

    search_router = (
        root / "routers" / "search.py"
    ).read_text(encoding="utf-8")
    product_router = (
        root / "routers" / "product.py"
    ).read_text(encoding="utf-8")
    service = (
        root / "ai" / "rag" / "service.py"
    ).read_text(encoding="utf-8")
    index_html = (
        root / "index.html"
    ).read_text(encoding="utf-8")
    product_page = (
        root / "pages" / "urun.html"
    ).read_text(encoding="utf-8")
    main_js = (
        root / "js" / "main.js"
    ).read_text(encoding="utf-8")

    assert "search_count +=" not in search_router
    assert "/{product_id}/search-selection" in product_router
    assert "resolve_history_context" in service
    assert "data-product-id" in index_html
    assert "/search-selection" in index_html
    assert "Yorum Analizi" in product_page
    assert "sample_size_warning" in product_page
    assert "Promise.all([" in product_page
    assert "conversationHistory" in main_js
    assert "history: historyPayload" in main_js


def main() -> None:
    test_comment_validation()
    test_comment_analysis()
    test_chat_context()
    test_static_integration()

    print("FINAL KALİTE ÇEVRİMDIŞI KABUL TESTİ BAŞARILI")
    print("- Chatbot tek ürünlü önceki konuşma bağlamını güvenli biçimde hatırlıyor.")
    print("- Birden fazla ürün geçen bağlamda rastgele ürün seçilmiyor.")
    print("- Katalog dışı açık ürün sorusu önceki bağlama yanlış bağlanmıyor.")
    print("- Yorum puanı 1-5, ad 60 ve yorum 500 karakterle sınırlandı.")
    print("- Boş yorum ve geçersiz puanlar Pydantic tarafından reddediliyor.")
    print("- Yorum dağılımı yıldız puanlarından, yan etkiler metinden çıkarılıyor.")
    print("- Tek yorumlu analizde örneklem uyarısı üretiliyor.")
    print("- Arama yazarken sayaç artmıyor; yalnızca ürün seçimi sayılıyor.")
    print("- Yorum gönderiminden sonra liste ve analiz birlikte yenileniyor.")


if __name__ == "__main__":
    main()
