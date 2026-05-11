
# Construct Circular - Ekran Ekran Fonksiyonel Analiz

**Tarih:** 17 June 2025, 19:30  
**Platform:** Construct Circular v2.0  
**Kapsam:** Tüm Ekranlar ve Fonksiyonellik  

---

## Ana Sayfa ve Giriş

### Ana Sayfa (/)
**Fonksiyonlar:**
- Otomatik yönlendirme (giriş yapmış kullanıcılar dashboard'a)
- Giriş formu görüntüleme
- Dil değiştirme (TR/EN)
- Logo ve marka kimliği

**UI Bileşenleri:**
- Header: Icon logo + gradyan yazı
- Hero section: Ana logo (280px) + açıklama
- Navigation menu: Responsive hamburger menu
- Footer: Üniversite ve TÜBİTAK logoları

**Teknik Özellikler:**
- Flask route: @main_bp.route('/', methods=['GET', 'POST'])
- Template: auth/login.html
- Responsive design: Bootstrap grid
- CSS gradyan: linear-gradient(135deg, #2ecc71, #1abc9c)

---

## Kimlik Doğrulama Ekranları

### Giriş Ekranı (/login)
**Form Alanları:**
- Email/Username (zorunlu, validasyonlu)
- Şifre (güvenli giriş)
- Rol seçimi (Company/Contractor dropdown)
- Giriş butonu + kayıt linkleri

**Güvenlik:**
- CSRF token koruması
- Input validation (client + server)
- Session management
- Brute force protection

**Fonksiyonlar:**
- Kullanıcı doğrulama
- Rol tabanlı yönlendirme
- Hata mesajları
- Remember me özelliği

### Şirket Kayıt (/register/company)
**Form Alanları:**
- Username (2-20 karakter, benzersiz)
- Email (geçerli, benzersiz)
- Şifre (min 6 karakter)
- Şifre tekrarı
- Şirket adı (2-100 karakter)
- Şirket açıklaması (opsiyonel)

**Validasyon:**
- Real-time benzersizlik kontrolü
- Güçlü şifre gereksinimleri
- Email format doğrulama

### Müteahhit Kayıt (/register/contractor)
**Özel Alanlar:**
- Uzmanlık alanı (2-100 karakter)
- Deneyim yılı (0-100 numerik)
- Portfolio bilgileri
- Sertifikalar

**Fonksiyonlar:**
- Uzmanlık kategorileri
- Deneyim validasyonu
- Portfolio upload
- Yetenek değerlendirmesi

---

## Dashboard Ekranları

### Şirket Dashboard (/dashboard)
**Metrik Kartları:**
- Toplam projeler (status breakdown)
- Aktif başvurular (review gerekli)
- Tamamlanan işler
- Bütçe özeti

**Hızlı Eylemler:**
- Yeni proje oluştur butonu
- Başvuruları görüntüle
- Raporları incele
- Profil güncelle

**Görselleştirme:**
- Chart.js interactive charts
- Progress bars
- Timeline view
- Status indicators

### Müteahhit Dashboard (/dashboard)
**Başvuru Kartları:**
- DRAFT (taslak başvurular)
- PENDING (değerlendirme bekleyen)
- ACCEPTED (kabul edilen)
- REJECTED (reddedilen)

**Fonksiyonlar:**
- Proje arama ve filtreleme
- Başvuru durumu takibi
- Profil tamamlama progress
- Performans metrikleri

---

## Proje Yönetimi

### Proje Oluşturma (/projects/create)
**Temel Bilgiler:**
- Proje adı (2-100 karakter)
- Proje açıklaması
- Beklentiler
- Lokasyon

**Zaman Planı:**
- Başlangıç tarihi (DatePicker)
- Bitiş tarihi (validation)
- Otomatik süre hesaplama

**Bütçe ve Kriterler:**
- Bütçe aralığı dropdown
- Değerlendirme kriterleri
- KPI tanımlama

**Özel Fonksiyonlar:**
- Taslak kaydetme
- Kriter ağırlık hesaplama
- Dosya yükleme
- Önizleme sistemi

### Proje Detay (/projects/<id>)
**Bilgi Bölümleri:**
- Proje özeti
- Zaman çizelgesi
- Bütçe bilgileri
- Değerlendirme kriterleri

**Başvuru Sistemi:**
- Başvuru butonu (contractors)
- Real-time başvuru sayacı
- Son başvuru tarihi countdown
- Gereksinimler listesi

**Şirket Kontrolü:**
- Düzenleme butonu (owner only)
- Başvuru listesi
- Proje durumu değiştirme
- İstatistikler

### Kriter Yönetimi (/projects/<id>/criteria)
**Hiyerarşik Yapı:**
- Ana kriterler
- Alt kriterler (ağırlıklı)
- KPI tanımlama
- Ağırlık dağılımı

**Fuzzy TOPSIS:**
- Low/medium/high weight values
- Otomatik normalizasyon
- Matematiksel doğrulama
- Önizleme sistemi

---

## Başvuru Sistemi

### Başvuru Formu (/apply/<project_id>)
**Dinamik Form:**
- Cover letter (rich text editor)
- KPI belgeleri (dinamik upload fields)
- Dosya önizleme
- Taslak kaydetme

**Draft Sistemi:**
- Otomatik kaydetme (30 saniye)
- Validasyon atlama
- Session recovery
- Visual status indicator

**Dosya Yönetimi:**
- Çoklu format (PDF, DOC, DOCX, TXT)
- Boyut kontrolü
- Güvenlik validation
- Önizleme sistemi

### Başvuru Durumu (/applications/<id>)
**Durum Takibi:**
- Visual timeline progression
- AI değerlendirme sonuçları
- TOPSIS puanı
- Feedback ve öneriler

**Düzenleme:**
- Belge güncelleme
- Cover letter edit
- Ek bilgi ekleme
- Withdraw seçeneği

### Başvuru Listesi (/my-applications)
**Filtreleme:**
- Status filtreleri
- Tarih sıralaması
- Proje kategorisi
- Puan sıralaması

**Toplu İşlemler:**
- Çoklu seçim
- Bulk delete
- PDF export
- İstatistik dashboard

---

## Admin Panel

### Admin Dashboard (/admin)
**Sistem İstatistikleri:**
- Kullanıcı sayıları (role breakdown)
- Aktif projeler
- Günlük aktivite
- Sistem sağlığı

**Yönetim Araçları:**
- Kullanıcı yönetimi
- Proje oversight
- Sistem konfigürasyon
- Log görüntüleme

### Kullanıcı Yönetimi (/admin/users)
**Kullanıcı Tablosu:**
- Filtreleme (role, date, status)
- Arama (username, email)
- Sıralama
- Sayfalama

**İşlemler:**
- Profil görüntüleme
- Rol değiştirme
- Hesap durumu
- Password reset

### KPI Yönetimi (/admin/kpis)
**Konfigürasyon:**
- Global KPIs
- AI evaluation settings
- Scoring algorithms
- Weight templates

---

## Profil Yönetimi

### Şirket Profil (/profile/company)
**Düzenlenebilir:**
- Şirket adı
- Açıklama
- İletişim bilgileri
- Logo yükleme

**Ayarlar:**
- Profil görünürlüğü
- İletişim tercihleri
- Bildirim ayarları

### Müteahhit Profil (/profile/contractor)
**Profesyonel Bilgiler:**
- Uzmanlık alanları
- Deneyim detayları
- Sertifikalar
- Portfolio

**Performans:**
- Başarı oranı
- Ortalama puan
- Müşteri değerlendirmeleri
- Tamamlanan projeler

---

## Rapor ve Analiz

### TOPSIS Raporu (/projects/<id>/topsis-report)
**Analiz Bileşenleri:**
- Karar matrisi
- Ağırlık dağılımı
- Alternatif sıralaması
- Skor dağılımı

**Export:**
- PDF rapor
- Excel data
- Chart images
- Summary report

### Performans Analiz (/reports/performance)
**Metrik Kategorileri:**
- Kullanıcı performansı
- Proje başarı oranları
- AI değerlendirme doğruluğu
- Sistem kullanımı

---

## Özel Fonksiyonlar

### AI Değerlendirme Sistemi
**Süreç:**
1. Belge yükleme ve validation
2. Text extraction (çoklu format)
3. GPT-4o powered analysis
4. 1-7 scale scoring
5. TOPSIS calculation

### Fuzzy TOPSIS Algoritması
**Adımlar:**
1. Matrix normalization
2. Weight application
3. Ideal solutions
4. Distance calculation
5. Ranking

### Draft Sistemi
**Özellikler:**
- Auto-save (JavaScript timer)
- Change detection
- Network handling
- Recovery system

---

## Mobil Uyumluluk

### Responsive Breakpoints
- xs (<576px): Mobile portrait
- sm (≥576px): Mobile landscape
- md (≥768px): Tablets
- lg (≥992px): Small desktops
- xl (≥1200px): Large desktops

### Touch Interface
- 44px minimum touch targets
- Gesture support
- Keyboard optimization
- Zoom prevention

---

## Güvenlik ve Performans

### Güvenlik Katmanları
- Password hashing (Werkzeug)
- Session management
- CSRF protection
- Input validation

### Performans Optimizasyonu
- Database indexing
- Query optimization
- CSS/JS minification
- Image optimization
- Browser caching

---

## Teknik Özellikler

### Backend Stack
- Python 3.11
- Flask framework
- SQLAlchemy ORM
- PostgreSQL database

### Frontend Stack
- HTML5 semantic markup
- CSS3 with Grid/Flexbox
- JavaScript + Chart.js
- Bootstrap 5 framework

### AI Integration
- OpenAI GPT-4o API
- Document processing
- Intelligent scoring

---

## Ekran İstatistikleri

**Toplam Kapsam:**
- 20+ ana fonksiyonel ekran
- 31 HTML template
- 15 Python modül
- 4,117 satır kod

**Kategoriler:**
- 5 kimlik doğrulama ekranı
- 4 dashboard ekranı
- 6 proje yönetimi ekranı
- 3 başvuru sistemi ekranı
- 4 admin panel ekranı
- 2 profil yönetimi ekranı
- 2 rapor ekranı

**Özel Özellikler:**
- AI-powered evaluation
- Fuzzy TOPSIS analysis
- Multi-language support
- Role-based architecture
- Draft system
- Real-time updates

---

**Platform Durumu:** Production Ready  
**Son Güncelleme:** 17 June 2025  
**Versiyon:** 2.0  
