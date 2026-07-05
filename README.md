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
