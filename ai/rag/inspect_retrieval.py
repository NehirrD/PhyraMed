"""Güvenli RAG ürün seçimini gözlemleme ve kabul testi."""

from __future__ import annotations

from ai.rag.retriever import retrieve_products


TEST_CASES = (
    {
        "query": "Melatonin hakkında hangi bilgiler bulunuyor?",
        "expected_any": {"Melatonin"},
        "must_be_empty": False,
        "forbidden": set(),
    },
    {
        "query": "Gece uykuya dalmakta zorlanıyorum, hangi içerikler ilgili?",
        "expected_any": {"Çarkıfelek otu", "Kediotu", "Melatonin"},
        "must_be_empty": False,
        "forbidden": set(),
    },
    {
        "query": "Stres ve zihinsel rahatlama konusunda hangi ürünleri inceleyebilirim?",
        "expected_any": {"Ashwagandha", "Çarkıfelek otu"},
        "must_be_empty": False,
        "forbidden": {"Aloe vera"},
    },
    {
        "query": "Mide ve bağırsak sağlığıyla ilgili hangi ürünler var?",
        "expected_any": set(),
        "must_be_empty": False,
        "forbidden": set(),
    },
    {
        "query": "Araba motoru nasıl çalışır?",
        "expected_any": set(),
        "must_be_empty": True,
        "forbidden": set(),
    },
    {
        "query": "Python kodu için güvenli kaynak var mı?",
        "expected_any": set(),
        "must_be_empty": True,
        "forbidden": set(),
    },
    {
        "query": "Yeni telefon ürünleri hakkında hangi içerikler var?",
        "expected_any": set(),
        "must_be_empty": True,
        "forbidden": set(),
    },
)


def main() -> None:
    failures: list[str] = []

    for case in TEST_CASES:
        query = case["query"]
        expected_names = case["expected_any"]
        must_be_empty = case["must_be_empty"]
        forbidden_names = case["forbidden"]

        print("\n" + "=" * 72)
        print("SORU:", query)

        products = retrieve_products(query, max_products=3)

        if not products:
            print("GÜVENLİ SONUÇ: Eşleşme bulunamadı.")
        else:
            for order, product in enumerate(products, start=1):
                chunk_types = sorted(
                    {
                        chunk["metadata"].get("chunk_type", "unknown")
                        for chunk in product["chunks"]
                    }
                )
                print(
                    f"{order}. {product['product_name']} | "
                    f"puan={product['score']:.3f} | "
                    f"semantik={product['semantic_similarity']:.3f} | "
                    f"kelime={product['lexical_overlap']} | "
                    f"neden={product['retrieval_reason']} | "
                    f"parçalar={','.join(chunk_types)}"
                )

        names = {product["product_name"] for product in products}

        if must_be_empty and products:
            failures.append(
                f"Alakasız sorgu ürün döndürdü: {query} -> {sorted(names)}"
            )

        if not must_be_empty and not products:
            failures.append(f"Alanla ilgili sorgu boş döndü: {query}")

        if expected_names and not (names & expected_names):
            failures.append(
                f"Beklenen ilgili ürün bulunamadı: {query} -> {sorted(names)}"
            )

        unexpected = names & forbidden_names
        if unexpected:
            failures.append(
                f"Zayıf/alakasız ürün kabul edildi: {query} -> {sorted(unexpected)}"
            )

    print("\n" + "=" * 72)
    if failures:
        print("KABUL TESTİ BAŞARISIZ")
        for failure in failures:
            print("-", failure)
        raise SystemExit(1)

    print("KABUL TESTİ BAŞARILI")
    print("- Açık ürün adı doğru ürünü buldu.")
    print("- Uyku ve stres sorguları ilgili ürünleri buldu.")
    print("- Stres sorgusunda zayıf üçüncü sonuç elendi.")
    print("- Teknoloji ve alışveriş sorguları hiçbir ürün döndürmedi.")


if __name__ == "__main__":
    main()
