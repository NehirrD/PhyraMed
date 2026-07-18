# Sprint 2 — Chatbot Temel Sürüm

## Mimari (Sprint 1 kararı uygulandı)

```
Kullanıcı sorusu
      ↓
Anahtar kelime arama (product_db.py)
      ↓
İlgili ürün(ler) bağlam olarak seçilir
      ↓
Prompt tabanlı yanıt (Groq veya şablon)
      ↓
Bilgilendirme + disclaimer
```

**RAG yok** — MVP için mock JSON ürün DB yeterli. Ürün sayısı arttığında RAG'e geçiş planlandı.

## Ürün veritabanı

`poc/data/products_db.json` — 5 örnek ürün (zencefil, spirulina, melisa, zerdeçal, nane).

Backend hazır olduğunda `product_db.py` içindeki `load_products()` fonksiyonu REST API çağrısına çevrilecek:

```python
# Gelecek: GET /api/products?search=...
```

## Kullanım

```powershell
# İnteraktif (key gerekmez — şablon yanıt)
python poc/chatbot.py

# Tek soru
python poc/chatbot.py --question "Zencefil mide bulantısına iyi gelir mi?"

# Groq ile doğal dil
python poc/chatbot.py --groq --question "Demir eksikliği için ne önerirsiniz?"
```

## Test soruları

| Soru | Beklenen ürün |
|------|---------------|
| "Zencefil mide bulantısına iyi gelir mi?" | Zencefil Kapsül |
| "Uyku için ne var?" | Melisa Uyku Damlası |
| "Demir eksikliği takviyesi" | Spirulina Demir Destek |

## Backend entegrasyonu (öneri)

- Endpoint: `POST /api/chat`
- Body: `{ "question": "..." }`
- AI modülü `search_products` + `groq_answer` pipeline'ını çalıştırır
- Yanıt: `{ "answer": "...", "sources": [{"id": 1, "name": "..."}] }`
