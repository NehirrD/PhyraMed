<img width="1400" height="482" alt="phyramed-brand-header" src="https://github.com/user-attachments/assets/25827c45-0d7d-4f86-aa02-d899177b8212" />

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

### Proje Bağlantıları

- **Product Backlog ve Sprint Board:**  
  [PhyraMed Jira Sprint Board](https://grup137.atlassian.net/jira/software/projects/SCRUM/boards/1)

- **Product Backlog Dokümanı:**  
  [Product Backlog](docs/product-management/product-backlog.md)

- **Bilimsel Kanıt Sınıflandırma Kriterleri:**  
  [Bilimsel Kanıt Sınıflandırması](docs/product-management/evidence-classification.md)

- **MVP Veri Seti:**  
  [PhyraMed MVP Seed Dataset](data/phyramed_mvp_seed_dataset_v1.xlsx)



> **Not:** Bu platform tıbbi tavsiye sunmaz, yalnızca bilgilendirme amaçlıdır. Kullanıcılar herhangi bir sağlık kararı öncesinde doktorlarına danışmalıdır.

## Sprint 1

**Sprint Tarihleri:** 19 Haziran – 5 Temmuz 2026

## Sprint Notları

Sprint 1 kapsamında ürün vizyonunun ve MVP kapsamının netleştirilmesi, Product Backlog'un oluşturulması, ilk veri setinin hazırlanması, teknik proje iskeletlerinin kurulması ve yapay zekâ özelliklerine yönelik araştırma çalışmalarının başlatılması hedeflenmiştir.

Product Owner çalışmaları kapsamında:

- Ürün vizyonu, kapsamı ve hedef kitlesi tanımlanmıştır.
- PhyraMed'in altı ana kategorisi belirlenmiştir.
- Her kategori için üç ürün olacak şekilde toplam 18 ürün-kullanım iddiasından oluşan ilk MVP veri seti hazırlanmıştır.
- PB-01 ile PB-10 arasındaki Product Backlog maddeleri oluşturulmuştur.
- User story'ler, kabul kriterleri, P0 öncelikleri ve hedef sprintler Jira üzerinde tanımlanmıştır.
- Güçlü, Orta ve Zayıf bilimsel kanıt seviyelerine ait sınıflandırma kriterleri hazırlanmıştır.

Takımın frontend, backend, veri entegrasyonu ve yapay zekâ araştırma görevleri Jira Sprint Board üzerinden takip edilmiştir. Sprint 1 son durumu, aşağıdaki Sprint Board Update ve Ürün Durumu bölümlerinde ekran görüntüleriyle belgelenmiştir.

## Backlog Düzeni ve Story Seçimleri

Sprint 1 backlog düzeni, PhyraMed MVP'sinin önce ürün temelini netleştirecek ve sonraki sprintlerde geliştirilecek özelliklere zemin hazırlayacak şekilde oluşturulmuştur.

Product Owner tarafında ilk olarak ürün vizyonu, hedef kitle ve MVP kapsamı tanımlanmıştır. Ardından ürünün veri yapısını ve kullanıcı akışını desteklemek amacıyla altı ana kategori belirlenmiş, her kategori için üç ürün olacak şekilde ilk MVP veri seti hazırlanmıştır.

Product Backlog, PB-01 ile PB-10 arasında ayrı user story kartları olarak düzenlenmiştir. Bu story'ler kullanıcı ihtiyacına göre yazılmış, her biri için kabul kriterleri oluşturulmuş, öncelik seviyesi P0 olarak belirlenmiş ve hedef sprint dağılımı yapılmıştır.

Sprint 1 için temel MVP akışını temsil eden aşağıdaki story'ler seçilmiştir:

- PB-01: Kullanıcı ana kategorileri görüntüleyebilmeli
- PB-02: Kullanıcı seçtiği kategoriye ait ürünleri görüntüleyebilmeli
- PB-03: Kullanıcı ürünün temel detaylarını görüntüleyebilmeli
- PB-07: Kullanıcı tıbbi bilgilendirme ve sorumluluk uyarısını görebilmeli

Bu story'lerin tamamlanması, ilgili frontend/backend geliştirme görevlerinin kabul kriterlerini karşılamasına bağlıdır. Bu nedenle Product Backlog kartlarının oluşturulması ile ürün özelliklerinin geliştirilmesi ayrı takip edilmektedir.

Sprint 2'ye planlanan story'ler ise bilimsel kanıt detayları, kaynak gösterimi, risk/etkileşim bilgileri, görsel tanıma, yorum analizi ve chatbot özellikleri üzerine ayrılmıştır:

- PB-04: Kullanıcı kullanım iddiasının bilimsel kanıt seviyesini görebilmeli
- PB-05: Kullanıcı bilimsel ve resmî kaynakları görüntüleyebilmeli
- PB-06: Kullanıcı risk, yan etki ve olası etkileşim bilgilerini görüntüleyebilmeli
- PB-08: Kullanıcı fotoğraf yükleyerek bitkiyi tanımlayabilmeli
- PB-09: Kullanıcı ürün yorumlarının toplu analizini görüntüleyebilmeli
- PB-10: Kullanıcı chatbot üzerinden ürün ve takviyeler hakkında bilgi alabilmeli

Story'ler Jira üzerinde `Yapılacaklar`, `Devam Ediyor`, `İncelemede`, `Tamamlandı` ve `Engellendi` durumlarıyla takip edilmiştir. Sprint 1'de story point ataması kullanılmadığı için ilerleme, görev durumları ve sprint çıktıları üzerinden değerlendirilmiştir.

## Sprint Puanlaması

Sprint 1 görevlerine story point ataması yapılmadığı için sprint ilerlemesi puan yerine Jira üzerindeki görev durumları üzerinden takip edilmiştir.

Story point kullanımına ilişkin kararın sonraki Sprint Planning çalışmasında ekip tarafından ortak şekilde değerlendirilmesi planlanmaktadır.

## Daily Scrum

Ekip içi günlük iletişim, görev güncellemeleri ve karşılaşılan engeller ağırlıklı olarak Slack üzerinden paylaşılmıştır.

Görevlerin resmî durumları Jira Sprint Board üzerinden takip edilmiş ve Sprint 1 son durumu README’ye eklenen board ekran görüntüleriyle belgelenmiştir.

## Product Backlog URL

[PhyraMed Jira Sprint Board](https://grup137.atlassian.net/jira/software/projects/SCRUM/boards/1)

## Sprint Board Update

Sprint 1 görevleri Jira Sprint Board üzerinden takip edilmiştir.

Aşağıda Sprint 1 sonunda güncellenen Jira Sprint Board ekran görüntüleri yer almaktadır.

![Sprint 1 Jira Board - Genel Durum](<img width="1439" height="716" alt="sprint-board-1" src="https://github.com/user-attachments/assets/fccba1ff-8c79-4e11-a13f-f4abdc94e938" />)

![Sprint 1 Jira Board - Devam Eden ve AI Görevleri](<img width="1442" height="361" alt="sprint-board-2" src="https://github.com/user-attachments/assets/12901870-1c39-4ba5-adec-c0e09c2b4636" />)

## Ürün Durumu: Ekran görüntüleri

Sprint 1 kapsamında ürünün temel bilgi mimarisi, veri yapısı ve ilk arayüz taslağı hazırlanmıştır.

Frontend tarafında PhyraMed ana sayfa taslağı, kategori kartları, kanıt seviyesi etiketleri ve temel ürün kartı görünümü oluşturulmuştur. Bu ekran Sprint 1 için statik/taslak ürün arayüzü olarak değerlendirilmiştir.

![Sprint 1 Frontend Taslak Ekranı](<img width="1207" height="901" alt="frontend-homepage" src="https://github.com/user-attachments/assets/c77b790b-e492-45d1-8def-af69cc7d8cc4" />)

Backend tarafında FastAPI proje iskeleti, temel veri modelleri ve veritabanı şeması hazırlanmıştır.

![Sprint 1 Veritabanı Şeması](<img width="1400" height="704" alt="database-diagram" src="https://github.com/user-attachments/assets/49ae19ef-8f5f-4938-8c60-140f63d95ecf" />)

Sprint 1 içerisinde doğrulanmış olarak tamamlanan veya hazırlanan temel çıktılar şunlardır:

- Ürün vizyonu, ürün kapsamı ve hedef kitle tanımlanmıştır.
- PhyraMed'in altı ana kategorisi belirlenmiştir.
- Toplam 18 ürün-kullanım iddiasından oluşan ilk MVP veri seti hazırlanmıştır.
- Veri seti GitHub reposuna eklenmiştir.
- PB-01 ile PB-10 arasındaki Product Backlog maddeleri ve kabul kriterleri oluşturulmuştur.
- Product Backlog dokümanı GitHub reposuna eklenmiştir.
- Bilimsel kanıt seviyesi sınıflandırma kriterleri hazırlanmıştır.
- Kanıt sınıflandırma dokümanı GitHub reposuna eklenmiştir.
- GitHub reposu ve Jira Sprint Board oluşturulmuştur.
- Backend proje iskeleti ve veritabanı şeması hazırlanmıştır.
- Frontend ana sayfa/kategori ekranı için ilk taslak arayüz hazırlanmıştır.

CRUD endpoint'leri, seed data aktarımı, API dokümantasyonu, backend-frontend entegrasyonu ve AI POC çalışmalarının nihai durumu Sprint 1 kapanışındaki Jira durumuna göre takip edilmektedir.

## Sprint Review

Sprint Review, Sprint 1 sonunda takımın geliştirdiği çıktıların sprint hedefleri ve ürün vizyonuyla karşılaştırılması amacıyla gerçekleştirilecektir.

Review sırasında aşağıdaki başlıklar değerlendirilecektir:

- Sprint hedeflerine ulaşılma durumu
- Tamamlanan teknik ve ürün çıktıları
- Devam eden veya Sprint 2'ye aktarılacak görevler
- Geliştirilen çıktıların ürün vizyonuyla uyumu
- Tespit edilen ürün ve teknik eksikler

Sprint Review tamamlandıktan sonra toplantıda alınan kararlar bu bölüme eklenecektir.

## Sprint Review Katılımcıları

Nehir Doğan
Melike Şenses
Enes Tüysüz
Ahmet Kılıç
Alper Güler

## Sprint Retrospective

Retrospective kapsamında aşağıdaki konuların değerlendirilmiştir.

- Ekip içi iletişim ve koordinasyon
- Görev dağılımının etkinliği
- Sprint içerisinde iyi ilerleyen çalışmalar
- Geciken veya tamamlanamayan görevlerin nedenleri
- Karşılaşılan engeller
- Sprint 2 için uygulanacak iyileştirmeler

**Alınan kararlar:**
Takım içindeki görev dağılımıyla ilgili düzenleme yapılması kararı alınmıştır.
Tahmin puanları (story point) kullanımının Sprint 2 planlamasında yeniden değerlendirilmesine ve sprint planlama toplantılarında developer'lardan geri bildirim alınmasına karar verilmiştir.
Unit test'ler için ayrılan efor/saatin artırılması gerektiği kararlaştırılmıştır.

Sprint 2
--------

**Sprint Tarihleri:** 6 Temmuz – 19 Temmuz 2026 

### Sprint Notları

Sprint 2 kapsamında Sprint 1'de kurulan temel üzerine; ürün kartı detaylarının zenginleştirilmesi, kaynak/güvenilirlik etiketleme mantığının veri modeline işlenmesi, frontend-backend entegrasyonunun ilerletilmesi ve yapay zekâ destekli özelliklerin (görsel tanıma, yorum analizi, chatbot) ilk çalışır versiyonlarının oluşturulması hedeflenmiştir.

Sprint 1 Retrospective kararları doğrultusunda backlog güncellenmiş, önceliklendirilmiş ve her ürün kartı için "kullanım amacı / risk-yan etki / uzman görüşü" alanları detaylandırılmıştır.

### Backlog Düzeni ve Story Seçimleri

Sprint 2 backlog'u, Sprint 1 Retrospective çıktılarına göre gözden geçirilerek güncellenmiş ve önceliklendirilmiştir (SCRUM-28). Sprint 1'de tamamlanan **PB-01, PB-02, PB-03, PB-07** story'leri Sprint 2'de inceleme (review) sürecine alınmıştır.

Sprint 2 için asıl odak, Sprint 1 README'sinde Sprint 2'ye planlanmış olan story'ler olmuştur:

- **PB-04** – Kullanıcı kullanım iddiasının bilimsel kanıt seviyesini görebilmeli
- **PB-05** – Kullanıcı bilimsel ve resmî kaynakları görüntüleyebilmeli
- **PB-06** – Kullanıcı risk, yan etki ve olası etkileşim bilgilerini görüntüleyebilmeli
- **PB-08** – Kullanıcı fotoğraf yükleyerek bitkiyi tanımlayabilmeli
- **PB-09** – Kullanıcı ürün yorumlarının toplu analizini görüntüleyebilmeli
- **PB-10** – Kullanıcı chatbot üzerinden ürün ve takviyeler hakkında bilgi alabilmeli

Bu story'lere ait alt görevler (task) Dev1-Dev5, PO ve SM etiketleriyle Jira Sprint Board üzerinde takip edilmiştir. Her ürün kartı için "kullanım amacı / risk-yan etki / uzman görüşü" detaylandırma çalışması tamamlanmıştır.

### Daily Scrum

Ekip içi günlük iletişim, görev güncellemeleri ve karşılaşılan engeller Sprint 1'de olduğu gibi Slack üzerinden paylaşılmaya devam edilmiştir. Görevlerin resmî durumları Jira Sprint Board üzerinden takip edilmiş ve Sprint 2 son durumu README'ye eklenen board ekran görüntüleriyle belgelenmiştir.

### Product Backlog URL

[PhyraMed Jira Sprint Board](#)

### Sprint Board Update
<img width="1429" height="699" alt="image" src="https://github.com/user-attachments/assets/abb9bfbe-093c-48f5-9a39-8e617a0444f4" />

<img width="1441" height="711" alt="image" src="https://github.com/user-attachments/assets/d322485b-eaef-4f9d-b1be-742c0b412f6e" />

### Ürün Durumu: Ekran görüntüleri
<img width="1207" height="901" alt="image" src="https://github.com/user-attachments/assets/59e8fd0e-b2ce-4e61-bcee-2e621255b559" />


Sprint 2 kapsamında frontend-backend entegrasyonu ilerletilmiştir.

### Sprint Review

Sprint Review, Sprint 2 sonunda takımın geliştirdiği çıktıların sprint hedefleri ve ürün vizyonuyla karşılaştırılması amacıyla gerçekleştirilmiştir. Toplantıda backend tarafında API dokümantasyonu ve yorum toplu analizi modülünün ilk versiyonu, frontend tarafında ortak tasarım sistemi ve sayfa geçişleri, AI tarafında ise görsel tanıma, yorum analizi ve chatbot POC'larının canlı demoları gösterilmiştir. Ekip, Sprint 2 hedeflerinin büyük bölümüne ulaşıldığını, kalan entegrasyon ve arayüz işlerinin ise Sprint 3'e net bir kapsam ile aktarılabileceğini değerlendirmiştir.

**Alınan kararlar:**

- Görsel tanıma, yorum analizi ve chatbot özelliklerinin temel/POC sürümlerinin başarıyla kurulduğu ve ürün veritabanına bağlandığı değerlendirilmiştir.
- Kaynak/güvenilirlik etiketleme mantığının veri modeline işlenmesi çalışması devam ettiği için ilgili PBI'lar Sprint 3'e aktarılmıştır.
- PB-04 ile PB-10 arasındaki story'lerin (bilimsel kanıt seviyesi, kaynak gösterimi, risk/etkileşim bilgisi, görsel tanıma arayüzü, yorum analizi arayüzü, chatbot arayüzü) frontend entegrasyonu Sprint 3 kapsamına alınmıştır.
- Çıkan ürün çıktılarının çalışmasında ve testlerinde kritik bir problem görülmemiştir.

**Sprint Review Katılımcıları:**
Nehir Doğan
Enes Tüysüz 
Ahmet Kılıç
Melike Şenses
Alper Güler

### Sprint Retrospective

- Görev dağılımının etkinliği tekrar gözden geçirilmiş, Dev2/Dev4/Dev5 arasındaki iş yükü dengesinin Sprint 3'te yeniden düzenlenmesine karar verilmiştir.
- Story point kullanımına geçiş kararı bir sonraki Sprint Planning toplantısına ertelenmiştir.
- Unit test'ler için ayrılan efor/saatin Sprint 3'te artırılması gerektiği tekrar vurgulanmıştır.
- AI özelliklerinin (chatbot, görsel tanıma, yorum analizi) entegrasyon ve doğrulama testleri için süre planlanması kararlaştırılmıştır.

