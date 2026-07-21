# PhyraMed — AI Modülü

PhyraMed'in yapay zeka bileşenleri bu klasörde geliştirilir: **bitki görsel tanıma**, **kullanıcı yorumu analizi** ve **chatbot** altyapısı.

> Bu modül bilgilendirme amaçlıdır; tıbbi tavsiye sunmaz.

---

## Sprint 1 — Araştırma & POC

| Alan | Durum | Açıklama |
|------|-------|----------|
| Görsel tanıma | POC hazır | Groq Qwen 3.6 27B (vision) ile bitki fotoğrafından tanımlama |
| Yorum analizi | POC hazır | Olumlu/olumsuz/nötr sınıflandırma + özet |
| Chatbot mimarisi | Karar verildi | MVP: prompt tabanlı; ileride RAG |

## Sprint 2 — Test & Temel Sürüm

| Alan | Durum | Açıklama |
|------|-------|----------|
| Görsel tanıma | Değerlendirme | Etiketli veri seti + doğruluk metrikleri (`image_eval.py`) |
| Yorum analizi | Format belirlendi | Olumlu/olumsuz oran + en sık yan etki JSON şeması |
| Chatbot | Temel sürüm | Ürün DB'ye bağlı prompt tabanlı asistan (`chatbot.py`) |

### Dokümanlar

| Sprint | Dosya | Konu |
|--------|-------|------|
| 1 | [`docs/01-gorsel-tanima.md`](docs/01-gorsel-tanima.md) | API seçenekleri |
| 1 | [`docs/02-yorum-analizi.md`](docs/02-yorum-analizi.md) | Sentiment yaklaşımları |
| 1 | [`docs/03-chatbot-mimari.md`](docs/03-chatbot-mimari.md) | Prompt vs RAG |
| 2 | [`docs/04-yorum-ozet-formati.md`](docs/04-yorum-ozet-formati.md) | Standart özet JSON |
| 2 | [`docs/05-gorsel-degerlendirme.md`](docs/05-gorsel-degerlendirme.md) | Doğruluk ölçümü |
| 2 | [`docs/06-chatbot-sprint2.md`](docs/06-chatbot-sprint2.md) | Chatbot kullanımı |

### Script'ler

| Script | Sprint | Ne yapar |
|--------|--------|----------|
| `poc/image_test.py` | 1 | Tek fotoğraf tanıma |
| `poc/image_eval.py` | 2 | Veri seti doğruluk ölçümü |
| `poc/sentiment_test.py` | 1 | Basit sentiment testi |
| `poc/sentiment_summary.py` | 2 | Standart JSON özet üretir |
| `poc/chatbot.py` | 2 | Ürün DB'ye bağlı chatbot |
| `poc/product_db.py` | 2 | Ürün arama / bağlam |
| `poc/groq_client.py` | 1 | Groq API istemcisi |

---

## Kurulum

```powershell
cd ai
pip install -r requirements.txt
```

Groq API kullanmak için (görsel tanıma ve gelişmiş sentiment):

```powershell
copy .env.example .env
# .env içine GROQ_API_KEY=... yaz
```

**Key olmadan da** `sentiment_test.py` basit kelime yöntemiyle çalışır.

---

## Çalıştırma

```powershell
# --- Sprint 1 ---
python poc/sentiment_test.py
python poc/sentiment_test.py --groq
python poc/image_test.py poc/sample/ginger.jpg

# --- Sprint 2 ---
python poc/sentiment_summary.py
python poc/sentiment_summary.py --groq
python poc/image_eval.py
python poc/image_eval.py --prompt-v2
python poc/chatbot.py --question "Zencefil mide bulantısına iyi gelir mi?"
python poc/chatbot.py --groq
```

Fotoğraflar **20 MB altında** olmalı (Groq vision limiti).

---

## Klasör yapısı

```
ai/
├── docs/                    # Araştırma ve karar notları
├── poc/
│   ├── data/products_db.json    # Mock ürün veritabanı
│   ├── dataset/image_labels.json
│   ├── reports/                 # Değerlendirme raporları (üretilir)
│   ├── sample/                  # Bitki fotoğrafları
│   └── *.py
├── requirements.txt
└── README.md
``

Ana proje bilgisi için: [../README.md](../README.md)
