# Construct Circular Platform Wireframe Documentation

## Genel Bakış
Bu belge, Construct Circular platformunun kullanıcı akışlarını, ekran tasarımlarını ve sistem mimarisini wireframe formatında göstermektedir.

---

## 1. Platform Ana Yapısı

### Header/Navigation Bar
```
[Logo: Construct Circular] [Dashboard] [Projects] [Applications] [Reports] [Account ▼] [Language ▼]
```

### User Authentication Flow
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Landing Page  │ →  │   Login/Register│ →  │   Dashboard     │
│                 │    │                 │    │                 │
│ • Platform Info │    │ • Company       │    │ • Role-based    │
│ • Features      │    │ • Contractor    │    │ • Quick Actions │
│ • Login Button  │    │ • Admin         │    │ • Statistics    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 2. İşveren (Company) Kullanıcı Akışı

### 2.1 Dashboard
```
┌──────────────────────────────────────────────────────────────┐
│                     İşveren Dashboard                        │
├──────────────────────────────────────────────────────────────┤
│ [+ New Project]                              [My Profile]    │
│                                                              │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│ │ Active Projects │ │ Total Applic.   │ │ Completed       │ │
│ │      5          │ │      23         │ │      12         │ │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘ │
│                                                              │
│ Recent Projects:                                             │
│ ┌────────────────────────────────────────────────────────┐   │
│ │ Project Name           Status        Applications      │   │
│ │ ─────────────────────────────────────────────────────   │   │
│ │ İnşaat Projesi A      Published           8           │   │
│ │ Yol Yapım İşi         Evaluation          5           │   │
│ │ Köprü Projesi         Completed           12          │   │
│ └────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Project Creation Flow
```
Step 1: Basic Info           Step 2: Criteria              Step 3: KPI Definition
┌─────────────────────┐     ┌─────────────────────┐       ┌─────────────────────┐
│ • Project Name      │ →   │ • Main Criteria     │ →     │ • KPI Selection     │
│ • Description       │     │ • Sub-criteria      │       │ • AI Evaluation     │
│ • Budget            │     │ • Weights (%)       │       │ • Document Types    │
│ • Timeline          │     │ • Scoring Method    │       │ • Upload Rules      │
│ • Location          │     │                     │       │                     │
│ [Next Step]         │     │ [Add Criterion]     │       │ [Publish Project]   │
└─────────────────────┘     └─────────────────────┘       └─────────────────────┘
```

### 2.3 Application Review & TOPSIS Analysis
```
┌────────────────────────────────────────────────────────────────────┐
│                    Project: İnşaat Projesi A                       │
├────────────────────────────────────────────────────────────────────┤
│ Applications (8)                          [Calculate TOPSIS]       │
│                                                                    │
│ ┌──────────────────────────────────────────────────────────────┐   │
│ │ Contractor Name    Status      TOPSIS Score    Documents     │   │
│ │ ──────────────────────────────────────────────────────────   │   │
│ │ ABC İnşaat        Evaluated    0.847523       ✓ Complete    │   │
│ │ XYZ Yapı          Evaluated    0.735241       ✓ Complete    │   │
│ │ DEF Construction  Pending      -              ⚠ Incomplete  │   │
│ └──────────────────────────────────────────────────────────────┘   │
│                                                                    │
│ [View Details] [Generate Report] [Select Winner]                   │
└────────────────────────────────────────────────────────────────────┘
```

---

## 3. Yüklenici (Contractor) Kullanıcı Akışı

### 3.1 Dashboard
```
┌──────────────────────────────────────────────────────────────┐
│                   Yüklenici Dashboard                        │
├──────────────────────────────────────────────────────────────┤
│ [Browse Projects]                        [My Applications]   │
│                                                              │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│ │ Active Applic.  │ │ Won Projects    │ │ Success Rate    │ │
│ │      3          │ │      2          │ │      67%        │ │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘ │
│                                                              │
│ Available Projects:                                          │
│ ┌────────────────────────────────────────────────────────┐   │
│ │ Project Name           Deadline      Budget Range      │   │
│ │ ─────────────────────────────────────────────────────   │   │
│ │ İnşaat Projesi B      15 days       5M - 10M TL       │   │
│ │ Yol Genişletme        7 days        2M - 4M TL        │   │
│ │ Park Düzenleme        30 days       500K - 1M TL      │   │
│ └────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 Project Application Process
```
Step 1: Project Details      Step 2: Documents Upload       Step 3: Review & Submit
┌─────────────────────┐     ┌─────────────────────┐       ┌─────────────────────┐
│ • Project Info      │ →   │ • Certificate Files │ →     │ • Application       │
│ • Requirements      │     │ • Experience Docs   │       │   Summary           │
│ • Criteria List     │     │ • Financial Docs    │       │ • Document Status   │
│ • Timeline          │     │ • Technical Plans   │       │ • AI Evaluation     │
│ • KPI Definitions   │     │ • References        │       │   Preview           │
│ [Apply Now]         │     │ [Upload & AI Check] │       │ [Submit Application]│
└─────────────────────┘     └─────────────────────┘       └─────────────────────┘
```

