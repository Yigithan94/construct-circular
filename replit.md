# Overview

This Flask-based web application facilitates construction project decision-making using Fuzzy TOPSIS analysis. It enables companies to create projects, contractors to apply, and employs AI-powered evaluation combined with TOPSIS scoring for objective contractor selection. The platform aims to streamline and enhance the decision-making process in construction project procurement.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Design Principles
-   **Modular Structure**: Blueprint-based architecture for scalability and maintainability.
-   **Role-Based Access Control**: Distinct permissions for Company, Contractor, and Admin roles.
-   **Internationalization**: Multi-language support (Turkish and English) using Flask-Babel.
-   **Responsive Design**: Mobile-friendly interface built with Bootstrap.
-   **AI Integration**: AI-powered document analysis for objective evaluation.
-   **Advanced Decision Support**: Fuzzy TOPSIS for multi-criteria analysis and ranking.

## Technical Stack
-   **Backend**: Flask (Python), SQLAlchemy ORM, WTForms, Flask-Login.
-   **Frontend**: Jinja2 templates, Bootstrap (dark theme), Chart.js for visualizations.
-   **Database**: PostgreSQL.

## Key Features
-   **User Management**: Role-based authentication, profile management, and an administrative interface.
-   **Project Lifecycle Management**: Project creation, flexible criteria definition (with weights and sub-criteria), contractor application system, and status tracking.
-   **TOPSIS Analysis Engine**: Fuzzy TOPSIS implementation, group analysis, automated scoring, and comparative reporting.
-   **AI Evaluation**: OpenAI-powered document analysis (PDF, DOCX, web content), text extraction, and AI-assisted KPI assessment.
-   **Reporting**: Professional PDF report generation (WeasyPrint), performance analytics, and visual reports with Chart.js.

# External Dependencies

## Core Technologies
-   **Flask Ecosystem**: Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-Babel.
-   **Database**: PostgreSQL (with psycopg2-binary).
-   **Scientific Computing**: NumPy, Pandas.
-   **Document Processing**: PyPDF2, python-docx, trafilatura.

## AI and Machine Learning
-   **OpenAI API**: For GPT model integration in document analysis and evaluation.

## Visualization and Reporting
-   **Charting**: Matplotlib, Chart.js.
-   **PDF Generation**: WeasyPrint.

## Infrastructure & Utilities
-   **Email Services**: SendGrid, Twilio.
-   **Security**: Werkzeug.
-   **Internationalization**: Babel.

# AI Architecture & Methodology

## Overview
The platform employs OpenAI's GPT-4o model for automated document evaluation and KPI scoring. The AI system processes contractor-submitted documents (PDF, DOCX, HTML, TXT) to generate objective scores (1-7 scale) based on circular economy criteria.

## 1. Document Processing Pipeline

### Text Extraction
- **PDF Processing**: PyPDF2 library with encryption handling and page-by-page extraction
- **DOCX Processing**: python-docx with table extraction and heading preservation
- **HTML Processing**: Trafilatura for intelligent content extraction with fallback mechanisms
- **TXT Processing**: Multi-encoding support (UTF-8, ISO-8859-1, Windows-1252, ASCII)

### Text Preprocessing
- Page break markers insertion for context preservation
- Whitespace normalization and newline cleanup
- Token limit management: 10,000 character truncation (5,000 from beginning + 5,000 from end)

## 2. Vectorisation & Embedding (Current State)

**Current Implementation**: The system does NOT use vector embeddings. Documents are processed as raw text strings.

**Processing Flow**:
```
Document → Text Extraction → Direct String Input → GPT-4o
```

**Limitations**:
- Token limit constraints (10,000 chars after truncation)
- No semantic search capability
- Limited long-document handling

**Future Enhancement Opportunities**:
- **Embedding Models**: OpenAI `text-embedding-3-small` or `text-embedding-3-large`
- **Vector Storage**: PostgreSQL with pgvector extension, Pinecone, or Weaviate
- **RAG Architecture**: Chunk-based retrieval for comprehensive document analysis
- **Semantic Search**: Query-based relevant section extraction

## 3. Machine Learning Models & Text Interpretation

