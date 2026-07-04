# PhyraMed Product Backlog

Bu doküman, PhyraMed ürün vizyonunun kullanıcı ihtiyaçlarına göre önceliklendirilmiş Product Backlog maddelerini içerir.

## Öncelik Sistemi

- **P0 – MVP için zorunlu:** Ürünün temel değer önerisinin çalışması için tamamlanması gereken özellikler.
- **P1 – Ürünü farklılaştıran:** Kullanıcı deneyimini ve ürün değerini güçlendiren özellikler.
- **P2 – Zaman kalırsa:** MVP tamamlandıktan sonra değerlendirilecek geliştirmeler.

Story point ve teknik sorumlu atamaları, geliştirme ekibi tarafından Sprint Planning sırasında değerlendirilecektir.

## Backlog Özeti

| ID | Backlog Maddesi | Öncelik | Hedef Sprint |
|---|---|---|---|
| PB-01 | Ana kategorileri görüntüleme | P0 | Sprint 1 |
| PB-02 | Seçilen kategoriye ait ürünleri listeleme | P0 | Sprint 1 |
| PB-03 | Ürünün temel detaylarını görüntüleme | P0 | Sprint 1 |
| PB-04 | Bilimsel kanıt seviyesini görüntüleme | P0 | Sprint 2 |
| PB-05 | Bilimsel ve resmî kaynakları görüntüleme | P0 | Sprint 2 |
| PB-06 | Risk, yan etki ve etkileşim bilgilerini görüntüleme | P0 | Sprint 2 |
| PB-07 | Tıbbi bilgilendirme uyarısını görüntüleme | P0 | Sprint 1 |
| PB-08 | Fotoğraf yükleyerek bitkiyi tanıma | P1 | Sprint 2 |
| PB-09 | Kullanıcı yorumlarının toplu analizini görüntüleme | P1 | Sprint 2 |
| PB-10 | Chatbot üzerinden bilgi alma | P1 | Sprint 2 |

---

## PB-01 – Ana Kategorileri Görüntüleme

**User Story:**  
Bir kullanıcı olarak PhyraMed’in ana kategorilerini görüntülemek istiyorum; böylece bilgi aradığım sağlık ve destek alanını kolayca seçebileyim.

**Temel Kabul Kriterleri:**

- Altı MVP kategorisi gösterilmelidir.
- Her kategoride ad ve kısa açıklama bulunmalıdır.
- Eksik veya tekrarlanan kategori gösterilmemelidir.
- Kategori açıklamaları teşhis veya tedavi vaadi içermemelidir.
- Mobil ve masaüstü ekranlarda okunabilir olmalıdır.

## PB-02 – Kategoriye Ait Ürünleri Listeleme

**User Story:**  
Bir kullanıcı olarak seçtiğim kategoriye ait bitki ve takviyeleri görüntülemek istiyorum; böylece ilgili kullanım alanında araştırılan seçenekleri inceleyebileyim.

**Temel Kabul Kriterleri:**

- Kategori seçildiğinde ilişkili ürünler listelenmelidir.
- Ürün kartında ürün adı, türü ve kısa kullanım amacı bulunmalıdır.
- Aynı ürün liste içinde tekrar etmemelidir.
- Ürün bulunmadığında anlaşılır bir boş durum mesajı gösterilmelidir.
- Bir ürün birden fazla kategoriyle ilişkilendirilebilmelidir.

## PB-03 – Ürünün Temel Detaylarını Görüntüleme

**User Story:**  
Bir kullanıcı olarak seçtiğim bitki veya takviyenin temel bilgilerini görüntülemek istiyorum; böylece ürünün ne olduğunu ve hangi kullanım iddiasıyla incelendiğini anlayabileyim.

**Temel Kabul Kriterleri:**

- Ürünün Türkçe adı gösterilmelidir.
- Varsa İngilizce ve bilimsel adı gösterilmelidir.
- Ürün türü, kullanım amacı ve incelenen iddia gösterilmelidir.
- Kullanım amacı kesin tedavi vaadi gibi sunulmamalıdır.
- Kullanıcı önceki ürün listesine dönebilmelidir.

## PB-04 – Bilimsel Kanıt Seviyesini Görüntüleme

**User Story:**  
Bir kullanıcı olarak ürünün belirli kullanım iddiasına ait bilimsel kanıt seviyesini görmek istiyorum; böylece pazarlama iddialarıyla bilimsel bulguları ayırt edebileyim.

**Temel Kabul Kriterleri:**

- Kanıt seviyesi ürünün tamamına değil, belirli kullanım iddiasına bağlı olmalıdır.
- Seviye Güçlü, Orta veya Zayıf olarak gösterilmelidir.
- Seviyenin yanında kısa ve anlaşılır bir açıklama bulunmalıdır.
- Değerlendirme tamamlanmamışsa kesin seviye gösterilmemelidir.
- Kanıt seviyesi tedavi garantisi olarak sunulmamalıdır.

## PB-05 – Bilimsel ve Resmî Kaynakları Görüntüleme

**User Story:**  
Bir kullanıcı olarak sunulan bilgilerin dayandığı bilimsel ve resmî kaynakları görüntülemek istiyorum; böylece bilgilerin güvenilirliğini değerlendirebileyim.

