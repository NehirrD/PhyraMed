# Takım 137

## Ürün ile İlgili Bilgiler

### Takım Elemanları

- **Enes Tüysüz:** Product Owner - Developer
- **Nehir Doğan:** Scrum Master - Developer
- **Melike Şenses:** Developer
- **Alper Güler:** Developer
- **Ahmet Kılıç:** Developer

## Ürün İsmi

**PhyraMed**

## Ürün Açıklaması

PhyraMed, bitkisel takviyeler ve doğal ürünler hakkındaki kullanım iddialarını bilimsel kaynaklar doğrultusunda anlaşılır biçimde sunmayı amaçlayan, yapay zekâ destekli bir bilgilendirme platformudur.

Kullanıcılar; uyku ve dinlenme, stres ve zihinsel iyi oluş, sindirim ve bağırsak sağlığı, bağışıklık desteği, enerji ve yorgunluk ile cilt, saç ve tırnak desteği kategorilerindeki bitki ve takviyeleri inceleyebilir.

Platformda her ürün-kullanım iddiası için bilimsel kanıt seviyesi, kısa bilimsel özet, ilgili kaynaklar, temel riskler, olası yan etkiler ve etkileşim bilgilerinin sunulması hedeflenmektedir.

PhyraMed ayrıca fotoğraf yükleyerek olası bitki tanıma, kullanıcı yorumlarının yapay zekâ ile toplu analizi ve sohbet tabanlı bilgi erişimi özelliklerini kapsamaktadır.

## Ürün Özellikleri

- Altı ana kategori üzerinden bitki ve takviyeleri keşfetme
- Seçilen kategoriye ait ürünleri listeleme
- Ürünlerin temel bilgilerini ve kullanım iddialarını görüntüleme
- Her ürün-kullanım iddiası için bilimsel kanıt seviyesini görüntüleme:
  - Güçlü
  - Orta
  - Zayıf
- Bilimsel ve resmî kaynakları görüntüleme
- Risk, yan etki ve etkileşim bilgilerini görüntüleme
- Tıbbi bilgilendirme ve sorumluluk uyarısı
- Fotoğraf yükleyerek olası bitki tanıma
- Kullanıcı yorumlarının yapay zekâ ile toplu analizi
- Sohbet tabanlı yapay zekâ asistanı

## Hedef Kitle

- Bitkisel takviye veya doğal ürün satın almadan önce araştırma yapan kullanıcılar
- Bilimsel kanıtlarla pazarlama iddialarını ayırt etmek isteyen kullanıcılar
- Sağlıklı yaşam ve beslenme konularıyla ilgilenen kullanıcılar
- Online ürün yorumlarını daha kolay değerlendirmek isteyen kullanıcılar
- Karşılaştığı bir bitkiyi fotoğraf yoluyla tanımak isteyen kullanıcılar
- Güvenilir ve anlaşılır sağlık bilgisine ihtiyaç duyan 18 yaş ve üzeri genel kullanıcılar

## Proje Bağlantıları

