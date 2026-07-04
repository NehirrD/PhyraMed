# PhyraMed — AI Modülü

PhyraMed'in yapay zeka bileşenleri bu klasörde geliştirilir: **bitki görsel tanıma**, **kullanıcı yorumu analizi** ve **chatbot** altyapısı.

> Bu modül bilgilendirme amaçlıdır; tıbbi tavsiye sunmaz.

---

## Sprint 1'de yapılanlar

| Alan | Durum | Açıklama |
|------|-------|----------|
| Görsel tanıma | POC hazır | Groq Llama 4 Scout ile bitki fotoğrafından tanımlama |
| Yorum analizi | POC hazır | Olumlu/olumsuz/nötr sınıflandırma + özet |
| Chatbot mimarisi | Karar verildi | MVP: prompt tabanlı; ileride RAG |

### Araştırma dokümanları

- [`docs/01-gorsel-tanima.md`](docs/01-gorsel-tanima.md) — API seçenekleri ve Groq önerisi
- [`docs/02-yorum-analizi.md`](docs/02-yorum-analizi.md) — Sentiment yaklaşımları ve test sonuçları
- [`docs/03-chatbot-mimari.md`](docs/03-chatbot-mimari.md) — Prompt vs RAG kararı

### POC script'leri

| Script | Ne yapar |
|--------|----------|
| `poc/image_test.py` | Bitki fotoğrafını Groq vision API ile analiz eder |
| `poc/sentiment_test.py` | Örnek yorumları sınıflandırır (kelime listesi veya Groq) |
| `poc/groq_client.py` | Groq API ortak istemcisi |
| `poc/sample_comments.json` | Test için 10 örnek kullanıcı yorumu |
| `poc/sample/` | Örnek bitki fotoğrafları (zencefil, nane, zerdeçal) |

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
# Yorum analizi (key gerekmez)
python poc/sentiment_test.py

# Yorum analizi (Groq ile)
python poc/sentiment_test.py --groq

# Bitki fotoğrafı tanıma (key gerekir)
python poc/image_test.py poc/sample/ginger.jpg
```

Fotoğraflar **4 MB altında** olmalı (Groq base64 limiti).

---

## Klasör yapısı

```
ai/
├── docs/           # Sprint 1 araştırma ve karar notları
├── poc/            # Deneme script'leri ve örnek veriler
├── requirements.txt
└── README.md
``

Ana proje bilgisi için: [../README.md](../README.md)
