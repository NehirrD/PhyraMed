"""RAG servis katmanı için model çağrısı yapmadan kabul testi."""

from __future__ import annotations

from ai.rag.service import answer_question, resolve_products
from ai.rag.store import get_product_collection


def assert_contains_any(names: set[str], expected: set[str], label: str) -> None:
    if not names & expected:
        raise AssertionError(
            f"{label}: Beklenen ürünlerden hiçbiri bulunamadı. Gelen: {sorted(names)}"
        )


def main() -> None:
    collection_count = get_product_collection().count()
    if collection_count <= 0:
        raise RuntimeError(
            "RAG indeksi boş. Önce şu komutu çalıştırın: "
            "python -m ai.rag.indexer"
        )

    melatonin = resolve_products(
        "Melatonin hakkında hangi bilgiler bulunuyor?"
    )
    melatonin_names = {p["name"] for p in melatonin.products}
    assert "Melatonin" in melatonin_names
    assert melatonin.strategy == "rag"

    sleep = resolve_products(
        "Gece uykuya dalmakta zorlanıyorum, hangi içerikler ilgili?"
    )
    sleep_names = {p["name"] for p in sleep.products}
    assert_contains_any(
        sleep_names,
        {"Melatonin", "Kediotu", "Çarkıfelek otu"},
        "Uyku sorgusu",
    )

    unrelated = resolve_products("Araba motoru nasıl çalışır?")
    assert unrelated.products == []

    deterministic = answer_question(
        "Melatonin hakkında hangi bilgiler bulunuyor?",
        use_groq=False,
    )
    assert "Melatonin" in deterministic
    assert "Bilimsel kanıt" in deterministic
    assert "Riskler" in deterministic
    assert "Etkileşimler" in deterministic
    assert "Kaynaklar" in deterministic

    unknown = answer_question(
        "Araba motoru nasıl çalışır?",
        use_groq=False,
    )
    assert "genel yapay zekâ bilgisi sunmuyoruz" in unknown

    evidence = answer_question(
        "Kanıt seviyesi ne demek?",
        use_groq=False,
    )
    assert "Güçlü" in evidence
    assert "Orta" in evidence
    assert "Zayıf" in evidence

    print("RAG SERVİS KABUL TESTİ BAŞARILI")
    print("- Chroma kayıt sayısı:", collection_count)
    print("- Açık ürün adı RAG ile bulundu:", sorted(melatonin_names))
    print("- Doğal dilde uyku sorgusu çözüldü:", sorted(sleep_names))
    print("- Alakasız sorgu güvenli biçimde reddedildi.")
    print("- Şablon cevap risk, etkileşim ve kaynakları içeriyor.")
    print("- Kanıt seviyesi açıklaması çalışıyor.")


if __name__ == "__main__":
    main()
