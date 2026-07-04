# Görev 1 — Görsel Tanıma Araştırması

PhyraMed'de kullanıcı bitki fotoğrafı yükleyecek. Sprint 1 için en basit seçenekler:

## Seçenek karşılaştırması

| Seçenek | Zorluk | Ücret | Sprint 1 için |
|---------|--------|-------|---------------|
| **Groq Llama 4 Scout (vision)** | Kolay | Ücretsiz kota | ✅ En hızlı POC |
| OpenAI GPT-4o (vision) | Kolay | Ücretli | Alternatif |
| Google Cloud Vision | Orta | Ücretsiz kotası var | Backend entegrasyonu gerekir |
| Hugging Face (yerel model) | Zor | Ücretsiz | ❌ İlk sprint için fazla |

## Sprint 1 önerisi

**Groq `meta-llama/llama-4-scout-17b-16e-instruct`** — hızlı, ücretsiz kota, tek API çağrısı.

## POC denemesi

`.env`'e `GROQ_API_KEY` ekle. Bir bitki fotoğrafını `poc/sample/` klasörüne koy (ör. `ginger.jpg`):

```powershell
# Windows: kendi fotoğrafını kopyala
copy C:\Users\melik\Pictures\ginger.jpg poc\sample\ginger.jpg

python poc/image_test.py poc/sample/ginger.jpg
# veya sadece dosya adı: python poc/image_test.py ginger.jpg
```

Fotoğraf **4 MB altında** olmalı (Groq base64 limiti).

## Sonuç / karar

- [ ] Seçilen API: _______________
- [ ] Neden: _______________
