# Takım 137

## Ürün İle İlgili Bilgiler

### Takım Elemanları

* Enes Tüysüz: Product Owner - Developer
* Nehir Doğan: Scrum Master - Developer
* Melike Şenses: Developer
* Alper Güler: Developer
* Ahmet Kılıç: Developer

### Ürün İsmi - PhyraMed

### Ürün Açıklaması

* PhyraMed, bitkisel takviye ve doğal ürünler hakkında kanıta dayalı bilgi sunan AI destekli bir platformdur. Kullanıcılar ihtiyaçlarına (örn. demir eksikliği, kilo verme) göre bitkisel ürünleri keşfedebilir; her ürün için bilimsel kanıt seviyesi, uzman görüşleri, olası riskler ve yan etkiler şeffaf bir şekilde sunulur. Platform ayrıca kullanıcı yorumlarını yapay zeka ile toplu olarak analiz ederek en sık bildirilen yan etki ve deneyimleri özetler, tanınmayan bitkileri fotoğraf yoluyla tanımlar.

### Ürün Özellikleri

* Kategori/ihtiyaç bazlı bitkisel ürün listeleme (demir eksikliği, uyku sorunu, kilo verme vb.)
* Her ürün için kanıt seviyesi rozeti (Yüksek / Orta / Sadece geleneksel kullanım)
* Uzman ve doktor görüşlerinin sunulması
* Olası risk ve yan etki bilgilendirmesi
* Fotoğraf yükleyerek bitki/ürün tanıma
* Kullanıcı yorumlarının AI ile toplu sentezi (en sık bildirilen yan etki, olumlu/olumsuz dağılım)
* Ürünler arası karşılaştırma
* Sohbet tabanlı AI asistan - chatbot

### Hedef Kitle

* Bitkisel takviye satın almadan önce araştırma yapan tüketiciler
* Sağlıklı yaşam ve beslenme takipçileri
* Doğada karşılaştığı bitkiyi tanımak isteyen kullanıcılar
* Online alışveriş yorumlarının güvenilirliğini sorgulayan kullanıcılar
* 18 - 60 yaş arası, sağlık/beslenme bilincine sahip kullanıcılar

### Product Backlog URL



> **Not:** Bu platform tıbbi tavsiye sunmaz, yalnızca bilgilendirme amaçlıdır. Kullanıcılar herhangi bir sağlık kararı öncesinde doktorlarına danışmalıdır.

---

## Kurulum ve Çalıştırma

### Gereksinimler

- Python 3.9+
- PostgreSQL (Supabase)
- Groq API Key

### Adımlar

1. Depoyu klonlayın:
```bash
git clone https://github.com/NehirrD/PhyraMed.git
cd PhyraMed
```

2. Gereksinimleri yükleyin:
```bash
pip install -r requirements.txt
```

3. Ortam değişkenlerini ayarlayın (.env dosyasını düzenleyin):
```bash
cp .env.example .env
# .env dosyasına DATABASE_URL ve GROQ_API_KEY ekleyin
```

4. RAG indeksini oluşturun:
```bash
cd ai
python -m poc.rag.indexer
```

5. Backend'i başlatın:
```bash
cd ..
uvicorn main:app --reload
```

### API Endpoint'leri

- `GET /` - API durumu
- `GET /products` - Tüm ürünleri listele
- `GET /products/{id}` - Ürün detayı
- `POST /products` - Yeni ürün ekle
- `POST /chat` - AI chatbot
- `POST /products/identify` - Görsel tanıma
- `GET /categories` - Kategoriler
- `GET /risks` - Riskler
- `GET /sources` - Kaynaklar
- `GET /interactions` - Etkileşimler
- `GET /comments` - Yorumlar

### Proje Yapısı

```
PhyraMed/
├── ai/                      # AI modülleri
│   ├── poc/                # Proof of Concept kodları
│   │   ├── rag/            # RAG sistemi
│   │   ├── product_db.py   # Backend API entegrasyonu
│   │   ├── chatbot.py      # Chatbot mantığı
│   │   └── vision.py       # Görsel tanıma
│   ├── identify.py         # Backend görsel tanıma
│   └── chatbot.py          # Backend chatbot
├── routers/                # FastAPI router'ları
│   ├── product.py
│   ├── chat.py
│   ├── category.py
│   └── ...
├── models.py               # SQLAlchemy modelleri
├── database.py             # Veritabanı bağlantısı
├── schemas.py              # Pydantic şemaları
└── main.py                 # Ana FastAPI uygulaması
```
