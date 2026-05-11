#!/usr/bin/env python3
"""
Screen-by-Screen Documentation Generator for Construct Circular
Creates detailed functionality analysis for every screen
"""

import os
from datetime import datetime
import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

def create_screen_documentation():
    """Create comprehensive screen-by-screen documentation"""
    
    content = f"""
# Construct Circular - Ekran Ekran Fonksiyonel Analiz

**Tarih:** {datetime.now().strftime('%d %B %Y, %H:%M')}  
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
**Son Güncelleme:** {datetime.now().strftime('%d %B %Y')}  
**Versiyon:** 2.0  
"""
    
    return content

def create_pdf_report():
    """Generate PDF from documentation"""
    
    print("Ekran ekran analiz dokümanı oluşturuluyor...")
    
    # Generate content
    markdown_content = create_screen_documentation()
    
    # Save markdown
    markdown_file = "Construct_Circular_Ekran_Analiz.md"
    with open(markdown_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    # Convert to HTML
    md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc', 'tables'])
    html_body = md.convert(markdown_content)
    
    # Create styled HTML
    html_doc = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Construct Circular - Ekran Analizi</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        body {{
            font-family: 'Inter', system-ui, sans-serif;
            line-height: 1.6;
            color: #2d3748;
            max-width: 210mm;
            margin: 0 auto;
            padding: 20mm;
            background: white;
        }}
        
        h1 {{
            color: #1a202c;
            font-size: 2.5em;
            font-weight: 700;
            text-align: center;
            margin-bottom: 2rem;
            background: linear-gradient(135deg, #2ecc71, #1abc9c);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        h2 {{
            color: #2d3748;
            font-size: 1.8em;
            font-weight: 600;
            margin: 2rem 0 1rem 0;
            border-left: 4px solid #2ecc71;
            padding-left: 1rem;
        }}
        
        h3 {{
            color: #4a5568;
            font-size: 1.4em;
            font-weight: 500;
            margin: 1.5rem 0 1rem 0;
        }}
        
        p, li {{
            margin-bottom: 0.8rem;
            text-align: justify;
        }}
        
        ul, ol {{
            margin: 1rem 0;
            padding-left: 2rem;
        }}
        
        strong {{
            color: #2d3748;
            font-weight: 600;
        }}
        
        .screen-section {{
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-left: 4px solid #3182ce;
        }}
        
        @page {{
            size: A4;
            margin: 15mm;
        }}
    </style>
</head>
<body>
    {html_body}
    
    <div style="text-align: center; margin-top: 3rem; padding-top: 2rem; border-top: 2px solid #e2e8f0;">
        <p><strong>Yıldız Teknik Üniversitesi - TÜBİTAK Destekli Proje</strong></p>
        <p>Bu ekran analiz raporu, Construct Circular platformunun tüm fonksiyonelliklerini kapsar.</p>
    </div>
</body>
</html>
"""
    
    # Save HTML
    html_file = "Construct_Circular_Ekran_Analiz.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_doc)
    
    # Generate PDF
    pdf_file = "Construct_Circular_Ekran_Fonksiyon_Raporu.pdf"
    
    pdf_css = CSS(string='''
        @page { size: A4; margin: 15mm; }
        body { font-size: 11pt; }
        h1 { font-size: 18pt; }
        h2 { font-size: 14pt; }
        h3 { font-size: 12pt; }
    ''')
    
    font_config = FontConfiguration()
    
    HTML(string=html_doc).write_pdf(
        pdf_file,
        stylesheets=[pdf_css],
        font_config=font_config,
        optimize_images=True
    )
    
    return markdown_file, html_file, pdf_file

def main():
    """Main execution function"""
    try:
        markdown_file, html_file, pdf_file = create_pdf_report()
        
        print(f"✅ Markdown: {markdown_file}")
        print(f"✅ HTML: {html_file}")
        print(f"✅ PDF: {pdf_file}")
        print(f"📊 PDF boyutu: {os.path.getsize(pdf_file) / 1024:.1f} KB")
        
        print("\n🎉 Ekran ekran fonksiyonel analiz tamamlandı!")
        
    except Exception as e:
        print(f"❌ Hata: {str(e)}")

if __name__ == "__main__":
    main()