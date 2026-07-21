# Görev 3 — Chatbot Mimari Kararı

PhyraMed chatbot'u bitkisel ürünler hakkında **bilgilendirme** yapacak (tıbbi tavsiye değil).

## İki seçenek

### A) Basit prompt tabanlı
- System prompt + ürün bilgisi metne eklenir.
- Chatbot önce ürün veritabanında arama yapar.
- Ürün bulunursa doğrulanmış ürün bilgileri kullanılarak cevap oluşturulur.
- Ürün bulunamazsa Groq modelinin genel bilgisinden yararlanılarak bilgilendirici cevap verilir.
- **Artı:** Hızlı, az kod, Sprint 1 MVP'ye uygun
- **Eksi:** Ürün sayısı arttıkça yönetimi zorlaşır, canlı internet verisi kullanılmaz.

### B) RAG
- Dokümanlar vektör DB'ye kaydedilir, soruya göre ilgili içerik çekilir.
- **Artı:** Ölçeklenebilir, kaynak gösterilebilir.
- **Eksi:** Daha fazla altyapı gerekir (embedding, vektör DB).

## Sprint 1 kararı

| | Seçim |
|---|-------|
| **MVP (şimdi)** | Basit prompt tabanlı |
| **İleride** | RAG'e geçiş |

**Gerekçe:** Az ürün, hızlı demo, backend entegrasyonu kolay. Ürün veritabanı büyüdüğünde veya internet araması eklendiğinde RAG mimarisine geçilmesi planlanmaktadır.

## Sprint 2 — uygulama

Temel chatbot kuruldu. Çalışma mantığı:

```text
Kullanıcı sorusu
      ↓
Ürün veritabanında arama
      ↓
Ürün bulundu mu?
     ├── Evet
     │      ↓
     │  Ürün bilgileri prompt'a eklenir
     │      ↓
     │  Kaynak: Onaylanmış Bilgi
     │
     └── Hayır
            ↓
      Groq genel bilgisi kullanılır
            ↓
      Kaynak: AI Yanıtı
            ↓
Bilgilendirme + disclaimer
```

Detay: [`06-chatbot-sprint2.md`](06-chatbot-sprint2.md)

```powershell
python poc/chatbot.py --question "Zencefil mide bulantısına iyi gelir mi?"
```

## Açık sorular (takımla netleştirilecek)

- [ ] Backend ürün verisini REST API olarak verecek (`GET /api/products`)
- [ ] Chatbot ürün önerecek mi, sadece bilgi mi verecek?