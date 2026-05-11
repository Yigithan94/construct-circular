# Construct Circular - Sistem Mimarisi Açıklaması

**Oluşturulma Tarihi:** 19 Haziran 2025  
**Platform:** Construct Circular v2.0  
**Mimari Yaklaşımı:** Katmanlı Mimari (Layered Architecture)

---

## 📋 Sistem Mimarisi Genel Bakış

Construct Circular platformu, modern web geliştirme prensiplerine uygun olarak **5 katmanlı mimari** yapısı ile tasarlanmıştır. Bu mimari, ölçeklenebilirlik, sürdürülebilirlik ve modülerlik açısından optimum performans sağlar.

---

## 🏗️ Mimari Katmanlar

### 1. Sunum Katmanı (Presentation Layer)
**Renk Kodu:** Mavi (#3498db)  
**Bileşenler:**
- **HTML/CSS/JavaScript:** Modern responsive web arayüzü
- **Bootstrap UI:** Mobile-first tasarım yaklaşımı
- **Jinja2 Templates:** Server-side template rendering
- **Multi-language Support:** Türkçe/İngilizce dil desteği

**Sorumluluklar:**
- Kullanıcı arayüzü render işlemleri
- Form validasyon ve input handling
- Responsive tasarım adaptasyonu
- Çoklu dil desteği yönetimi

### 2. Uygulama Katmanı (Application Layer)
**Renk Kodu:** Yeşil (#2ecc71)  
**Bileşenler:**
- **Flask Framework:** Python web framework
- **Blueprint Architecture:** Modüler uygulama yapısı
- **Form Validation:** WTForms ile güvenli form işleme
- **Session Management:** Güvenli oturum yönetimi

**Sorumluluklar:**
- HTTP request/response handling
- Routing ve URL yönetimi
- Middleware işlemleri
- Session ve cookie yönetimi

### 3. İş Mantığı Katmanı (Business Logic Layer)
**Renk Kodu:** Kırmızı (#e74c3c)  
**Bileşenler:**
- **TOPSIS Algorithm:** Fuzzy TOPSIS çok kriterli karar verme
- **AI Evaluation:** OpenAI GPT entegrasyonu ile akıllı değerlendirme
- **Role-based Access:** Kullanıcı rol tabanlı erişim kontrolü
- **Draft System:** Taslak başvuru sistemi

**Sorumluluklar:**
- İş kuralları implementasyonu
- Algoritma hesaplamaları
- AI entegrasyonu ve değerlendirme
- Güvenlik ve yetkilendirme

### 4. Veri Erişim Katmanı (Data Access Layer)
**Renk Kodu:** Turuncu (#f39c12)  
**Bileşenler:**
- **SQLAlchemy ORM:** Object-Relational Mapping
- **Database Models:** Veri modeli tanımları
- **Query Optimization:** Performans odaklı sorgu optimizasyonu
- **Transaction Management:** Veri tutarlılığı yönetimi

**Sorumluluklar:**
- Veritabanı bağlantı yönetimi
- CRUD operasyonları
- İlişkisel veri mapping
- Transaction yönetimi

### 5. Veri Katmanı (Data Layer)
**Renk Kodu:** Mor (#9b59b6)  
**Bileşenler:**
- **PostgreSQL Database:** Ana veritabanı sistemi
- **File Storage:** Dosya depolama sistemi
- **Backup Systems:** Yedekleme mekanizmaları
- **Data Security:** Veri güvenliği protokolleri

**Sorumluluklar:**
- Veri depolama ve yönetimi
- Dosya sistemi operasyonları
- Yedekleme ve kurtarma
- Veri güvenliği ve şifreleme

---

## 🔄 Sistem Bileşenleri Arası İletişim

### Harici Entegrasyonlar

#### OpenAI API Entegrasyonu
- **Konum:** İş Mantığı Katmanı ile entegre
- **Fonksiyon:** Doküman analizi ve akıllı değerlendirme
- **Protokol:** REST API üzerinden JSON iletişimi

#### E-posta Sistemleri
- **Konum:** Veri Erişim Katmanı ile entegre
- **Fonksiyon:** Bildirim ve iletişim
- **Servisler:** SendGrid, Twilio entegrasyonu

#### Dosya Depolama
- **Konum:** Veri Katmanı ile entegre
- **Fonksiyon:** Proje dosyaları ve dokümanlar
- **Format Desteği:** PDF, DOCX, TXT, resim dosyaları

---

## 🎯 Mimari Avantajları

### Modülerlik
- Her katman bağımsız geliştirilebilir
- Değişiklikler diğer katmanları etkilemez
- Test edilebilirlik artar

### Ölçeklenebilirlik
- Horizontal ve vertical scaling mümkün
- Yük dağılımı optimize edilebilir
- Performans izleme kolaylaşır

### Sürdürülebilirlik
- Kod organizasyonu net ve anlaşılır
- Bakım ve geliştirme kolaylaşır
- Yeni özellik ekleme basitleşir

### Güvenlik
- Katmanlar arası güvenlik kontrolleri
- Role-based access control
- Veri validasyon çoklu seviyede

---

## 🔧 Teknik Özellikler

### Design Patterns
- **MVC Pattern:** Model-View-Controller
- **Repository Pattern:** Veri erişim soyutlaması
- **Factory Pattern:** Nesne oluşturma yönetimi
- **Observer Pattern:** Event handling

### API Yaklaşımı
- **RESTful Design:** Standart HTTP metotları
- **JSON Communication:** Lightweight veri transferi
- **Error Handling:** Standartlaştırılmış hata yönetimi

### Performans Optimizasyonları
- **Database Indexing:** Sorgu performansı
- **Caching Strategies:** Memory ve disk cache
- **Asset Optimization:** CSS/JS minification
- **Image Compression:** Görsel optimizasyonu

---

## 📊 Veri Akışı

### Kullanıcı İnteraksiyon Akışı
1. **Frontend:** Kullanıcı arayüzü ile etkileşim
2. **Application Layer:** Request processing ve routing
3. **Business Logic:** İş kuralları uygulaması
4. **Data Access:** Veritabanı operasyonları
5. **Database:** Veri depolama ve retrieval

### AI Değerlendirme Akışı
1. **Doküman Upload:** Kullanıcı dosya yükler
2. **Text Extraction:** İçerik çıkarma işlemi
3. **AI Processing:** OpenAI API ile analiz
4. **Score Calculation:** TOPSIS algoritması
5. **Result Storage:** Sonuçların saklanması

---

## 🛡️ Güvenlik Mimarisi

### Kimlik Doğrulama
- **Session-based Auth:** Flask-Login ile güvenli oturum
- **Password Hashing:** Werkzeug güvenlik utilities
- **Role Management:** Şirket/Müteahhit/Admin rolleri

### Veri Güvenliği
- **Input Validation:** Form seviyesinde validasyon
- **SQL Injection Prevention:** ORM kullanımı
- **XSS Protection:** Template engine güvenliği
- **CSRF Protection:** Token tabanlı koruma

### Dosya Güvenliği
- **Upload Restrictions:** Dosya tipi ve boyut kontrolü
- **Virus Scanning:** Yüklenen dosya kontrolü
- **Access Control:** Yetki tabanlı dosya erişimi

---

## 🚀 Deployment Mimarisi

### Replit Platform
- **Hosting:** Replit autoscale deployment
- **Runtime:** Python 3.11 + PostgreSQL 16
- **Process Management:** Gunicorn production server
- **Package Management:** UV ile bağımlılık yönetimi

### Sistem Bağımlılıkları
- **Cairo/FontConfig:** PDF generation support
- **GTK Libraries:** GUI toolkit dependencies
- **SSL Support:** OpenSSL secure communications

---

## 📈 Performans ve İzleme

### Monitoring
- **Application Logs:** Detaylı sistem logları
- **Database Monitoring:** Query performance tracking
- **Error Tracking:** Exception handling ve raporlama

### Optimization
- **Database Queries:** Index optimization
- **Static Assets:** CDN ve caching
- **Memory Management:** Efficient resource usage

---

Bu mimari, Construct Circular platformunun hem mevcut ihtiyaçlarını karşılar hem de gelecekteki gelişmeler için solid bir temel sağlar. Katmanlı yapı sayesinde sistem modüler, güvenli ve ölçeklenebilir bir şekilde tasarlanmıştır.