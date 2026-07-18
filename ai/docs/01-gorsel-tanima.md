# Görev 1 — Görsel Tanıma Araştırması

PhyraMed'de kullanıcı bitki fotoğrafı yükleyecek. Sprint 1 için en basit seçenekler:

## Seçenek karşılaştırması

| Seçenek | Zorluk | Ücret | Sprint 1 için |
|---------|--------|-------|---------------|
| **Groq Qwen 3.6 27B (vision)** | Kolay | Ücretsiz kota | ✅ Güncel vision modeli |
| Groq Llama 4 Scout (vision) | Kolay | — | ❌ 2026-07-17'de kaldırıldı |
| OpenAI GPT-4o (vision) | Kolay | Ücretli | Alternatif |
| Google Cloud Vision | Orta | Ücretsiz kotası var | Backend entegrasyonu gerekir |
| Hugging Face (yerel model) | Zor | Ücretsiz | ❌ İlk sprint için fazla |

## Sprint 1 önerisi

**Groq `qwen/qwen3.6-27b`** — güncel multimodal model (Llama 4 Scout yerine).

> **Not:** `meta-llama/llama-4-scout-17b-16e-instruct` Groq'ta **17 Temmuz 2026**'da kaldırıldı. 404 alırsan model adını kontrol et.

## POC denemesi

`.env`'e `GROQ_API_KEY` ekle. Bir bitki fotoğrafını `poc/sample/` klasörüne koy (ör. `ginger.jpg`):

```powershell
# Windows: kendi fotoğrafını kopyala
copy C:\Users\melik\Pictures\ginger.jpg poc\sample\ginger.jpg

python poc/image_test.py poc/sample/ginger.jpg
# veya sadece dosya adı: python poc/image_test.py ginger.jpg
```

Fotoğraf **20 MB altında** olmalı (Groq vision limiti).

## Sprint 2 — değerlendirme

Etiketli veri seti ve doğruluk ölçümü eklendi. Detay: [`05-gorsel-degerlendirme.md`](05-gorsel-degerlendirme.md)

```powershell
python poc/image_eval.py
python poc/image_eval.py --prompt-v2
```

## Sonuç / karar

- [x] Seçilen API: Groq Qwen 3.6 27B (`qwen/qwen3.6-27b`)
- [x] Neden: Llama 4 Scout kaldırıldı; Groq'un güncel vision modeli