### Model Architecture
- **Model**: GPT-4o (OpenAI's multimodal foundation model, released May 2024)
- **Training Approach**: Pre-trained model (no fine-tuning or supervised learning)
- **Temperature**: 0.2 (low temperature for consistent, deterministic scoring)
- **Output Format**: Structured JSON (`{"score": int, "explanation": str}`)

### Prompt Engineering Strategy

**System Role Definition**:
```
"Professional KPI evaluator for construction projects with expertise 
in circular economy principles and sustainability"
```

**Evaluation Prompt Structure**:
1. **Criteria Injection**: Sub-criterion description and evaluation guidelines
2. **Document Context**: Extracted text with structural markers
3. **Scoring Scale**: Detailed 1-7 rubric with descriptive anchors
4. **Output Schema**: JSON format with score and explanation fields

**Scoring Rubric**:
- 1 = Completely inadequate, does not meet any criteria
- 2 = Very poor, barely meets minimal criteria  
- 3 = Below average, meets some basic criteria but has significant weaknesses
- 4 = Average, adequately meets criteria but has room for improvement
- 5 = Above average, meets most criteria well
- 6 = Very good, meets almost all criteria excellently
- 7 = Exceptional, exceeds all criteria

### Model Behavior Control
- **Temperature 0.2**: Reduces randomness for scoring consistency
- **Max Tokens 1500**: Allows detailed explanations (≤300 words)
- **JSON Mode**: Enforces structured output for reliable parsing

## 4. Information Extraction & Criteria Detection

### Current Approach: Criteria-Guided Evaluation

The system uses **prompt-based criteria specification** rather than autonomous information extraction.

**Evaluation Process**:
```python
EVALUATION CRITERIA: {sub_criterion_description}
DOCUMENT TEXT: {extracted_text}

# AI evaluates document alignment with provided criteria
→ Score: 1-7
→ Explanation: Evidence-based reasoning
```

**Example Flow**:
- **Criterion**: "MC1: Recyclability - Assessment of material recyclability rate"
- **Document**: Contains "80% recycled content, Type II recycling certification"
- **AI Output**: Score 6/7 with explanation citing specific evidence

### Information Extraction Capabilities (Current)
- **Qualitative Analysis**: Contextual understanding of sustainability concepts
- **Evidence Mapping**: Links document content to evaluation criteria
- **Comparative Assessment**: Benchmarks against scoring rubric

### Future Enhancement: Named Entity Recognition (NER)
**Potential Implementation**:
- **Tools**: spaCy, Hugging Face Transformers (BERT-based models)
- **Entities**: Equipment ("crane", "excavator"), Materials ("concrete", "steel"), Personnel ("worker", "engineer")
- **Relations**: Safety protocols, material specifications, compliance references
- **Use Cases**: 
  - Automated compliance checking
  - Risk factor identification
  - Quantitative metric extraction (percentages, certifications)

## 5. Information Exchange & Data Flow

### API-to-Database Pipeline

**Step 1: Document Upload & Extraction**
```python
# routes.py - edit_application
document_text = extract_text_from_file(document_path, file_type)
```

**Step 2: OpenAI API Integration**
```python
# utils/ai_evaluator.py - evaluate_document_with_ai
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "system", "content": system_prompt},
              {"role": "user", "content": evaluation_prompt}],
    temperature=0.2,
    response_format={"type": "json_object"},
    max_tokens=1500
)

# Parse JSON response
result = json.loads(response.choices[0].message.content)
score = result.get("score")  # Integer 1-7
explanation = result.get("explanation")  # String
```

**Step 3: Database Persistence (SQLAlchemy ORM)**
```python
# routes.py - save to PostgreSQL
kpi_score = KPIScore(
    application_id=application_id,
    sub_criterion_id=sub_criterion_id,
    score=score,  # AI-generated score
    reasoning=explanation,  # AI-generated explanation
    document_path=file_path,
    is_ai_generated=True,
    is_manually_modified=False
)
db.session.add(kpi_score)
db.session.commit()
```

### Data Flow Architecture
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│   Document  │ →   │     Text     │ →   │   OpenAI    │ →   │  PostgreSQL  │
│  (PDF/DOCX) │     │  Extraction  │     │   GPT-4o    │     │  (kpi_score) │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
                                                │
                                                ↓
                                          JSON Response
                                          {score: 1-7,
                                           explanation: "..."}
```

### Error Handling & Resilience
- **Quota Errors (429)**: Fallback to score=4 (average) with manual review flag
- **Authentication Errors (401)**: Graceful degradation with user notification
- **Extraction Failures**: Encrypted PDF detection, encoding fallbacks
- **API Timeouts**: Retry logic with exponential backoff

## 6. System Strengths & Limitations

### Strengths ✅
1. **Multimodal Foundation**: GPT-4o supports future image/diagram analysis
2. **Structured Output**: JSON mode ensures reliable data parsing
3. **Low-Temperature Consistency**: Reduces scoring variability across evaluations
4. **Comprehensive Error Handling**: Graceful degradation for API failures
5. **Bilingual Support**: Evaluation criteria available in Turkish and English

### Current Limitations ⚠️
1. **No Embedding/Vector Search**: Cannot process very long documents efficiently
2. **No Fine-Tuning**: Generic model not optimized for construction domain
3. **No Entity Extraction**: Lacks explicit NER for quantitative data mining
4. **Single Document Analysis**: No cross-document comparative analysis
5. **No Confidence Scoring**: AI doesn't provide uncertainty estimates

### Future Development Roadmap 🚀
1. **RAG Implementation**: Vector database + chunk-based retrieval for long documents
2. **Domain Fine-Tuning**: Construction-specific GPT model training
3. **NER Integration**: Automated entity and relation extraction
4. **Multi-Document Analysis**: Comparative evaluation across contractor portfolios
5. **Confidence Intervals**: Bayesian scoring with uncertainty quantification
6. **Vision Integration**: Leverage GPT-4o for blueprint/diagram analysis

## 7. Academic & Research Context

### Relevant Methodologies
- **Information Extraction (IE)**: Entity recognition, relation extraction, event detection
- **Information Exchange**: Document classification, indexing, search engine optimization
- **Knowledge Discovery**: Pattern recognition, predictive analytics, risk modeling
- **Downstream Applications**: Compliance checking, automated auditing, decision support systems

### Theoretical Foundations
- **Natural Language Understanding (NLU)**: Semantic comprehension via transformer architectures
- **Few-Shot Learning**: Prompt-based task specification without fine-tuning
- **Multi-Criteria Decision Analysis (MCDA)**: Integration of AI scoring with TOPSIS ranking

# Recent Changes

- October 15, 2025: AI Architecture documentation added - comprehensive technical methodology covering vectorisation, ML models, information extraction, and API-to-database data flow
- October 14, 2025: Edit application route'una kriter çevirileri eklendi - doküman yükleme ekranında artık İngilizce açıklamalar gösteriliyor
- October 14, 2025: Component Circularity ve Energy Circularity kriter açıklamaları güncellendi - İngilizce akademik açıklamalar eklendi
- October 14, 2025: Material Circularity alt kriterlerinin İngilizce isimleri güncellendi - MC1-MC5 için yeni akademik terminoloji eklendi
- October 14, 2025: Material Circularity, Resource Consumption ve Total Material Consumption açıklamaları güncellendi - akademik derinlik ve netlik artırıldı
- October 14, 2025: Custom dosya yükleme butonları eklendi - "Dosya Seç" ve "Dosya seçilmedi" metinleri artık dil seçeneğine göre çevriliyor
- October 14, 2025: Proje detay sayfasına "Expectations" bölümü eklendi - owner'ın girdiği beklentiler description'ın altında görüntüleniyor
- October 14, 2025: Contractor proje erişim izni genişletildi - başvuru yapmamış yükleniciler de "View Details" ile proje detaylarını görebiliyor
- October 14, 2025: İngilizce çeviri sistemi tamamlandı - contractor başvuru formunda tüm Türkçe metinler (alt kriterler, göster/gizle, KPI başlıkları) çevrildi
- October 14, 2025: Sub-criterion açıklamaları için İngilizce çeviri eklendi - Component Circularity gibi açıklamalar artık İngilizce gösteriliyor
- October 14, 2025: Sticky navbar eklendi - scroll yaparken navbar ekranın üstünde sabit kalıyor
- October 14, 2025: Unsaved changes uyarı sistemi eklendi - kaydedilmemiş değişiklikler varken sayfa değiştirildiğinde modal uyarı gösteriliyor
- October 14, 2025: Wireframe menüsü navbar'dan kaldırıldı - son kullanıcılar için gereksiz teknik dokümantasyon menüsü temizlendi
- October 14, 2025: TOPSIS skor gösterimi 6 ondalık basamağa düşürüldü - daha okunabilir skor formatı