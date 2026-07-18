# Görev 3 — Chatbot Mimari Kararı

PhyraMed chatbot'u bitkisel ürünler hakkında **bilgilendirme** yapacak (tıbbi tavsiye değil).

## İki seçenek

### A) Basit prompt tabanlı
- System prompt + ürün bilgisi metne eklenir
- **Artı:** Hızlı, az kod, Sprint 1 MVP'ye uygun
- **Eksi:** Bilgi güncellemek için kod değişir

### B) RAG
- Dokümanlar vektör DB'ye kaydedilir, soruya göre parça çekilir
- **Artı:** Ölçeklenebilir, kaynak gösterilebilir
- **Eksi:** Daha fazla altyapı (embedding, vektör DB)

## Sprint 1 kararı

| | Seçim |
|---|-------|
| **MVP (şimdi)** | Basit prompt tabanlı |
| **İleride** | RAG'e geçiş |

**Gerekçe:** Az ürün, hızlı demo, backend entegrasyonu kolay.

## Sprint 2 — uygulama

Temel chatbot kuruldu. Detay: [`06-chatbot-sprint2.md`](06-chatbot-sprint2.md)

```powershell
python poc/chatbot.py --question "Zencefil mide bulantısına iyi gelir mi?"
```

## Açık sorular (takımla netleştirilecek)

- [ ] Backend ürün verisini REST API olarak verecek (`GET /api/products`)
- [ ] Chatbot ürün önerecek mi, sadece bilgi mi verecek?
