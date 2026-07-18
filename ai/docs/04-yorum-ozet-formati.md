# Sprint 2 — Yorum Analizi Özet Formatı

Backend ve frontend'in tüketeceği standart JSON formatı.

## Örnek çıktı

```json
{
  "sentiment_distribution": {
    "positive": { "count": 4, "ratio": 0.4 },
    "negative": { "count": 5, "ratio": 0.5 },
    "neutral": { "count": 1, "ratio": 0.1 },
    "total_comments": 10
  },
  "most_reported_side_effect": "baş ağrısı",
  "side_effects": [
    { "effect": "baş ağrısı", "count": 1 },
    { "effect": "alerjik reaksiyon", "count": 1 }
  ],
  "summary_text": "10 yorum analiz edildi. Olumlu/olumsuz oranı: %40 olumlu, %50 olumsuz. En sık bildirilen yan etki: baş ağrısı.",
  "method": "keyword_rules"
}
```

## Alan açıklamaları

| Alan | Tip | Açıklama |
|------|-----|----------|
| `sentiment_distribution` | object | Olumlu/olumsuz/nötr sayı ve oran |
| `most_reported_side_effect` | string \| null | En sık geçen yan etki |
| `side_effects` | array | Yan etki + tekrar sayısı |
| `summary_text` | string | UI'da gösterilecek kısa özet cümlesi |
| `method` | string | `keyword_rules` veya `keyword_rules+groq` |

## Üretim

```powershell
python poc/sentiment_summary.py
python poc/sentiment_summary.py --groq
```

Rapor: `poc/reports/sentiment_summary.json`

## Backend entegrasyonu (öneri)

- Endpoint: `GET /api/products/{id}/review-summary`
- AI modülü periyodik veya yorum eklendiğinde bu JSON'u üretir
- Frontend rozetlerde `ratio` değerlerini, kartta `summary_text` ve `most_reported_side_effect` kullanır