### 3.3 Application Tracking
```
┌────────────────────────────────────────────────────────────────────┐
│                      My Applications                               │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│ ┌──────────────────────────────────────────────────────────────┐   │
│ │ Project Name       Status        Score      AI Evaluation    │   │
│ │ ────────────────────────────────────────────────────────────  │   │
│ │ İnşaat Proj. A    Evaluated      0.735     ✓ 8.5/10         │   │
│ │ Yol Yapımı        Under Review   -         ⏳ Processing     │   │
│ │ Köprü Projesi     Won           0.891      ✓ 9.2/10         │   │
│ └──────────────────────────────────────────────────────────────┘   │
│                                                                    │
│ [View Details] [Update Documents] [Performance Report]             │
└────────────────────────────────────────────────────────────────────┘
```

---

## 4. AI Evaluation & TOPSIS System Flow

### 4.1 Document Processing Pipeline
```
Document Upload → AI Analysis → KPI Scoring → TOPSIS Calculation → Ranking
     ↓              ↓             ↓              ↓                 ↓
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐      ┌─────────┐
│PDF/DOCX │ → │OpenAI   │ → │1-7 Scale│ → │Matrix   │  →   │Final    │
│Files    │   │Analysis │   │Scoring  │   │Calc     │      │Ranking  │
│         │   │         │   │         │   │         │      │         │
│Text     │   │Content  │   │Auto KPI │   │Weighted │      │Report   │
│Extract  │   │Eval     │   │Assign   │   │Scores   │      │Generate │
└─────────┘   └─────────┘   └─────────┘   └─────────┘      └─────────┘
```

