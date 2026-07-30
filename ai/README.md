# PhyraMed — AI Modülü

PhyraMed'in yapay zeka bileşenleri bu klasörde geliştirilir: **bitki görsel tanıma**, **kullanıcı yorumu analizi** ve **RAG destekli chatbot** altyapısı.

> Bu modül bilgilendirme amaçlıdır; tıbbi tavsiye sunmaz.

---

## Sprint 1 — Araştırma & POC

| Alan | Durum | Açıklama |
|------|-------|----------|
| Görsel tanıma | POC hazır | Groq Qwen 3.6 27B (vision) ile bitki fotoğrafından tanımlama |
| Yorum analizi | POC hazır | Olumlu/olumsuz/nötr sınıflandırma + özet |
| Chatbot mimarisi | Karar verildi | MVP: prompt tabanlı; Sprint 3: RAG |

## Sprint 2 — Test & Temel Sürüm

| Alan | Durum | Açıklama |
|------|-------|----------|
| Görsel tanıma | Değerlendirme | Etiketli veri seti + doğruluk metrikleri (`image_eval.py`) |
| Yorum analizi | Format belirlendi | Olumlu/olumsuz oran + en sık yan etki JSON şeması |
| Chatbot | Temel sürüm | Ürün DB'ye bağlı prompt tabanlı asistan (`chatbot.py`) |

## Sprint 3 — RAG + Orkestrasyon + API

| Alan | Durum | Açıklama |
|------|-------|----------|
| RAG | Tamamlandı | ChromaDB vektör store + hibrit retrieval |
| Hafıza | Tamamlandı | Oturum bazlı çok turlu konuşma (`memory.py`) |
| Orkestrasyon | Tamamlandı | Retrieve → generate akışı (`orchestrator.py`) |
| Görsel tanıma | İyileştirildi | v3 prompt, düşük güven fallback, ürün eşleştirme |
| Yorum analizi | İyileştirildi | Ürün bazlı özet, negasyon handling |
| REST API | Tamamlandı | FastAPI — chat, identify, review-summary |

### Dokümanlar

| Sprint | Dosya | Konu |
|--------|-------|------|
| 1 | [`docs/01-gorsel-tanima.md`](docs/01-gorsel-tanima.md) | API seçenekleri |
| 1 | [`docs/02-yorum-analizi.md`](docs/02-yorum-analizi.md) | Sentiment yaklaşımları |
| 1 | [`docs/03-chatbot-mimari.md`](docs/03-chatbot-mimari.md) | Prompt vs RAG |
| 2 | [`docs/04-yorum-ozet-formati.md`](docs/04-yorum-ozet-formati.md) | Standart özet JSON |
| 2 | [`docs/05-gorsel-degerlendirme.md`](docs/05-gorsel-degerlendirme.md) | Doğruluk ölçümü |
| 2 | [`docs/06-chatbot-sprint2.md`](docs/06-chatbot-sprint2.md) | Chatbot kullanımı |
| 3 | [`docs/07-rag-orchestration.md`](docs/07-rag-orchestration.md) | RAG + hafıza + API |

### Script'ler

| Script | Sprint | Ne yapar |
|--------|--------|----------|
| `poc/rag/indexer.py` | 3 | Vektör indeks oluşturur |
| `poc/chatbot.py` | 3 | RAG + hafıza destekli chatbot |
| `poc/orchestrator.py` | 3 | Orkestrasyon katmanı |
| `poc/memory.py` | 3 | Oturum hafızası |
| `poc/vision.py` | 3 | Görsel tanıma + ürün eşleştirme |
| `poc/image_test.py` | 1/3 | Tek fotoğraf tanıma |
| `poc/image_eval.py` | 2/3 | Veri seti doğruluk ölçümü |
| `poc/sentiment_test.py` | 1/3 | Basit sentiment testi |
| `poc/sentiment_summary.py` | 2/3 | Standart JSON özet üretir |
| `poc/product_db.py` | 2 | Ürün arama / bağlam |
| `poc/groq_client.py` | 1 | Groq API istemcisi |
| `api/main.py` | 3 | REST API sunucusu |

---

## Kurulum

```powershell
cd ai
pip install -r requirements.txt
python poc/rag/indexer.py
```

Groq API kullanmak için (görsel tanıma, Groq chatbot, gelişmiş sentiment):

```powershell
copy .env.example .env
# .env içine GROQ_API_KEY=... yaz
```

**Key olmadan da** chatbot şablon modunda, sentiment keyword modunda çalışır.

---

## Çalıştırma

```powershell
# --- Sprint 3: RAG Chatbot ---
python poc/chatbot.py --groq --json --question "Zencefil mide bulantısına iyi gelir mi?"
python poc/chatbot.py --groq

# --- REST API ---
uvicorn api.main:app --reload --app-dir .

# --- Görsel tanıma ---
python poc/image_test.py poc/sample/ginger.jpg --json
python poc/image_eval.py --prompt-v3

# --- Yorum analizi ---
python poc/sentiment_summary.py --by-product
python poc/sentiment_summary.py --product Zencefil --groq
python poc/sentiment_test.py
```

Fotoğraflar **20 MB altında** olmalı (Groq vision limiti).

---

## Testler

```powershell
cd ai
python -m pytest tests/ -v
```

---

## Klasör yapısı

```
ai/
├── api/                     # FastAPI REST katmanı
├── docs/                    # Araştırma ve karar notları
├── tests/                   # Otomatik testler
├── poc/
│   ├── rag/                 # RAG pipeline (indexer, retriever, store)
│   ├── data/
│   │   ├── products_db.json
│   │   └── vector_store/    # ChromaDB (üretilir)
│   ├── dataset/image_labels.json
│   ├── reports/
│   ├── sample/
│   └── *.py
├── requirements.txt
└── README.md
```

Ana proje bilgisi için: [../README.md](../README.md)
