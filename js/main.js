// PhyraMed — ortak arayüz mantığı
// Navbar, footer ve chatbot HTML'i tek yerden (bu dosyadan) enjekte edilir.
// Yeni bir menü linki eklemek istersen SADECE navHTML() fonksiyonunu değiştir.
//
// Her sayfa <body> etiketine data-home / data-profil attribute'ları koyarak
// (klasör derinliğine göre) doğru göreli yolu bildiriyor:
//   index.html   → data-home="index.html"     data-profil="pages/profil.html"
//   pages/*.html → data-home="../index.html"   data-profil="profil.html"
//
// Not: data.js gibi bu dosya da klasik script + window.PhyraMed nesnesi
// kullanıyor, ES modülü (export/import) değil — ES modülleri file:// (yani
// dosyayı çift tıklayıp açma) üzerinden çalışmıyor, projeyi sunucu olmadan
// açılabilir tutmak için bu yöntemde kaldık.

window.PhyraMed = window.PhyraMed || {};

/**
 * Kullanıcıdan/veritabanından gelen metni innerHTML şablonlarına
 * güvenle basmak için kaçışlama (escaping) yardımcı fonksiyonu.
 * Mock veri için risk yok, ama gerçek API verisi geldiğinde
 * (ör. bir kullanıcı adı veya yorum metninde <script> olması ihtimali)
 * XSS'e karşı koruma sağlar. Metin alanlarını innerHTML'e basmadan önce
 * MUTLAKA bu fonksiyondan geçir.
 */
function escapeHTML(value) {
  const div = document.createElement("div");
  div.textContent = value ?? "";
  return div.innerHTML;
}
window.PhyraMed.escapeHTML = escapeHTML;

/**
 * Basit iskelet (skeleton) yükleyici — gerçek API bağlanınca fetch()
 * network gecikmesi sırasında boş ekran yerine bunu göster.
 */
function renderSkeletons(container, count, extraClass) {
  container.innerHTML = "";
  for (let i = 0; i < count; i++) {
    const el = document.createElement("div");
    el.className = `card skeleton ${extraClass}`;
    container.appendChild(el);
  }
}
window.PhyraMed.renderSkeletons = renderSkeletons;

function navHTML(home, profil) {
  return `
    <div class="navbar-inner">
      <a href="${home}" class="brand">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C8 7 5 10.5 5 14.5A7 7 0 0 0 19 14.5C19 10.5 16 7 12 2z"/></svg>
        PhyraMed
      </a>
      <nav class="nav-links">
        <a href="${profil}" class="nav-cta">Hesabım</a>
      </nav>
      <button class="menu-btn" aria-label="Menüyü aç" aria-expanded="false">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
      </button>
    </div>
    <nav class="mobile-menu">
      <a href="${home}">Keşfet</a>
      <a href="${profil}">Hesabım</a>
    </nav>
  `;
}

const FOOTER_HTML = `
  <p class="footer-disclaimer">
    <strong>Not:</strong> PhyraMed bir tıbbi teşhis veya tedavi platformu değildir; bilimsel kaynaklara dayalı
    bilgilendirme ve farkındalık amacı taşır. Herhangi bir takviye kullanmadan önce mutlaka bir sağlık
    profesyoneline danışın.
  </p>
  <div class="footer-inner">
    <span><strong>PhyraMed</strong> — AI destekli bitkisel içerik ve takviye kanıt platformu</span>
    <span>Takım 137 · YZTA Bootcamp 2026</span>
  </div>
`;

const CHATBOT_HTML = `
  <div class="chat-panel">
    <div class="chat-header">
      <span>Phyra Asistan</span>
      <button aria-label="Sohbeti kapat">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12"/></svg>
      </button>
    </div>
    <div class="chat-body"></div>
    <div class="quick-replies"></div>
    <form class="chat-form">
      <input type="text" placeholder="Bir şey sor..." />
      <button type="submit" aria-label="Gönder">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2 11 13M22 2l-7 20-4-9-9-4z"/></svg>
      </button>
    </form>
  </div>
  <button class="mascot-btn" aria-label="Phyra asistanı ile sohbet et">
    <svg width="40" height="40" viewBox="0 0 100 100" fill="none">
      <circle cx="50" cy="55" r="30" fill="#3F6B44" />
      <path d="M50 25c10 0 18 8 18 18-10 0-18-8-18-18z" fill="#2E7D4F" />
      <path d="M50 25c-10 0-18 8-18 18 10 0 18-8 18-18z" fill="#6B9A68" />
      <circle cx="41" cy="52" r="4" fill="#F3F6F1" />
      <circle cx="59" cy="52" r="4" fill="#F3F6F1" />
      <path class="mascot-mouth" d="M42 63 Q50 68 58 63" stroke="#F3F6F1" stroke-width="3" stroke-linecap="round" fill="none" />
    </svg>
  </button>
`;

