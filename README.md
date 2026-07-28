# PhyraMed Frontend

Framework ya da build aracı yok. Düz HTML/CSS/JS — çift tıkla `index.html`'i aç, çalışır.

## Klasör yapısı

```
index.html            Anasayfa
pages/
  urun.html            Ürün detay sayfası (?id= parametresiyle çalışır)
  profil.html          Profil ve geçmiş aramalar
  gorsel-tanima.html   Bitki fotoğrafı yükleme / tanıma sonucu
css/style.css          Tasarım sistemi
js/
  data.js              Mock veri
  api.js               Backend entegrasyonu, bağlanamazsa mock'a döner
  main.js              Navbar/footer/chatbot ve ortak yardımcılar
```

## Birkaç teknik not

Navbar, footer ve chatbot her sayfaya `js/main.js` üzerinden enjekte ediliyor, yani HTML tekrarı yok — bir yeri değiştirince hepsi güncelleniyor.

Veri alanları backend'deki `models/*.py` ile aynı isimlerle tutuldu, böylece `js/data.js`'teki mock verinin yerine `fetch()` geçince sayfa tarafında neredeyse hiçbir şey değişmiyor.

Kullanıcıdan/veritabanından gelen metinler `escapeHTML()`'den geçiriliyor, direkt `innerHTML`'e basılmıyor. Veri yüklenirken de boş ekran yerine iskelet (skeleton) gösteriliyor. Scriptler `defer` ile yükleniyor ve hepsi tek bir `PhyraMed` nesnesi altında toplanıyor, global scope'u kirletmesin diye.

Tıbbi teşhis/tedavi amacı taşımadığımıza dair uyarı footer'da, ürün detay sayfasında ve chatbot'un ilk mesajında var.

## Hangi görev nerede

| Görev | Konum |
|---|---|
| SCRUM-14 – Frontend iskeleti | tüm proje |
| SCRUM-15 – Ürün detay taslağı | `pages/urun.html` |
| SCRUM-16 – Tasarım sistemi | `css/style.css` |
| SCRUM-17 – Routing | `pages/` klasörü, navbar |
| SCRUM-18 – Ana sayfa wireframe | `index.html` |
| SCRUM-35/53 – Chatbot + animasyon | `js/main.js` → `initChatbot()` |
| SCRUM-36 – Ürün detay (tüm alanlar) | `pages/urun.html` |
| SCRUM-37 – Görsel yükleme | `pages/gorsel-tanima.html` |
| SCRUM-54 – UI/UX cilalama | `css/style.css` |
| Profil + geçmiş aramalar | `pages/profil.html` |

## PO'nun içerik standardına uyum

PO, `docs/product-management/` altına iki doküman koydu (`evidence-classification.md`, `product-card-content-standard.md`) ve bazı terminoloji/davranış kuralları belirledi. Buna göre değiştirdiklerimiz:

"Uzman/doktor görüşü özeti" başlığı gitti, yerine "Bilimsel kanıt özeti" geldi — PO'nun istediği terim bu.

`evidence_level` artık sadece Güçlü/Orta/Zayıf değil; "Bekliyor" ve "Değerlendirilemedi" de gelebiliyor. Bunlar kanıt seviyesi sayılmadığı için renkli rozet yerine nötr gri bir ifadeyle gösteriliyor (bkz. `evidenceBadgeText()` / `evidenceStatusNote()` — `js/main.js`). Gerçek MVP veri setindeki 18 kaydın hepsi şu an zaten "Bekliyor" durumunda, mock veriye de bunu gösteren bir kayıt ekledik (id: 103).

Risk, etkileşim ya da kaynak bilgisi eksikse alanı boş bırakmıyoruz — standarttaki durum cümlelerini gösteriyoruz ("bilgi bulunmaması ürünün risksiz olduğu anlamına gelmez" gibi).

Kategori isim/açıklamaları `data/phyramed_mvp_seed_dataset_v1.xlsx`'teki Categories sekmesiyle birebir aynı.

Açık kalan bir konu var: backend'deki alan hâlâ `expert_opinion_summary` ismini taşıyor, PO'nun dokümanına göre bunun `evidence_summary` olarak yeniden adlandırılması gerekiyor (SCRUM-30). Bu backend/veri ekibinin kararı, biz sadece ekrandaki başlığı değiştirdik, alan adına dokunmadık.

## Backend entegrasyonu

Backend'de artık gerçek endpoint'ler var — `backend/dev3-nehir` ve `backend/dev4-alper` branch'lerinde, `develop`'a henüz merge edilmedi: `/category`, `/products`, `/products/identify`, `/chat`, `/analysis/comments/{id}`.

Bunlara bağlanan yer `js/api.js`. İçindeki `fetchCategories`, `fetchProducts`, `fetchProductDetail`, `sendChatMessage`, `identifyImage` fonksiyonlarının hepsi aynı mantıkla çalışıyor: önce gerçek API'yi dener, olmazsa (backend kapalı, CORS engeli, ağ sorunu, ne olursa) sessizce mock veriye döner. Yani bu dosya bağlansın bağlanmasın site çalışmaya devam ediyor.

Backend adresini değiştirmek istersen `js/api.js`'in en üstündeki `API_BASE_URL`'i güncelle (şu an `http://localhost:8000`).

Test ettim, backend'i lokalde ayağa kaldırıp gerçek veriyle denedim — çalışıyor. Tek eksik: backend'de CORS ayarı yok, main.py'ye `CORSMiddleware` eklenmesi lazım, yoksa tarayıcı gerçek API'yi engelleyip otomatik mock'a düşecek.

Mock ile gerçek API arasında birkaç küçük fark var, aklında olsun:

- `evidence_level` gerçek API'de sadece Güçlü/Orta/Zayıf — "Bekliyor"/"Değerlendirilemedi" henüz backend'de yok (SCRUM-30 açık). `null` da gelebilir, ona göre null-safe yazdık.
- `/products/identify`'nin `confidence` alanı yüzde değil, "yüksek/orta/düşük" gibi bir metin.
- Kategori nesnesinde artık `search_count` var (popülerlik takibi), şu an kullanmıyoruz ama `/category/popular` hazır bekliyor.

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