- **Product Backlog ve Sprint Board:**  
  [PhyraMed Jira Sprint Board](https://grup137.atlassian.net/jira/software/projects/SCRUM/boards/1)

- **Product Backlog Dokümanı:**  
  [Product Backlog](docs/product-management/product-backlog.md)

- **Bilimsel Kanıt Sınıflandırma Kriterleri:**  
  [Bilimsel Kanıt Sınıflandırması](docs/product-management/evidence-classification.md)

- **MVP Veri Seti:**  
  [PhyraMed MVP Seed Dataset](data/phyramed_mvp_seed_dataset_v1.xlsx)

> **Tıbbi bilgilendirme:** PhyraMed teşhis koymaz, tedavi önermez ve bir sağlık profesyonelinin görüşünün yerini tutmaz. Platform yalnızca bilgilendirme amacıyla hazırlanmaktadır. Kullanıcıların sağlıkla ilgili kararlar almadan önce uygun bir sağlık profesyoneline danışması gerekir.

---

# Sprint 1

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

Takımın frontend, backend, veri entegrasyonu ve yapay zekâ araştırma görevleri Jira Sprint Board üzerinden takip edilmektedir. Teknik görevlerin nihai durumu, Sprint 1 kapanışındaki güncel Jira panosuna göre bu README içerisinde güncellenecektir.

## Backlog Dağıtma Mantığı

Sprint görevleri takım üyelerinin rol ve sorumluluk alanlarına göre dağıtılmıştır:

- **Product Owner:** Ürün vizyonu, kategori yapısı, veri seti, Product Backlog ve kanıt sınıflandırma kriterleri
- **Scrum Master / Backend:** Süreç yönetimi, GitHub ve Jira yapısı, backend iskeleti ve veritabanı şeması
- **Frontend:** Proje arayüz iskeleti, ürün detay sayfası, tasarım sistemi, routing ve ana sayfa wireframe'i
- **Backend / Entegrasyon:** Ham verinin veritabanına aktarılması, API dokümantasyonu ve ilk entegrasyon testleri
- **AI Araştırma ve POC:** Görsel tanıma, yorum analizi ve chatbot mimarisi araştırmaları

Product Backlog kapsamındaki PB-01 ile PB-10 arasındaki kullanıcı hikâyeleri ayrı Jira kartları olarak oluşturulmuştur. Story'lerin geliştirme durumu ile Product Owner tarafından oluşturulma durumu birbirinden ayrı takip edilmektedir.

## Sprint Puanlaması

Sprint 1 görevlerine story point ataması yapılmadığı için sprint ilerlemesi puan yerine Jira üzerindeki görev durumları üzerinden takip edilmiştir.

Story point kullanımına ilişkin kararın sonraki Sprint Planning çalışmasında ekip tarafından ortak şekilde değerlendirilmesi planlanmaktadır.

## Daily Scrum

Ekip içi günlük iletişim, görev güncellemeleri ve karşılaşılan engeller ağırlıklı olarak Slack üzerinden paylaşılmıştır.

Görevlerin resmî durumları Jira Sprint Board üzerinden takip edilmiştir. Takım üyelerinin sprint kapanışından önce kendi görev durumlarını güncellemesi planlanmıştır.

## Product Backlog URL

[PhyraMed Jira Sprint Board](https://grup137.atlassian.net/jira/software/projects/SCRUM/boards/1)

## Sprint Board Update

Sprint 1 boyunca görevler aşağıdaki durumlar üzerinden takip edilmiştir:

- Yapılacaklar
- Devam Ediyor
- İncelemede
- Tamamlandı
- Engellendi

Sprint 1 kapanışındaki son Jira Sprint Board ekran görüntüsü, takım üyelerinin görev durumlarını güncellemesinin ardından bu bölüme eklenecektir.

<!--
TESLİM ÖNCESİ:
Bu açıklamayı kaldırın ve son Sprint Board ekran görüntüsünü aşağıya ekleyin.

Örnek:
![Sprint 1 Jira Board](docs/sprint-1/sprint-1-board.png)
-->

## Ürün Durumu

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
- Backend proje iskeleti kurulmuştur.
- Veritabanı şeması hazırlanmıştır.

Frontend, backend, veri entegrasyonu ve yapay zekâ araştırma görevlerinin son durumu Sprint 1 kapanışında Jira panosuna göre güncellenecektir.

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

Sprint Review toplantısı tamamlandıktan sonra katılımcıların isimleri bu bölüme eklenecektir.

## Sprint Retrospective

Sprint Retrospective, Sprint 1 kapanışında Scrum Master koordinasyonunda gerçekleştirilecektir.

Retrospective kapsamında aşağıdaki konuların değerlendirilmesi planlanmaktadır:

- Ekip içi iletişim ve koordinasyon
- Görev dağılımının etkinliği
- Sprint içerisinde iyi ilerleyen çalışmalar
- Geciken veya tamamlanamayan görevlerin nedenleri
- Karşılaşılan engeller
- Sprint 2 için uygulanacak iyileştirmeler

Sprint Retrospective tamamlandıktan sonra alınan kararlar bu bölüme eklenecektir.
