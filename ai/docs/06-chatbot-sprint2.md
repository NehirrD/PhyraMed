# Sprint 2 — Chatbot Temel Sürüm

## Mimari (Sprint 1 kararı uygulandı)

```text
Kullanıcı sorusu
      ↓
Anahtar kelime arama (product_db.py)
      ↓
Ürün bulundu mu?
     ├── Evet
     │      ↓
     │  İlgili ürün(ler) prompt'a eklenir
     │      ↓
     │  Groq doğal dil cevabı üretir
     │      ↓
     │  Kaynak: Onaylanmış Bilgi
     │
     └── Hayır
            ↓
      Groq genel bilgisini kullanır
            ↓
      Kaynak: AI Yanıtı
            ↓
Bilgilendirme + disclaimer
```

**RAG yok** — MVP için mock JSON ürün veritabanı yeterlidir. Ürün sayısı arttığında, daha kapsamlı bir ürün veritabanına veya internet tabanlı bilgi kaynağına geçildiğinde RAG mimarisine geçilmesi planlanmaktadır.

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

| Soru | Beklenen sonuç |
|------|----------------|
| "Zencefil mide bulantısına iyi gelir mi?" | Zencefil Kapsül (**Kaynak: Onaylanmış Bilgi**) |
| "Uyku için ne var?" | Melisa Uyku Damlası (**Kaynak: Onaylanmış Bilgi**) |
| "Demir eksikliği takviyesi" | Spirulina Demir Destek (**Kaynak: Onaylanmış Bilgi**) |
| "Ashwagandha ne işe yarar?" | Ürün bulunamazsa Groq genel bilgisi (**Kaynak: AI Yanıtı**) |

## Backend entegrasyonu (öneri)

- Endpoint: `POST /api/chat`
- Body: `{ "question": "..." }`
- AI modülü önce `search_products` ile ürün veritabanında arama yapar.
- Ürün bulunursa doğrulanmış ürün bilgileri kullanılarak cevap oluşturulur.
- Ürün bulunamazsa Groq modelinin genel bilgisinden yararlanılarak cevap oluşturulur.
- Yanıt örneği:

```json
{
  "answer": "...",
  "source": "verified_db",
  "sources": [
    {
      "id": 1,
      "name": "Zencefil Kapsül"
    }
  ]
}
```

veya

```json
{
  "answer": "...",
  "source": "ai_generated",
  "sources": []
}
```