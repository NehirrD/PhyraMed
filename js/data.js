// PhyraMed — sahte (mock) veri
// Backend'deki models/*.py alan adlarıyla birebir uyumlu tutuldu.
// API hazır olunca bu dosyanın yerine gerçek fetch() çağrıları gelecek;
// sayfalardaki render kodları aynı kalabilir.
//
// Not: Bunu ES modülü (export/import) olarak değil, klasik script olarak
// yazdık. Sebebi basit: ES modülleri tarayıcılarda file:// üzerinden (yani
// dosyaya çift tıklayıp açtığında) CORS kısıtlaması yüzünden çalışmıyor.
// Proje bir sunucu olmadan doğrudan açılabilsin diye klasik yöntemde kaldık,
// ama global scope kirlenmesin diye her şeyi tek bir PhyraMed nesnesi
// altında topluyoruz.
window.PhyraMed = window.PhyraMed || {};

// Her kategori için tekil, konuyla ilgili bir ikon (lucide tarzı, 24x24, stroke).
// Sayı rozeti (01/02/03) yerine anlamlı ikon kullanmak, kategoriyi bir bakışta
// tanınır kılıyor.
// İsim ve açıklamalar data/phyramed_mvp_seed_dataset_v1.xlsx (Categories
// sekmesi) ile birebir uyumlu tutuldu.
window.PhyraMed.CATEGORIES = [
  {
    id: 1,
    name: "Uyku ve Dinlenme",
    description: "Uyku düzeni, uykuya geçiş ve dinlenme amacıyla araştırılan bitki ve takviyeler.",
    icon: '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
  },
  {
    id: 2,
    name: "Stres ve Zihinsel İyi Oluş",
    description: "Stres belirtileri ve zihinsel iyi oluş amacıyla araştırılan bitki ve takviyeler.",
    icon: '<path d="M12 3a5 5 0 0 0-5 5c0 2 1 3 1 5v2a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2v-2c0-2 1-3 1-5a5 5 0 0 0-5-5z"/><path d="M9.5 21h5"/>',
  },
  {
    id: 3,
    name: "Sindirim ve Bağırsak Sağlığı",
    description: "Sindirim sistemi, bağırsak işlevi, bulantı ve karın rahatsızlığı amacıyla araştırılan ürünler.",
    icon: '<path d="M6 3c0 4-3 5-3 9a7 7 0 0 0 14 0c0-3-2-3-2-6"/><path d="M13 3c1 2 2 3 2 6"/>',
  },
  {
    id: 4,
    name: "Bağışıklık Desteği",
    description: "Bağışıklık sisteminin normal işlevini destekleme veya üst solunum yolu şikâyetleriyle ilişkilendirilen ürünler.",
    icon: '<path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6z"/>',
  },
  {
    id: 5,
    name: "Enerji ve Yorgunluk",
    description: "Eksiklik durumları veya günlük yorgunlukla ilişkilendirilen vitamin, mineral ve bitkisel takviyeler.",
    icon: '<path d="M12 2 4 14h6l-1 8 9-13h-6z"/>',
  },
  {
    id: 6,
    name: "Cilt, Saç ve Tırnak Desteği",
    description: "Cilt, saç ve tırnak görünümü veya sağlığı için kullanılan takviye ve bitkisel ürünler.",
    icon: '<path d="M12 2C8 7 5 10.5 5 14.5A7 7 0 0 0 19 14.5C19 10.5 16 7 12 2z"/>',
  },
];

