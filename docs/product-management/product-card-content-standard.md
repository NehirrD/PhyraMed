# PhyraMed Ürün Kartı İçerik Standardı

**İlgili Jira kaydı:** SCRUM-29  
**Sorumlu rol:** Product Owner  
**Kapsam:** MVP ürün-kullanım iddiası kayıtları

## 1. Amaç

Bu doküman, PhyraMed ürün kartlarında ve ürün detay ekranlarında gösterilecek bilgilerin anlamını, kullanıcıya sunulan başlıklarını ve eksik bilgi davranışlarını tanımlar.

Amaç; veri seti, backend API ve frontend arayüzünde aynı ürün dilinin kullanılmasını sağlamak, bilimsel bilgi ile kişisel görüşün karıştırılmasını önlemek ve sağlık içeriklerinin teşhis, tedavi veya kesin sonuç vaadine dönüşmesini engellemektir.

## 2. Temel Ürün Kararı

PhyraMed’de bilimsel değerlendirme ürünün tamamına değil, **ürün + kullanım iddiası** birleşimine bağlıdır.

Bu nedenle aynı ürünün farklı kullanım iddiaları farklı bilimsel özetlere, kanıt durumlarına, risklere, etkileşimlere ve kaynaklara sahip olabilir.

## 3. Bağlayıcı Terminoloji ve Alan Eşlemesi

| Veri alanı | Kullanıcıya gösterilecek başlık | Ürün anlamı |
|---|---|---|
| `product_name_tr` | Ürün adı | Ürünün Türkçe adı |
| `product_type` | Ürün türü | Bitkisel ürün, vitamin, mineral veya takviye türü |
| `usage_purpose` | Kullanım amacı | Ürünün hangi destek alanı kapsamında incelendiğinin kısa ve nötr açıklaması |
| `claim` | İncelenen kullanım iddiası | Bilimsel değerlendirmeye konu olan belirli iddia |
| `evidence_summary` | Bilimsel kanıt özeti | İlgili iddiaya yönelik bulguların dengeli ve anlaşılır özeti |
| `evidence_level` | Kanıt durumu / Kanıt seviyesi | Değerlendirmenin mevcut durumu veya tamamlandıysa seviyesi |
| `risk_summary` | Riskler ve olası yan etkiler | Bilinen veya olası risk ve yan etki bilgileri |
| `interaction_summary` | Etkileşimler ve önemli uyarılar | İlaç, takviye, özel durum veya kullanım biçimiyle ilgili önemli uyarılar |
| `review_status` | İçerik inceleme durumu | Kaydın içerik kontrolü ve yayıma hazır olma durumu |

### Terminoloji kararı

- Kullanıcı arayüzünde **“Uzman görüşü”**, **“doktor görüşü”** veya **“uzman/doktor görüşü özeti”** ifadeleri kullanılmaz.
- Bağlayıcı ürün terimi **“Bilimsel kanıt özeti”**dir.
- Bilimsel kanıt özeti kişisel görüş değil, bilimsel ve resmî kaynaklara dayanan içerik özetidir.
- Teknik uygulamada bulunan `expert_opinion_summary` adlandırması ürün terminolojisiyle uyumlu değildir; entegrasyon sırasında `evidence_summary` anlamıyla eşleştirilmelidir.

## 4. Kullanıcı Arayüzünde Gösterim

### 4.1 Ürün liste kartı

Ürün liste kartında en az aşağıdaki bilgiler gösterilir:

- Ürün adı
- Ürün türü
- Kullanım amacı

Liste kartında ayrıntılı bilimsel özet, risk ve etkileşim metinlerinin tamamının gösterilmesi zorunlu değildir. Bu içerikler ürün detayında sunulur.

### 4.2 Ürün detay ekranı

Ürün detay ekranında aşağıdaki bölümler birbirinden ayrı gösterilir:

1. Ürün adı ve ürün türü
2. Kullanım amacı
3. İncelenen kullanım iddiası
4. Kanıt durumu veya kanıt seviyesi
5. Bilimsel kanıt özeti
6. Riskler ve olası yan etkiler
7. Etkileşimler ve önemli uyarılar
8. Bilimsel ve resmî kaynaklar
9. Tıbbi bilgilendirme ve sorumluluk uyarısı

Risk ve etkileşim alanları tek metin altında birleştirilmez. Etkililik ile güvenlilik ayrı değerlendirilir.

## 5. Kanıt ve İnceleme Durumu Kuralları

