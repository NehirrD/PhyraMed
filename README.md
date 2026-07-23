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