// NOT (PO içerik standardı — docs/product-management/product-card-content-standard.md):
// Teknik alan adı `expert_opinion_summary` olarak kalıyor (backend modeliyle
// birebir uyumlu olsun diye), ama PO'nun ürün terminolojisi kararına göre
// kullanıcıya gösterilen başlık "Uzman/doktor görüşü" DEĞİL, "Bilimsel kanıt
// özeti" olmalı — bkz. pages/urun.html. Yani veri alanı adı ile ekrandaki
// başlık kasıtlı olarak farklı; SCRUM-30 kapsamında backend tarafında da
// yeniden adlandırılması planlanıyor.
//
// evidence_level değeri sadece Güçlü/Orta/Zayıf değil, "Bekliyor" (henüz
// değerlendirilmedi) ve "Değerlendirilemedi" de olabilir — gerçek MVP veri
// setindeki (data/phyramed_mvp_seed_dataset_v1.xlsx) 18 kaydın tamamı şu an
// "Bekliyor" durumunda, bu yüzden aşağıya o durumu da örnekleyen bir kayıt
// eklendi (bkz. id: 103).
window.PhyraMed.PRODUCTS = [
  {
    id: 101,
    name: "Demir (Bitkisel Kaynaklı)",
    category_id: 4,
    usage_purpose: "Demir eksikliğine bağlı yorgunluğu azaltmaya yönelik kullanılır.",
    evidence_level: "Güçlü",
    expert_opinion_summary:
      "Klinik çalışmalar demir eksikliği anemisinde takviyenin etkili olduğunu göstermektedir; doz doktor kontrolünde belirlenmelidir.",
    status: "Onaylanmış",
    risks: [{ id: 1, description: "Yüksek dozda mide bulantısı ve kabızlık görülebilir.", severity: "Orta" }],
    interactions: [{ id: 1, interacts_with: "Kalsiyum takviyeleri", description: "Birlikte alımı demirin emilimini azaltabilir." }],
    sources: [{ id: 1, type: "Akademik Makale", title: "Iron supplementation and fatigue: a systematic review" }],
  },
  {
    id: 102,
    name: "Goji Berry Ekstresi",
    category_id: 5,
    usage_purpose: "Enerji ve genel iyi oluş için antioksidan destek amacıyla kullanılır.",
    evidence_level: "Zayıf",
    expert_opinion_summary:
      "Mevcut çalışmalar küçük örneklem gruplarıyla sınırlıdır; enerji artışı iddiaları güçlü klinik kanıtla desteklenmemektedir.",
    status: "AI",
    risks: [],
    interactions: [],
    sources: [{ id: 2, type: "Resmi Sağlık Kuruluşu", title: "NCCIH — Goji Berry bilgi notu" }],
  },
  {
    id: 103,
    name: "Ashwagandha",
    category_id: 2,
    usage_purpose: "Stres yönetimini destekleme amacıyla araştırılmaktadır.",
    evidence_level: "Bekliyor",
    expert_opinion_summary:
      "Bazı kısa süreli çalışmalar algılanan stresin azalabileceğine işaret etse de, preparat ve doz farklılıkları nedeniyle sonuçlar genellenememektedir.",
    status: "AI",
    risks: [{ id: 2, description: "Uyuşukluk ve mide rahatsızlığı görülebilir; gebelikte kullanılmamalıdır.", severity: "Orta" }],
    interactions: [],
    sources: [],
  },
];

// Nice-to-have: profil + geçmiş aramalar
window.PhyraMed.SEARCH_HISTORY = [
  { id: 1, query: "demir eksikliği", category: "Bağışıklık Desteği", date: "2026-07-01" },
  { id: 2, query: "uykusuzluk için bitkisel", category: "Uyku ve Dinlenme", date: "2026-06-28" },
  { id: 3, query: "goji berry yan etki", category: "Enerji ve Yorgunluk", date: "2026-06-25" },
];

// SCRUM-37: Görsel tanıma modülü — henüz gerçek bir AI modeli bağlı değil,
// bu yüzden kullanıcı hangi fotoğrafı yüklerse yüklesin aynı örnek sonuç
// gösteriliyor. AI/Melike tarafındaki model hazır olunca bu sabit obje,
// görsel analiz endpoint'inin döneceği gerçek yanıtla değiştirilecek —
// alan adları (name, confidence, category, summary, related_product_id)
// o yanıtla uyumlu olacak şekilde seçildi.
window.PhyraMed.RECOGNITION_DEMO = {
  name: "Ispanak (Spinacia oleracea)",
  confidence: 92,
  category: "Bağışıklık Desteği",
  summary:
    "Demir ve C vitamini açısından zengin, yapraklı bir sebzedir. Demir eksikliğine bağlı yorgunlukla mücadelede destekleyici olarak tüketilebilir.",
  related_product_id: 101,
};
