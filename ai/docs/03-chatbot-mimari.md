# Görev 3 — Chatbot Mimari Kararı

PhyraMed chatbot'u bitkisel ürünler hakkında **bilgilendirme** yapacak (tıbbi tavsiye değil).

## İki seçenek

### A) Basit prompt tabanlı (Sprint 1–2)
- System prompt + ürün bilgisi metne eklenir.
- Anahtar kelime araması ile ürün bulunur.

### B) RAG (Sprint 3 — uygulandı)
- Ürün alanları chunk'lara ayrılır, ChromaDB'ye indekslenir.
- Hibrit retrieval: semantik + keyword.
- Oturum hafızası ile çok turlu konuşma.
- Orkestrasyon katmanı kaynak seçimi ve yanıt üretimini yönetir.

## Sprint 3 kararı

| | Seçim |
|---|-------|
| **Retrieval** | ChromaDB + keyword hibrit |
| **Hafıza** | In-memory session store (session_id) |
| **Orkestrasyon** | `orchestrator.py` — retrieve → generate |
| **API** | FastAPI `POST /api/chat` |

Detay: [`07-rag-orchestration.md`](07-rag-orchestration.md)

## Akış

```text
Kullanıcı sorusu
      ↓
Session memory (önceki turlar)
      ↓
Hibrit RAG retrieval
      ↓
Ürün bulundu mu?
     ├── Evet → Kaynak: Onaylanmış Bilgi (verified_db)
     └── Hayır → Kaynak: AI Yanıtı (ai_generated)
      ↓
Bilgilendirme + disclaimer
```

```powershell
python poc/rag/indexer.py
python poc/chatbot.py --groq --json --question "Zencefil mide bulantısına iyi gelir mi?"
```

## Açık sorular (takımla netleştirilecek)

- [ ] Backend ürün verisini REST API olarak verecek (`GET /api/products`) — mock JSON geçici
- [ ] Chatbot ürün önerecek mi, sadece bilgi mi verecek?