**Temel Kabul Kriterleri:**

- Kaynak kuruluşu, kaynak başlığı ve bağlantısı gösterilmelidir.
- Bir kullanım iddiasına birden fazla kaynak bağlanabilmelidir.
- Kaynaklar ilgili kullanım iddiasıyla ilişkilendirilmelidir.
- Eksik veya geçersiz bağlantılar doğrulanmış kaynak gibi sunulmamalıdır.
- Kaynağın bulunması ürünün kesin olarak etkili olduğu şeklinde yorumlanmamalıdır.

## PB-06 – Risk, Yan Etki ve Etkileşim Bilgileri

**User Story:**  
Bir kullanıcı olarak bir bitki veya takviyenin risklerini, olası yan etkilerini ve etkileşimlerini görüntülemek istiyorum; böylece ürünü değerlendirmeden önce güvenlik açısından bilinçli hareket edebileyim.

**Temel Kabul Kriterleri:**

- Temel risk ve yan etkiler gösterilmelidir.
- Önemli ilaç veya takviye etkileşimleri ayrı bölümde sunulmalıdır.
- Özel kullanıcı grupları için önemli uyarılar gösterilebilmelidir.
- Bilgi bulunmaması ürünün risksiz olduğu şeklinde sunulmamalıdır.
- Gerektiğinde sağlık profesyoneline danışılması hatırlatılmalıdır.

## PB-07 – Tıbbi Bilgilendirme Uyarısı

**User Story:**  
Bir kullanıcı olarak sunulan bilgilerin tıbbi teşhis veya tedavi önerisi olmadığını açıkça görmek istiyorum; böylece platformun kullanım sınırlarını anlayabileyim.

**Temel Kabul Kriterleri:**

- Ana sayfada veya kolay erişilebilir bir alanda bilgilendirme uyarısı bulunmalıdır.
- Ürün detaylarında bilgilerin teşhis veya tedavi önerisi olmadığı belirtilmelidir.
- İlaç kullanımı, hastalık, gebelik veya emzirme durumunda sağlık profesyoneline danışılması hatırlatılmalıdır.
- Uyarı okunabilir ve görünür olmalıdır.
- Chatbot ve yapay zekâ çıktılarında da uygun uyarı gösterilebilmelidir.

## PB-08 – Görsel Bitki Tanıma

**User Story:**  
Bir kullanıcı olarak bir bitkinin fotoğrafını yüklemek istiyorum; böylece bitkinin olası adını öğrenerek PhyraMed’deki bilgi kartına ulaşabileyim.

**Temel Kabul Kriterleri:**

- Kullanıcı desteklenen bir bitki fotoğrafı yükleyebilmelidir.
- Sistem bitkinin olası adını gösterebilmelidir.
- Veri tabanında kayıt varsa ilgili detay sayfasına yönlendirme yapılmalıdır.
- Güven seviyesi düşükse kesin sonuç verilmemelidir.
- Tanıma sonucu tüketim veya tedavi tavsiyesi olarak sunulmamalıdır.
- Geçersiz görsellerde anlaşılır hata mesajı gösterilmelidir.

## PB-09 – Kullanıcı Yorumlarının Toplu Analizi

**User Story:**  
Bir kullanıcı olarak ürün hakkında paylaşılan yorumların toplu analizini görmek istiyorum; böylece çok sayıda yorumu tek tek okumadan genel kullanıcı deneyimini anlayabileyim.

**Temel Kabul Kriterleri:**

- Analiz edilen yorum sayısı gösterilmelidir.
- Olumlu, olumsuz ve nötr yorum dağılımı gösterilebilmelidir.
- Sık bildirilen olumlu ve olumsuz deneyimler özetlenmelidir.
- Yetersiz veri varsa kesin sonuç sunulmamalıdır.
- Kullanıcı yorumları bilimsel kanıt olarak gösterilmemelidir.
- Yapay zekâ özeti yorumlarda bulunmayan bilgi üretmemelidir.

## PB-10 – Chatbot Üzerinden Bilgi Alma

**User Story:**  
Bir kullanıcı olarak PhyraMed chatbot’una bitkiler, takviyeler ve kullanım iddiaları hakkında soru sormak istiyorum; böylece doğrulanmış bilgilere konuşma yoluyla ulaşabileyim.

**Temel Kabul Kriterleri:**

- Kullanıcı chatbot’a metin olarak soru gönderebilmelidir.
- Yanıtlar mümkün olduğunca PhyraMed veri tabanına dayanmalıdır.
- İlgili kaynaklara veya ürün detayına yönlendirme yapılabilmelidir.
- Yeterli bilgi yoksa chatbot bunu açıkça belirtmeli ve tahminde bulunmamalıdır.
- Chatbot teşhis koymamalı veya tedavi önermemelidir.
- Bilimsel kanıtlarla kullanıcı yorumlarını birbirine karıştırmamalıdır.

## Not

Ayrıntılı user story ve kabul kriterleri Jira üzerinde oluşturulmuş ve `SCRUM-9` göreviyle ilişkilendirilmiştir. Bu doküman, Product Backlog’un GitHub üzerinde erişilebilir özetini oluşturmaktadır.
