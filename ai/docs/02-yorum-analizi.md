# Görev 2 — Yorum Analizi Araştırması

Kullanıcı yorumlarından **sentiment** (olumlu/olumsuz) ve **kısa özet** çıkarılacak.

## Yaklaşım seçenekleri

| Yaklaşım | Zorluk | Sprint 1 |
|----------|--------|----------|
| **Kelime listesi (basit)** | Çok kolay | ✅ İlk test için yeterli |
| Groq `llama-3.3-70b-versatile` | Kolay | ✅ Key varsa daha iyi sonuç + özet |
| Hugging Face BERT (yerel) | Zor | ❌ 500MB indirme, kurulum ağır |

## Sprint 1 önerisi

1. Önce `sentiment_test.py` ile basit test (key gerekmez)
2. Key varsa `--groq` ile karşılaştır

```powershell
python poc/sentiment_test.py
python poc/sentiment_test.py --groq
```

## İlk test sonuçları

*=== Basit kelime yöntemi (Sprint 1) ===

1. [Olumlu] Bu zencefil kapsül gerçekten mide bulantıma iyi geldi, 2 haftadır kull
2. [Olumsuz] Hiçbir faydasını görmedim, para boşa gitti.
3. [Olumsuz] Kargo hızlıydı ama ürün kokusu biraz garip geldi bana.
4. [Olumlu] Doktorum onayladı, demir eksikliğim için harika bir alternatif.
5. [Olumsuz] Yan etki olarak baş ağrısı yaptı, bıraktım.
6. [Olumlu] Fiyat/performans olarak çok iyi, tekrar alacağım.
7. [Olumsuz] Kullanım talimatı yetersiz, nasıl dozajlayacağımı anlamadım.
8. [Olumlu] Arkadaşım önerdi, uyku kalitem gerçekten arttı.
9. [Olumsuz] Alerjik reaksiyon yaptı, dikkatli olun.
10. [Nötr] Bilimsel kanıt seviyesi düşük ama geleneksel kullanımda etkili oldu ba

Özet: Olumlu 4, Olumsuz 5, Nötr 1

- Olumlu: __ / 10
- Olumsuz: __ / 10
- En sık geçen konular: ___

