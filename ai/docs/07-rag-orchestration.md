# Sprint 3 — RAG + Orkestrasyon + Hafiza

## Mimari

```text
Kullanici sorusu + session_id
        |
        v
+------------------+
| Session Memory   |  <- onceki 8 tur
+------------------+
        |
        v
+------------------+
| Hybrid Retrieval |
|  - ChromaDB (RAG)|
|  - Keyword search|
+------------------+
        |
        v
+------------------+
| Orchestrator     |
|  - Kaynak secimi |
|  - Prompt olustur|
+------------------+
        |
        v
+------------------+
| Groq LLM         |  (veya sablon)
+------------------+
        |
        v
Yapilandirilmis JSON yanit
```

## Bilesenler

| Dosya | Gorev |
|-------|-------|
| `poc/rag/indexer.py` | Urun chunk'larini vektor store'a yazar |
| `poc/rag/retriever.py` | Semantik + keyword hibrit arama |
| `poc/rag/store.py` | ChromaDB kalici depo |
| `poc/memory.py` | Oturum bazli konusma gecmisi |
| `poc/orchestrator.py` | Retrieve -> generate akisi |
| `poc/chatbot.py` | CLI arayuz |
| `api/main.py` | REST API |

## Kurulum

```powershell
cd ai
pip install -r requirements.txt
python poc/rag/indexer.py
```

## Kullanim

```powershell
# Indeks olustur
python poc/rag/indexer.py

# RAG chatbot (JSON cikti)
python poc/chatbot.py --groq --json --question "Uyku icin ne onerirsiniz?"

# Cok turlu oturum
python poc/chatbot.py --groq

# REST API
uvicorn api.main:app --reload --app-dir .
```

## API Endpoints

| Method | Endpoint | Aciklama |
|--------|----------|----------|
| POST | `/api/chat` | RAG chatbot |
| DELETE | `/api/chat/sessions/{id}` | Oturumu temizle |
| POST | `/api/identify` | Gorsel bitki tanima |
| GET | `/api/products/{id}/review-summary` | Urun yorum ozeti |
| GET | `/api/reviews/summary` | Tum urun ozetleri |
| GET | `/api/products` | Urun listesi |

### Ornek: POST /api/chat

```json
{
  "question": "Zencefil mide bulantisina iyi gelir mi?",
  "session_id": null,
  "use_groq": true
}
```

Yanit:

```json
{
  "answer": "...",
  "source": "verified_db",
  "sources": [{"id": 3, "name": "Zencefil"}],
  "retrieved_chunks": [...],
  "session_id": "uuid"
}
```

## Hafiza (Memory)

- Her oturum benzersiz `session_id` alir
- Son 20 tur saklanir; LLM'e son 8 tur gonderilir
- `memory_store` singleton — CLI ve API paylasir
- Production icin Redis/PostgreSQL ile degistirilebilir

## RAG Detaylari

- **Chunking:** Her urun alani (name, claim, evidence, risk, ...) ayri chunk
- **Embedding:** ChromaDB varsayilan embedding modeli
- **Retrieval:** Keyword + semantic birlestirme, skor sirali top-5
- **Kaynak:** Urun bulunursa `verified_db`, yoksa `ai_generated`