### 4.2 TOPSIS Decision Matrix
```
┌─────────────────────────────────────────────────────────────────────┐
│                     TOPSIS Analysis Matrix                          │
├─────────────────────────────────────────────────────────────────────┤
│                 │ Experience │ Financial │ Technical │ References   │
│ Contractors     │   (30%)    │   (25%)   │   (25%)   │    (20%)     │
│ ─────────────────────────────────────────────────────────────────── │
│ ABC İnşaat      │    8.5     │    7.2    │    9.1    │     8.8      │
│ XYZ Yapı        │    7.8     │    8.9    │    7.5    │     7.2      │
│ DEF Construction│    9.2     │    6.8    │    8.3    │     8.1      │
│                                                                     │
│ Calculated Scores:                                                  │
│ 1. ABC İnşaat:      0.847523                                       │
│ 2. DEF Construction: 0.782341                                       │
│ 3. XYZ Yapı:        0.735241                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. Admin Panel Flow

### 5.1 System Management
```
┌────────────────────────────────────────────────────────────────────┐
│                        Admin Dashboard                             │
├────────────────────────────────────────────────────────────────────┤
│ [User Management] [Project Oversight] [System Settings]            │
│                                                                    │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐       │
│ │ Total Users     │ │ Active Projects │ │ System Health   │       │
│ │     1,247       │ │      89         │ │     ✓ Online    │       │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘       │
│                                                                    │
│ Global Criteria Management:                                        │
│ ┌──────────────────────────────────────────────────────────────┐   │
│ │ • Experience Requirements                                    │   │
│ │ • Financial Criteria Standards                               │   │
│ │ • Technical Evaluation Methods                               │   │
│ │ • AI Evaluation Parameters                                   │   │
│ │ • TOPSIS Weight Configurations                               │   │
│ └──────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────┘
```

---

## 6. Reporting & Analytics

### 6.1 Performance Reports
```
┌────────────────────────────────────────────────────────────────────┐
│                    Performance Analytics                           │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│ Chart Area:                        Key Metrics:                    │
│ ┌─────────────────────────────┐   ┌─────────────────────────────┐  │
│ │        📊 TOPSIS           │   │ • Average Score: 0.756      │  │
│ │      Score Distribution     │   │ • Best Performance: 0.891  │  │
│ │                            │   │ • Projects Completed: 45   │  │
│ │   📈 Trend Analysis        │   │ • Success Rate: 78%        │  │
│ │                            │   │ • AI Accuracy: 94%         │  │
│ └─────────────────────────────┘   └─────────────────────────────┘  │
│                                                                    │
│ [Export PDF] [Detailed Report] [Historical Data]                   │
└────────────────────────────────────────────────────────────────────┘
```

---

## 7. Mobile Responsive Design

### 7.1 Mobile Navigation
```
┌─────────────────────┐
│ ☰  Construct       │ ← Hamburger Menu
│    Circular    👤  │ ← User Avatar
├─────────────────────┤
│                     │
│ Dashboard           │
│ Projects            │
│ Applications        │
│ Reports             │
│ Account             │
│ ─────────────────── │
│ Language: TR ▼     │
│ Logout             │
│                     │
└─────────────────────┘
```

### 7.2 Mobile Project Cards
```
┌─────────────────────┐
│ İnşaat Projesi A    │
├─────────────────────┤
│ 🏗️ Construction     │
│ 💰 5M - 10M TL      │
│ 📅 15 days left     │
│ 👥 8 applications   │
│                     │
│ [View Details]      │
│ [Apply Now]         │
└─────────────────────┘
```

---

## 8. Data Flow Architecture

### 8.1 System Integration
```
Frontend (React/HTML) ←→ Flask Backend ←→ PostgreSQL Database
        ↓                      ↓                    ↓
   Bootstrap UI          Route Handlers         User Data
   Chart.js Viz         Authentication         Project Data
   Form Validation      File Processing        Application Data
        ↓                      ↓                    ↓
   User Interface    ←→   Business Logic   ←→   Data Storage
                            ↓
                      External APIs:
                      • OpenAI (AI Evaluation)
                      • SendGrid (Email)
                      • Twilio (SMS)
```

### 8.2 Security & Authentication Flow
```
User Login → Session Creation → Role Verification → Route Access
     ↓              ↓                ↓               ↓
┌─────────┐   ┌─────────┐      ┌─────────┐   ┌─────────┐
│Username │ → │Password │  →   │Role     │ → │Page     │
│Email    │   │Hash     │      │Check    │   │Access   │
│         │   │Verify   │      │(Company,│   │Control  │
│         │   │         │      │Contract,│   │         │
│         │   │         │      │Admin)   │   │         │
└─────────┘   └─────────┘      └─────────┘   └─────────┘
```

---

## 9. Key Features Wireframe Summary

### Platform Highlights:
- **Multi-language Support**: Turkish/English interface switching
- **Role-based Access**: Company, Contractor, Admin dashboards
- **AI-powered Evaluation**: OpenAI integration for document analysis
- **TOPSIS Algorithm**: Scientific multi-criteria decision making
- **Real-time Updates**: Live application status and scoring
- **Comprehensive Reporting**: PDF generation with charts and analytics
- **Mobile Responsive**: Optimized for all device sizes
- **File Management**: Secure document upload and processing
- **Performance Tracking**: Historical data and trend analysis

### Technical Architecture:
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Backend**: Python Flask with Blueprint architecture
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI Integration**: OpenAI API for content evaluation
- **PDF Generation**: WeasyPrint for report creation
- **Visualization**: Chart.js for data presentation
- **Authentication**: Flask-Login with session management
- **Internationalization**: Flask-Babel for multi-language support

---

*Bu wireframe belgesi Construct Circular platformunun tam işlevsel akışını ve kullanıcı deneyimini göstermektedir. Platform, TOPSIS algoritması ve AI destekli değerlendirme ile objektif karar verme süreci sağlamaktadır.*

**Oluşturma Tarihi**: 25 Temmuz 2025  
**Platform Versiyonu**: 2.0 - Gelişmiş AI Entegrasyonu  
**Wireframe Kapsamı**: Tam Platform Akışı ve Kullanıcı Deneyimi