document.addEventListener("DOMContentLoaded", () => {
  injectSharedMarkup();
  initMobileMenu();
  initChatbot();
  initNavbarScroll();
});

function injectSharedMarkup() {
  const home = document.body.dataset.home || "index.html";
  const profil = document.body.dataset.profil || "pages/profil.html";

  const header = document.querySelector(".navbar");
  if (header) header.innerHTML = navHTML(home, profil);

  const footer = document.querySelector(".site-footer");
  if (footer) footer.innerHTML = FOOTER_HTML;

  const chatbot = document.querySelector(".chatbot-wrap");
  if (chatbot) chatbot.innerHTML = CHATBOT_HTML;
}

function initNavbarScroll() {
  const nav = document.querySelector(".navbar");
  if (!nav) return;
  const onScroll = () => nav.classList.toggle("scrolled", window.scrollY > 8);
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });
}

function initMobileMenu() {
  const btn = document.querySelector(".menu-btn");
  const menu = document.querySelector(".mobile-menu");
  if (!btn || !menu) return;

  btn.addEventListener("click", () => {
    const isOpen = menu.classList.toggle("open");
    btn.setAttribute("aria-expanded", String(isOpen));
    if (isOpen) {
      const firstLink = menu.querySelector("a");
      firstLink?.focus();
    }
  });

  menu.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      menu.classList.remove("open");
      btn.setAttribute("aria-expanded", "false");
      btn.focus();
    }
  });
}

const QUICK_REPLIES = [
  "Demir eksikliğine ne önerirsin?",
  "Bu bitkinin yan etkileri neler?",
  "Kanıt seviyesi ne demek?",
];

function initChatbot() {
  const root = document.querySelector(".chatbot-wrap");
  if (!root) return;

  const mascotBtn = root.querySelector(".mascot-btn");
  const panel = root.querySelector(".chat-panel");
  const body = root.querySelector(".chat-body");
  const form = root.querySelector(".chat-form");
  const input = root.querySelector(".chat-form input");
  const closeBtn = root.querySelector(".chat-header button");
  const quickWrap = root.querySelector(".quick-replies");

  QUICK_REPLIES.forEach((q) => {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = q;
    b.addEventListener("click", () => send(q));
    quickWrap.appendChild(b);
  });

  addBubble("bot", "Merhaba! Ben Phyra 🌿 Bitkisel takviyeler hakkında merak ettiğin bir şey var mı? (Bilgilerim bilgilendirme amaçlıdır, tıbbi tavsiye yerine geçmez.)");

  mascotBtn.addEventListener("click", () => {
    panel.classList.toggle("open");
  });
  closeBtn.addEventListener("click", () => panel.classList.remove("open"));

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    send(input.value);
    input.value = "";
  });

  function send(text) {
    if (!text || !text.trim()) return;
    addBubble("user", text);
    setMood("talking");
    // NOT: Burası ileride gerçek chatbot API'sine (ai/dev5-melike branch'i) bağlanacak.
    setTimeout(() => {
      addBubble("bot", "Bu konudaki bilimsel kanıt özetini hazırlıyorum, birazdan gerçek API'ye bağlanacağım 🙂");
      setMood("happy");
      setTimeout(() => setMood("idle"), 1200);
    }, 700);
  }

  function addBubble(from, text) {
    const div = document.createElement("div");
    div.className = `bubble ${from}`;
    div.textContent = text;
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
  }

  function setMood(mood) {
    mascotBtn.classList.remove("talking", "happy");
    if (mood !== "idle") mascotBtn.classList.add(mood);
  }
}
