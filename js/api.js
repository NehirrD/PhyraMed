// PhyraMed — gerçek backend entegrasyon katmanı
// ------------------------------------------------------------
// Backend artık gerçek endpoint'lere sahip (bkz. backend/dev3-nehir,
// backend/dev4-alper branch'leri): /category, /products, /chat,
// /products/identify, /analysis/comments/{id}.
//
// ÖNEMLİ — şu an için iki blocker var:
// 1) Backend'de CORS ayarlanmamış (main.py'de CORSMiddleware yok).
//    Tarayıcıdan fetch() çağrısı yapınca "blocked by CORS policy" hatası
//    alman muhtemel; bu bizim değil, backend tarafının çözmesi gereken bir
//    şey (bkz. README'deki not).
// 2) Backend'in canlıda/paylaşılan bir adresi yok, sadece lokalde
//    (muhtemelen `uvicorn main:app` ile localhost:8000) çalışıyor.
//    Aşağıdaki API_BASE_URL'i kendi ortamına göre değiştir.
//
// Tasarım kararı: her fetch fonksiyonu başarısız olursa (backend kapalı,
// CORS engeli, ağ hatası vb.) sessizce mock veriye düşer. Böylece bu dosya
// bağlansın ya da bağlanmasın site her zaman çalışır durumda kalır —
// jüri/mentor demosu API çökse bile bozulmaz.

window.PhyraMed = window.PhyraMed || {};

// Backend lokalde farklı bir portta çalışıyorsa burayı güncelle.
window.PhyraMed.API_BASE_URL = "http://localhost:8000";

// Kategori isimleri backend'den geliyor ama ikon bilgisi backend modelinde
// yok (salt görsel bir frontend kararı) — isme göre ikon eşleştiriyoruz.
const ICONS_BY_CATEGORY_NAME = {
  "Uyku ve Dinlenme": '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
  "Stres ve Zihinsel İyi Oluş": '<path d="M12 3a5 5 0 0 0-5 5c0 2 1 3 1 5v2a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2v-2c0-2 1-3 1-5a5 5 0 0 0-5-5z"/><path d="M9.5 21h5"/>',
  "Sindirim ve Bağırsak Sağlığı": '<path d="M6 3c0 4-3 5-3 9a7 7 0 0 0 14 0c0-3-2-3-2-6"/><path d="M13 3c1 2 2 3 2 6"/>',
  "Bağışıklık Desteği": '<path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6z"/>',
  "Enerji ve Yorgunluk": '<path d="M12 2 4 14h6l-1 8 9-13h-6z"/>',
  "Cilt, Saç ve Tırnak Desteği": '<path d="M12 2C8 7 5 10.5 5 14.5A7 7 0 0 0 19 14.5C19 10.5 16 7 12 2z"/>',
};
const FALLBACK_ICON = '<circle cx="12" cy="12" r="9"/>';

function withIcon(category) {
  return { ...category, icon: ICONS_BY_CATEGORY_NAME[category.name] || FALLBACK_ICON };
}

/** Kategori listesini API'den çeker; başarısız olursa mock veriye döner. */
async function fetchCategories() {
  try {
    const res = await fetch(`${window.PhyraMed.API_BASE_URL}/category/`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data.map(withIcon);
  } catch (e) {
    console.warn("[PhyraMed] /category/ adresine ulaşılamadı, mock veriye dönülüyor:", e.message);
    return window.PhyraMed.CATEGORIES;
  }
}
window.PhyraMed.fetchCategories = fetchCategories;

/**
 * Ürünleri çeker (opsiyonel categoryId ile filtreler).
 * API şu an evidence_level olarak sadece Güçlü/Orta/Zayıf tanıyor —
 * "Bekliyor"/"Değerlendirilemedi" durumları backend'de henüz yok
 * (SCRUM-30 kapsamında bekleniyor); mock veri bu iki durumu örneklemeye
 * devam ediyor, gerçek API'den gelen üründe evidence_level null da olabilir.
 */
async function fetchProducts(categoryId) {
  try {
    const url = categoryId
      ? `${window.PhyraMed.API_BASE_URL}/category/${categoryId}/products`
      : `${window.PhyraMed.API_BASE_URL}/products/`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) {
    console.warn("[PhyraMed] Ürün API'sine ulaşılamadı, mock veriye dönülüyor:", e.message);
    return categoryId
      ? window.PhyraMed.PRODUCTS.filter((p) => p.category_id === categoryId)
      : window.PhyraMed.PRODUCTS;
  }
}
window.PhyraMed.fetchProducts = fetchProducts;

/** Tek ürünün tüm detayını (risk/kaynak/etkileşim dahil) çeker. */
async function fetchProductDetail(id) {
  try {
    const res = await fetch(`${window.PhyraMed.API_BASE_URL}/products/${id}`);
    if (res.status === 404) return null;
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) {
    console.warn("[PhyraMed] Ürün detay API'sine ulaşılamadı, mock veriye dönülüyor:", e.message);
    return window.PhyraMed.PRODUCTS.find((p) => p.id === id) || null;
  }
}
window.PhyraMed.fetchProductDetail = fetchProductDetail;

/** Chatbot mesajı gönderir. API'ye ulaşılamazsa sabit bir yanıt döner. */
async function sendChatMessage(message) {
  try {
    const res = await fetch(`${window.PhyraMed.API_BASE_URL}/chat/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data.response;
  } catch (e) {
    console.warn("[PhyraMed] Chat API'sine ulaşılamadı, sabit yanıt gösteriliyor:", e.message);
    return "Şu anda asistana bağlanamıyorum, birazdan tekrar dener misin? 🌿";
  }
}
window.PhyraMed.sendChatMessage = sendChatMessage;

/**
 * Görsel tanıma: gerçek API bir dosya (multipart/form-data) bekliyor ve
 * confidence alanını YÜZDE değil "yüksek/orta/düşük" gibi bir METİN olarak
 * dönüyor — bu, mock RECOGNITION_DEMO'daki `confidence: 92` sayısal
 * varsayımından farklı, gerçek entegrasyonda bu ayrımı unutma.
 */
async function identifyImage(file) {
  try {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${window.PhyraMed.API_BASE_URL}/products/identify`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return {
      name: data.identified_name,
      name_en: data.identified_name_en,
      confidence: data.confidence, // metin: "yüksek" / "orta" / "düşük"
      summary: data.description,
      matched_products: data.matched_products || [],
      disclaimer: data.disclaimer,
    };
  } catch (e) {
    console.warn("[PhyraMed] Görsel tanıma API'sine ulaşılamadı, örnek sonuç gösteriliyor:", e.message);
    const demo = window.PhyraMed.RECOGNITION_DEMO;
    return {
      name: demo.name,
      name_en: null,
      confidence: "orta", // mock'ta da API'nin gerçek formatına uyduruyoruz
      summary: demo.summary,
      matched_products: [],
      related_product_id: demo.related_product_id, // sadece mock modunda var
      disclaimer: "Bu bir örnek sonuçtur (API'ye ulaşılamadı).",
    };
  }
}
window.PhyraMed.identifyImage = identifyImage;
