# Sprint 2/3 — Chatbot (RAG + Hafıza)

## Mimari (Sprint 3 — RAG uygulandı)

```text
Kullanıcı sorusu + session_id
        ↓
Oturum hafızası (son 8 tur)
        ↓
Hibrit retrieval (ChromaDB + keyword)
        ↓
Ürün bulundu mu?
     ├── Evet → Kaynak: verified_db
     └── Hayır → Kaynak: ai_generated
        ↓
Groq / şablon yanıt + disclaimer
        ↓
Yapılandırılmış JSON yanıt
```

Detaylı mimari: [`07-rag-orchestration.md`](07-rag-orchestration.md)

## Ürün veritabanı

`poc/data/products_db.json` — 5 ürün: Melatonin, Magnezyum, Zencefil, Nane, Zerdeçal.

Backend hazır olduğunda `product_db.py` içindeki `load_products()` REST API çağrısına çevrilecek.

## Kullanım

```powershell
# İndeks oluştur (ilk çalıştırmada)
python poc/rag/indexer.py

# Tek soru — JSON çıktı
python poc/chatbot.py --groq --json --question "Zencefil mide bulantısına iyi gelir mi?"

# İnteraktif çok turlu oturum
python poc/chatbot.py --groq

# Şablon modu (Groq key gerekmez)
python poc/chatbot.py --question "Uyku için ne var?"
```

## Test soruları

| Soru | Beklenen sonuç |
|------|----------------|
| "Zencefil mide bulantısına iyi gelir mi?" | Zencefil (**Kaynak: verified_db**) |
| "Uyku için ne var?" | Melatonin (**Kaynak: verified_db**) |
| "Kas krampları için ne önerirsiniz?" | Magnezyum (**Kaynak: verified_db**) |
| "Ashwagandha ne işe yarar?" | Ürün bulunamaz (**Kaynak: ai_generated**) |

## Backend entegrasyonu

- Endpoint: `POST /api/chat`
- Body: `{ "question": "...", "session_id": null, "use_groq": true }`
- Yanıt:

```json
{
  "answer": "...",
  "source": "verified_db",
  "sources": [{ "id": 3, "name": "Zencefil" }],
  "retrieved_chunks": [
    {
      "chunk_id": "3:evidence_summary",
      "product_id": 3,
      "product_name": "Zencefil",
      "field": "evidence_summary",
      "score": 0.92,
      "source": "semantic"
    }
  ],
  "session_id": "uuid"
}
```

## REST API başlatma

```powershell
uvicorn api.main:app --reload --app-dir .
```
