# PhyraMed Frontend

Build aracı veya framework kullanılmamıştır; proje düz HTML/CSS/JS ile
geliştirilmiştir.

## Çalıştırma

Kurulum gerekmez. `index.html` dosyası tarayıcıda açılarak çalıştırılabilir.

## Klasör yapısı

```
index.html            Anasayfa
pages/
  urun.html            Ürün detay sayfası (?id= parametresiyle çalışır)
  profil.html          Profil ve geçmiş aramalar sayfası
  gorsel-tanima.html   Bitki fotoğrafı yükleme ve tanıma sonucu sayfası
css/style.css          Tasarım sistemi
js/
  data.js              Mock veri (backend modelleriyle uyumlu)
  api.js               Gerçek backend entegrasyonu (mock'a otomatik fallback)
  main.js              Ortak bileşenler ve arayüz mantığı
```

## Teknik notlar

- Navbar, footer ve chatbot bileşenleri `js/main.js` üzerinden tüm
  sayfalara enjekte edilir; tekrar eden HTML bulunmaz.
- Veri alanları backend'deki `models/*.py` yapısıyla birebir uyumludur.
  API entegrasyonunda `js/data.js` içindeki mock veriler `fetch()`
  çağrılarıyla değiştirilir, sayfa tarafında ek değişiklik gerekmez.
- Kullanıcıdan/veritabanından gelen tüm metin alanları `escapeHTML()`
  ile işlenir.
- Veri yüklenirken iskelet (skeleton) bileşenleri gösterilir.
- Script'ler `defer` ile yüklenir; tek bir `PhyraMed` nesnesi altında
  toplanır.

## Sorumluluk reddi

Platformun tıbbi teşhis/tedavi amacı taşımadığı bilgisi footer'da,
ürün detay sayfasında ve chatbot'un ilk mesajında belirtilmiştir.

## Görev karşılıkları

| Görev | Konum |
|---|---|
| SCRUM-14: Frontend iskeleti | tüm proje |
| SCRUM-15: Ürün detay sayfası taslağı | `pages/urun.html` |
| SCRUM-16: Ortak tasarım sistemi | `css/style.css` |
| SCRUM-17: Routing/sayfa geçişleri | `pages/` klasörü, navbar |
| SCRUM-18: Ana sayfa wireframe'i | `index.html` |
| SCRUM-35/53: Chatbot arayüzü ve animasyonu | `js/main.js` → `initChatbot()` |
| SCRUM-36: Ürün detay sayfası (tüm alanlar) | `pages/urun.html` |
| SCRUM-37: Görsel yükleme arayüzü | `pages/gorsel-tanima.html` |
| SCRUM-54: UI/UX cilalama | `css/style.css` |
| Profil + geçmiş aramalar | `pages/profil.html` |

## PO içerik standardıyla uyum

GitHub'daki `docs/product-management/` altında PO tarafından yayımlanan iki
doküman (`evidence-classification.md`, `product-card-content-standard.md`)
bazı terminoloji ve davranış kuralları tanımlıyor; bu sürümde uygulandı:

- Ürün detayında "Uzman/doktor görüşü özeti" başlığı kaldırıldı, yerine
  bağlayıcı terim olan **"Bilimsel kanıt özeti"** kullanıldı.
- `evidence_level` sadece Güçlü/Orta/Zayıf değil, **Bekliyor** ve
  **Değerlendirilemedi** durumlarını da alabiliyor; bunlar birer kanıt
  seviyesi olmadığı için renkli rozet yerine nötr gri bir durum ifadesiyle
  gösteriliyor (`js/main.js` → `evidenceBadgeText()`, `evidenceStatusNote()`).
  Gerçek MVP veri setindeki 18 kaydın tamamı şu an "Bekliyor" durumunda,
  mock veriye bunu örnekleyen bir kayıt eklendi (id: 103).
- Risk, etkileşim ve kaynak bilgisi eksik olduğunda alan boş bırakılmıyor;
  standartta tanımlanan durum cümleleri gösteriliyor (ör. "Bilgi bulunmaması
  ürünün risksiz olduğu anlamına gelmez").
- Kategori adı ve açıklamaları `data/phyramed_mvp_seed_dataset_v1.xlsx`
  (Categories sekmesi) ile birebir eşleştirildi.

**Açık nokta:** Backend modelindeki (`models/product.py`) alan adı hâlâ
`expert_opinion_summary`; PO dokümanı bunun `evidence_summary` anlamıyla
yeniden eşleştirilmesi gerektiğini belirtiyor (SCRUM-30 kapsamında). Bu,
backend/veri ekibinin kararı — frontend tarafında sadece ekrandaki başlık
güncellendi, veri alanı adı değişmedi.

## Backend entegrasyonu

Backend'de artık gerçek endpoint'ler var (`backend/dev3-nehir`,
`backend/dev4-alper` branch'leri — henüz `develop`'a merge edilmedi):
`/category`, `/products`, `/products/identify`, `/chat`,
`/analysis/comments/{id}`. Bunlara bağlanan katman `js/api.js`.

**Nasıl çalışıyor:** `js/api.js` içindeki her fonksiyon (`fetchCategories`,
`fetchProducts`, `fetchProductDetail`, `sendChatMessage`, `identifyImage`)
önce gerçek API'yi dener; backend'e ulaşılamazsa (kapalı, CORS engeli, ağ
hatası) otomatik olarak mock veriye düşer. Yani bu dosya bağlansın ya da
bağlanmasın site her zaman çalışır — demo API çökse bile bozulmaz.

**Backend adresini ayarlamak için:** `js/api.js`'in en üstündeki
`window.PhyraMed.API_BASE_URL` değerini kendi ortamına göre değiştir
(varsayılan: `http://localhost:8000`).

### ⚠️ Backend ekibinin çözmesi gereken blocker: CORS

Backend'de (`main.py`) CORS ayarı henüz yok. Tarayıcıdan `fetch()` çağrısı
yapınca "blocked by CORS policy" hatası alman muhtemel — bu bizim
tarafımızda düzeltilebilecek bir şey değil. Nehir/Alper'e şu kodu
`main.py`'ye eklemelerini ilet:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # geliştirme aşamasında; production'da spesifik domain(ler) yazılmalı
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Bilinen veri şekli farkları (mock ↔ gerçek API)

- `evidence_level`: gerçek API'de enum sadece Güçlü/Orta/Zayıf tanıyor,
  "Bekliyor"/"Değerlendirilemedi" henüz backend'e eklenmedi (SCRUM-30 hâlâ
  açık). Alan `null` da gelebilir; frontend bunu nötr "Değerlendiriliyor"
  durumu olarak gösteriyor (`evidenceClassName()`/`evidenceBadgeText()`
  null-safe yazıldı).
- `/products/identify`'nin döndürdüğü `confidence` alanı yüzde değil,
  "yüksek/orta/düşük" gibi bir METİN — mock veri buna göre güncellendi.
- Kategori nesnesinde artık `search_count` alanı var (popülerlik takibi);
  frontend şu an bunu kullanmıyor ama ileride "popüler kategoriler"
  gösterimi için `/category/popular` endpoint'i hazır.

## Git akışı

```bash
git checkout develop
git pull
git checkout frontend/dev2-ahmet
git merge develop
git add .
git commit -m "[SCRUM-XX] açıklama"
git push origin frontend/dev2-ahmet
```
