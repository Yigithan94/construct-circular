#!/usr/bin/env python3
"""
PDF Converter for Technical Analysis Report
Converts the technical_analysis.md file to a professional PDF document
"""

import os
import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

def markdown_to_html(markdown_file):
    """Convert markdown file to HTML with proper formatting"""
    with open(markdown_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Configure markdown extensions for better formatting
    md = markdown.Markdown(extensions=[
        'extra',
        'codehilite',
        'toc',
        'tables',
        'fenced_code'
    ])
    
    html_content = md.convert(md_content)
    
    # Create full HTML document with proper styling
    full_html = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Construct Circular - Teknik Analiz Raporu</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                line-height: 1.6;
                color: #2c3e50;
                max-width: 210mm;
                margin: 0 auto;
                padding: 20mm;
                background: white;
            }}
            
            h1 {{
                color: #1a202c;
                font-size: 2.5em;
                font-weight: 700;
                border-bottom: 3px solid #3182ce;
                padding-bottom: 10px;
                margin-bottom: 30px;
                page-break-after: avoid;
            }}
            
            h2 {{
                color: #2d3748;
                font-size: 1.8em;
                font-weight: 600;
                margin-top: 40px;
                margin-bottom: 20px;
                border-left: 4px solid #3182ce;
                padding-left: 15px;
                page-break-after: avoid;
            }}
            
            h3 {{
                color: #4a5568;
                font-size: 1.4em;
                font-weight: 500;
                margin-top: 30px;
                margin-bottom: 15px;
                page-break-after: avoid;
            }}
            
            h4 {{
                color: #718096;
                font-size: 1.2em;
                font-weight: 500;
                margin-top: 25px;
                margin-bottom: 10px;
                page-break-after: avoid;
            }}
            
            p {{
                margin-bottom: 15px;
                text-align: justify;
                hyphens: auto;
            }}
            
            ul, ol {{
                margin-bottom: 20px;
                padding-left: 25px;
            }}
            
            li {{
                margin-bottom: 8px;
                line-height: 1.5;
            }}
            
            strong {{
                color: #2d3748;
                font-weight: 600;
            }}
            
            code {{
                background-color: #f7fafc;
                color: #e53e3e;
                padding: 2px 6px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
            }}
            
            pre {{
                background-color: #f8f9fa;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
                overflow-x: auto;
                page-break-inside: avoid;
            }}
            
            pre code {{
                background: none;
                color: #2d3748;
                padding: 0;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                page-break-inside: avoid;
            }}
            
            th, td {{
                border: 1px solid #e2e8f0;
                padding: 12px;
                text-align: left;
            }}
            
            th {{
                background-color: #f7fafc;
                font-weight: 600;
                color: #2d3748;
            }}
            
            blockquote {{
                border-left: 4px solid #bee3f8;
                background-color: #f0f8ff;
                padding: 15px 20px;
                margin: 20px 0;
                font-style: italic;
            }}
            
            .page-break {{
                page-break-before: always;
            }}
            
            .no-break {{
                page-break-inside: avoid;
            }}
            
            .header-info {{
                text-align: center;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                margin: -20mm -20mm 30px -20mm;
                border-radius: 0 0 15px 15px;
            }}
            
            .footer-info {{
                text-align: center;
                border-top: 2px solid #e2e8f0;
                padding-top: 20px;
                margin-top: 40px;
                color: #718096;
                font-size: 0.9em;
            }}
            
            .highlight {{
                background-color: #fef5e7;
                border-left: 4px solid #f6ad55;
                padding: 15px;
                margin: 20px 0;
            }}
            
            .metrics-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin: 20px 0;
            }}
            
            .metric-box {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid #3182ce;
            }}
            
            @page {{
                size: A4;
                margin: 15mm;
                
                @top-center {{
                    content: "Construct Circular - Teknik Analiz Raporu";
                    font-family: 'Inter', sans-serif;
                    font-size: 10pt;
                    color: #718096;
                }}
                
                @bottom-center {{
                    content: "Sayfa " counter(page) " / " counter(pages);
                    font-family: 'Inter', sans-serif;
                    font-size: 10pt;
                    color: #718096;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header-info">
            <h1 style="color: white; border: none; margin: 0;">Construct Circular</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.2em;">Kapsamlı Teknik Analiz Raporu</p>
        </div>
        
        {html_content}
        
        <div class="footer-info">
            <p><strong>Yıldız Teknik Üniversitesi - TÜBİTAK Destekli Proje</strong></p>
            <p>Bu rapor, Construct Circular platformunun teknik mimarisini ve kod analizini içermektedir.</p>
        </div>
    </body>
    </html>
    """
    
    return full_html

def create_pdf(html_content, output_file):
    """Convert HTML content to PDF with professional styling"""
    
    # Custom CSS for better PDF formatting
    pdf_css = CSS(string='''
        @page {
            size: A4;
            margin: 15mm;
        }
        
        body {
            font-size: 11pt;
            line-height: 1.4;
        }
        
        h1 { font-size: 18pt; }
        h2 { font-size: 16pt; }
        h3 { font-size: 14pt; }
        h4 { font-size: 12pt; }
        
        pre, code {
            font-size: 9pt;
        }
        
        table {
            font-size: 10pt;
        }
    ''')
    
    # Create font configuration
    font_config = FontConfiguration()
    
    # Generate PDF
    html_doc = HTML(string=html_content)
    html_doc.write_pdf(
        output_file,
        stylesheets=[pdf_css],
        font_config=font_config,
        optimize_images=True
    )

def main():
    """Main function to convert markdown to PDF"""
    input_file = 'technical_analysis.md'
    output_file = 'Construct_Circular_Teknik_Analiz_Raporu.pdf'
    
    print("📄 Teknik analiz raporu PDF'e dönüştürülüyor...")
    
    try:
        # Check if input file exists
        if not os.path.exists(input_file):
            print(f"❌ Hata: {input_file} dosyası bulunamadı!")
            return
        
        # Convert markdown to HTML
        print("🔄 Markdown HTML'e dönüştürülüyor...")
        html_content = markdown_to_html(input_file)
        
        # Create PDF
        print("🔄 PDF oluşturuluyor...")
        create_pdf(html_content, output_file)
        
        print(f"✅ PDF başarıyla oluşturuldu: {output_file}")
        print(f"📊 Dosya boyutu: {os.path.getsize(output_file) / 1024:.1f} KB")
        
    except Exception as e:
        print(f"❌ Hata oluştu: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()