- `evidence_level = Bekliyor` olduğunda Güçlü, Orta veya Zayıf etiketi gösterilmez.
- Bu durumda kullanıcıya **“Kanıt değerlendirmesi devam ediyor”** ifadesi gösterilir.
- `Değerlendirilemedi`, bir kanıt seviyesi değildir ve **“Mevcut bilgilerle değerlendirme yapılamadı”** şeklinde açıklanır.
- Güçlü, Orta veya Zayıf etiketi tek başına gösterilmez; yanında kısa bilimsel özet ve temel sınırlılık bulunur.
- `review_status = Taslak` olan kayıt, onaylanmış sağlık içeriği gibi sunulmaz. Geliştirme veya demo ortamında kullanılıyorsa taslak niteliği ekip tarafından bilinmeli ve ürün kabulünde onaylı içerik sayılmamalıdır.

## 6. Eksik Bilgi Davranışı

Eksik alanlar boş bırakılmaz ve bilgi yokluğu güvenlilik veya etkililik sonucu gibi yorumlanmaz.

- Bilimsel özet eksikse: **“Bilimsel kanıt özeti henüz hazırlanmadı.”**
- Risk bilgisi eksikse: **“Bu kayıt için risk bilgisi henüz tamamlanmadı. Bilgi bulunmaması ürünün risksiz olduğu anlamına gelmez.”**
- Etkileşim bilgisi eksikse: **“Bu kayıt için etkileşim bilgisi henüz tamamlanmadı. İlaç veya başka takviye kullanan kişilerin sağlık profesyoneline danışması gerekir.”**
- Kaynak eksikse: İçerik doğrulanmış veya güvenilir olarak etiketlenmez.

## 7. Sağlık Dili Kuralları

Ürün metinleri:

- Teşhis koymaz.
- Tedavi veya doz önermez.
- Kullanıcının ürünü kullanması gerektiğini söylemez.
- Kesin fayda, kesin güvenlik veya garanti iddiası içermez.
- İlaç bırakma veya değiştirme yönlendirmesi yapmaz.
- Yeterli bilgi yoksa tahminde bulunmaz.
- Kullanıcı yorumlarını bilimsel kanıt olarak sunmaz.

“Kullanım amacı” alanı ürün önerisi değildir; yalnızca kaydın hangi iddia kapsamında incelendiğini açıklar.

## 8. MVP Veri Seti PO Kontrol Sonucu

`data/phyramed_mvp_seed_dataset_v1.xlsx` dosyası üzerinde yapılan yapısal kontrol sonucu:

- 18/18 kayıtta `usage_purpose` alanı doludur.
- 18/18 kayıtta `evidence_summary` alanı doludur.
- 18/18 kayıtta `risk_summary` alanı doludur.
- 18/18 kayıtta `interaction_summary` alanı doludur.
- 18/18 kullanım iddiası en az bir kaynakla ilişkilidir.
- Toplam 19 kaynak kaydı bulunmaktadır; CLM-003 iki kaynakla, diğer kullanım iddiaları en az bir kaynakla ilişkilidir.
- 18/18 kaydın `evidence_level` değeri `Bekliyor` durumundadır.
- 18/18 kaydın `review_status` değeri `Taslak` durumundadır.

### PO değerlendirmesi

Veri seti, ürün kartı alanlarının **yapısal bütünlüğü** açısından entegrasyona uygundur. Ancak kayıtların tamamı `Taslak`, kanıt değerlendirmelerinin tamamı `Bekliyor` olduğu için içerikler bilimsel olarak nihai onay almış kabul edilmez.

## 9. Ekipler Arası Uygulama Kararı

- Veri ekibi için kanonik alan: `evidence_summary`
- Backend API’nin taşıması gereken ürün anlamı: bilimsel kanıt özeti
- Frontend kullanıcı etiketi: **Bilimsel kanıt özeti**
- `expert_opinion_summary` kullanıcıya gösterilecek ürün terimi değildir.
- Risk ve etkileşim ayrı API/arayüz alanları olarak korunur.
- Kanıt seviyesi ürün yerine kullanım iddiasıyla ilişkilendirilir.

Teknik alan adlarının ve veri modelinin nihai eşleştirmesi SCRUM-30 kapsamındaki kaynak/güvenilirlik ve veri modeli çalışmasıyla birlikte doğrulanacaktır.

## 10. SCRUM-29 Tamamlanma Koşulları

SCRUM-29 aşağıdaki koşullar birlikte sağlandığında tamamlanır:

- Bu içerik standardı GitHub üzerinden incelemeye açılmıştır.
- Ürün terminolojisi ve alan eşlemesi ekip tarafından erişilebilir durumdadır.
- 18 MVP kaydının temel alan doluluk kontrolü kayıt altına alınmıştır.
- Frontend’de “Uzman/doktor görüşü” yerine “Bilimsel kanıt özeti” kullanılacağı netleştirilmiştir.
- İlgili doküman `develop` branch’ine merge edilmiştir.
- Jira kaydına PR/merge kanıtı ve kısa kapanış özeti eklenmiştir.
