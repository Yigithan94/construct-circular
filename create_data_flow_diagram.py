#!/usr/bin/env python3
"""
Data Flow Diagram Generator for Construct Circular
Creates comprehensive database relationship and data flow diagrams
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np
from datetime import datetime

def create_database_erd():
    """Create Entity Relationship Diagram for database tables"""
    
    # Set up the figure with larger size for better visibility
    fig, ax = plt.subplots(figsize=(20, 16))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 16)
    ax.axis('off')
    
    # Define colors for different entity types
    colors = {
        'user': '#3498db',      # Blue for user-related
        'project': '#2ecc71',   # Green for project-related  
        'application': '#e74c3c', # Red for application-related
        'evaluation': '#f39c12',  # Orange for evaluation-related
        'document': '#9b59b6',    # Purple for document-related
        'association': '#95a5a6'  # Gray for association tables
    }
    
    # Define entity positions and properties
    entities = {
        # Core entities
        'User': {'pos': (2, 14), 'size': (2.5, 1.8), 'color': colors['user'], 
                'fields': ['id (PK)', 'username', 'email', 'password_hash', 'role', 'is_admin', 'company_name', 'contractor_specialization']},
        
        'Project': {'pos': (8, 14), 'size': (3, 2), 'color': colors['project'],
                   'fields': ['id (PK)', 'name', 'description', 'expectations', 'budget_range_min/max', 'start_date', 'deadline', 'location', 'status', 'user_id (FK)']},
        
        'ProjectApplication': {'pos': (14, 14), 'size': (3, 1.8), 'color': colors['application'],
                              'fields': ['id (PK)', 'project_id (FK)', 'contractor_id (FK)', 'status', 'cover_letter', 'proposed_budget', 'topsis_score']},
        
        # Criteria and evaluation
        'Criterion': {'pos': (2, 11), 'size': (2.5, 1.5), 'color': colors['evaluation'],
                     'fields': ['id (PK)', 'name', 'description', 'weight', 'is_cost', 'weight_low/medium/high']},
        
        'SubCriterion': {'pos': (8, 11), 'size': (3, 1.5), 'color': colors['evaluation'],
                        'fields': ['id (PK)', 'name', 'description', 'weight', 'detail_weight', 'criterion_id (FK)', 'has_kpi']},
        
        'KeyPerformanceIndicator': {'pos': (14, 11), 'size': (3, 1.5), 'color': colors['evaluation'],
                                   'fields': ['id (PK)', 'name', 'description', 'ai_evaluation_criteria', 'sub_criterion_id (FK)', 'use_ai_evaluation']},
        
        # Documents and scoring
        'Document': {'pos': (2, 8), 'size': (2.5, 1.5), 'color': colors['document'],
                    'fields': ['id (PK)', 'filename', 'file_path', 'file_type', 'file_size', 'project_id (FK)', 'application_id (FK)']},
        
        'KPIDocument': {'pos': (8, 8), 'size': (3, 1.5), 'color': colors['document'],
                       'fields': ['id (PK)', 'filename', 'file_path', 'ai_evaluated', 'ai_score', 'kpi_id (FK)', 'application_id (FK)']},
        
        'KPIScore': {'pos': (14, 8), 'size': (3, 1.2), 'color': colors['evaluation'],
                    'fields': ['id (PK)', 'application_id (FK)', 'kpi_id (FK)', 'score']},
        
        # Advanced evaluation
        'Alternative': {'pos': (2, 5), 'size': (2.5, 1.2), 'color': colors['project'],
                       'fields': ['id (PK)', 'name', 'description', 'project_id (FK)']},
        
        'CriterionEvaluation': {'pos': (8, 5), 'size': (3, 1.5), 'color': colors['evaluation'],
                               'fields': ['id (PK)', 'alternative_id (FK)', 'criterion_id (FK)', 'application_id (FK)', 'low', 'medium', 'high']},
        
        'DecisionMatrix': {'pos': (14, 5), 'size': (3, 1.2), 'color': colors['evaluation'],
                          'fields': ['id (PK)', 'project_application_id (FK)', 'matrix_data', 'topsis_score']}
    }
    
    # Association tables
    association_tables = {
        'project_criteria': {'pos': (5, 12.5), 'size': (2, 0.8), 'color': colors['association'],
                            'fields': ['project_id (FK)', 'criterion_id (FK)']},
        'project_subcriteria': {'pos': (11, 12.5), 'size': (2, 0.8), 'color': colors['association'],
                               'fields': ['project_id (FK)', 'sub_criterion_id (FK)']}
    }
    
    # Draw entities
    drawn_entities = {}
    for name, props in entities.items():
        x, y = props['pos']
        width, height = props['size']
        
        # Create fancy box for entity
        box = FancyBboxPatch((x-width/2, y-height/2), width, height,
                            boxstyle="round,pad=0.1", 
                            facecolor=props['color'], 
                            edgecolor='black',
                            alpha=0.8,
                            linewidth=1.5)
        ax.add_patch(box)
        
        # Add entity name (bold)
        ax.text(x, y+height/2-0.2, name, ha='center', va='center', 
                fontsize=10, fontweight='bold', color='white')
        
        # Add fields
        field_text = '\n'.join(props['fields'][:6])  # Limit to 6 fields for space
        if len(props['fields']) > 6:
            field_text += '\n...'
            
        ax.text(x, y-0.1, field_text, ha='center', va='center', 
                fontsize=7, color='white', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.3))
        
        drawn_entities[name] = (x, y, width, height)
    
    # Draw association tables
    for name, props in association_tables.items():
        x, y = props['pos']
        width, height = props['size']
        
        box = FancyBboxPatch((x-width/2, y-height/2), width, height,
                            boxstyle="round,pad=0.05", 
                            facecolor=props['color'], 
                            edgecolor='black',
                            alpha=0.6,
                            linewidth=1)
        ax.add_patch(box)
        
        ax.text(x, y+0.2, name, ha='center', va='center', 
                fontsize=8, fontweight='bold')
        
        field_text = '\n'.join(props['fields'])
        ax.text(x, y-0.1, field_text, ha='center', va='center', 
                fontsize=6)
    
    # Define relationships
    relationships = [
        # User relationships
        ('User', 'Project', '1:N', 'creates'),
        ('User', 'ProjectApplication', '1:N', 'applies'),
        
        # Project relationships  
        ('Project', 'ProjectApplication', '1:N', 'receives'),
        ('Project', 'Document', '1:N', 'has'),
        ('Project', 'Alternative', '1:N', 'has'),
        
        # Criteria relationships
        ('Criterion', 'SubCriterion', '1:N', 'contains'),
        ('SubCriterion', 'KeyPerformanceIndicator', '1:N', 'defines'),
        
        # Application relationships
        ('ProjectApplication', 'Document', '1:N', 'includes'),
        ('ProjectApplication', 'KPIDocument', '1:N', 'uploads'),
        ('ProjectApplication', 'KPIScore', '1:N', 'scored'),
        ('ProjectApplication', 'CriterionEvaluation', '1:N', 'evaluated'),
        ('ProjectApplication', 'DecisionMatrix', '1:1', 'generates'),
        
        # KPI relationships
        ('KeyPerformanceIndicator', 'KPIDocument', '1:N', 'evaluates'),
        ('KeyPerformanceIndicator', 'KPIScore', '1:N', 'scores'),
        
        # Evaluation relationships
        ('Alternative', 'CriterionEvaluation', '1:N', 'evaluated_by'),
        ('Criterion', 'CriterionEvaluation', '1:N', 'evaluates')
    ]
    
    # Draw relationships
    for rel in relationships:
        entity1, entity2, cardinality, label = rel
        if entity1 in drawn_entities and entity2 in drawn_entities:
            x1, y1, w1, h1 = drawn_entities[entity1]
            x2, y2, w2, h2 = drawn_entities[entity2]
            
            # Calculate connection points
            if x1 < x2:  # Left to right
                start_x, start_y = x1 + w1/2, y1
                end_x, end_y = x2 - w2/2, y2
            elif x1 > x2:  # Right to left
                start_x, start_y = x1 - w1/2, y1
                end_x, end_y = x2 + w2/2, y2
            else:  # Same x, vertical
                if y1 > y2:  # Top to bottom
                    start_x, start_y = x1, y1 - h1/2
                    end_x, end_y = x2, y2 + h2/2
                else:  # Bottom to top
                    start_x, start_y = x1, y1 + h1/2
                    end_x, end_y = x2, y2 - h2/2
            
            # Draw arrow
            ax.annotate('', xy=(end_x, end_y), xytext=(start_x, start_y),
                       arrowprops=dict(arrowstyle='->', color='black', lw=1.2))
            
            # Add cardinality label
            mid_x, mid_y = (start_x + end_x) / 2, (start_y + end_y) / 2
            ax.text(mid_x, mid_y + 0.1, cardinality, ha='center', va='bottom', 
                   fontsize=7, color='red', fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
    
    # Add title and legend
    ax.text(10, 15.5, 'Construct Circular - Veritabanı İlişki Diagramı (ERD)', 
            ha='center', va='center', fontsize=16, fontweight='bold')
    
    # Create legend
    legend_elements = [
        mpatches.Patch(color=colors['user'], label='Kullanıcı Tabloları'),
        mpatches.Patch(color=colors['project'], label='Proje Tabloları'),
        mpatches.Patch(color=colors['application'], label='Başvuru Tabloları'),
        mpatches.Patch(color=colors['evaluation'], label='Değerlendirme Tabloları'),
        mpatches.Patch(color=colors['document'], label='Belge Tabloları'),
        mpatches.Patch(color=colors['association'], label='İlişki Tabloları')
    ]
    
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.15))
    
    # Add database statistics
    stats_text = f"""
Veritabanı İstatistikleri:
• Toplam Tablo: 12 ana tablo + 2 ilişki tablosu
• Ana Varlıklar: User, Project, ProjectApplication
• Değerlendirme Sistemi: TOPSIS + AI + KPI
• İlişki Türleri: 1:1, 1:N, M:N
• Oluşturulma: {datetime.now().strftime('%d %B %Y')}
"""
    
    ax.text(1, 2, stats_text, ha='left', va='top', fontsize=9,
            bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    return fig

def create_data_flow_diagram():
    """Create Data Flow Diagram showing system processes"""
    
    fig, ax = plt.subplots(figsize=(18, 14))
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 14)
    ax.axis('off')
    
    # Define process colors
    process_colors = {
        'external': '#34495e',    # Dark blue for external entities
        'process': '#2ecc71',     # Green for processes  
        'datastore': '#e74c3c',   # Red for data stores
        'flow': '#3498db'         # Blue for data flows
    }
    
    # External entities (squares)
    external_entities = {
        'Şirket': {'pos': (2, 12), 'size': (2, 1)},
        'Müteahhit': {'pos': (2, 8), 'size': (2, 1)},
        'Admin': {'pos': (2, 4), 'size': (2, 1)},
        'AI Sistemi': {'pos': (16, 10), 'size': (2, 1)}
    }
    
    # Processes (circles)
    processes = {
        'P1: Kullanıcı\nKimlik Doğrulama': {'pos': (6, 10), 'radius': 1.2},
        'P2: Proje\nYönetimi': {'pos': (10, 12), 'radius': 1.2},
        'P3: Başvuru\nİşleme': {'pos': (10, 8), 'radius': 1.2},
        'P4: AI\nDeğerlendirme': {'pos': (14, 8), 'radius': 1.2},
        'P5: TOPSIS\nAnalizi': {'pos': (10, 4), 'radius': 1.2},
        'P6: Rapor\nOluşturma': {'pos': (6, 4), 'radius': 1.2}
    }
    
    # Data stores (open rectangles)
    data_stores = {
        'D1: Kullanıcılar': {'pos': (6, 12.5), 'size': (2.5, 0.6)},
        'D2: Projeler': {'pos': (10, 10), 'size': (2.5, 0.6)},
        'D3: Başvurular': {'pos': (14, 10), 'size': (2.5, 0.6)},
        'D4: Kriterler': {'pos': (6, 6), 'size': (2.5, 0.6)},
        'D5: Belgeler': {'pos': (10, 6), 'size': (2.5, 0.6)},
        'D6: Değerlendirmeler': {'pos': (14, 6), 'size': (2.5, 0.6)},
        'D7: Raporlar': {'pos': (6, 2), 'size': (2.5, 0.6)}
    }
    
    # Draw external entities (rectangles)
    for name, props in external_entities.items():
        x, y = props['pos']
        width, height = props['size']
        
        rect = plt.Rectangle((x-width/2, y-height/2), width, height,
                           facecolor=process_colors['external'], 
                           edgecolor='black', linewidth=2, alpha=0.8)
        ax.add_patch(rect)
        
        ax.text(x, y, name, ha='center', va='center', 
                fontsize=10, fontweight='bold', color='white')
    
    # Draw processes (circles)
    for name, props in processes.items():
        x, y = props['pos']
        radius = props['radius']
        
        circle = plt.Circle((x, y), radius, 
                          facecolor=process_colors['process'], 
                          edgecolor='black', linewidth=2, alpha=0.8)
        ax.add_patch(circle)
        
        ax.text(x, y, name, ha='center', va='center', 
                fontsize=9, fontweight='bold', color='white')
    
    # Draw data stores (open rectangles)
    for name, props in data_stores.items():
        x, y = props['pos']
        width, height = props['size']
        
        # Open rectangle (only left side closed)
        ax.plot([x-width/2, x-width/2], [y-height/2, y+height/2], 'k-', linewidth=3)
        ax.plot([x-width/2, x+width/2], [y-height/2, y-height/2], 'k-', linewidth=2)
        ax.plot([x-width/2, x+width/2], [y+height/2, y+height/2], 'k-', linewidth=2)
        
        # Fill
        rect = plt.Rectangle((x-width/2, y-height/2), width, height,
                           facecolor=process_colors['datastore'], 
                           alpha=0.3, edgecolor='none')
        ax.add_patch(rect)
        
        ax.text(x, y, name, ha='center', va='center', 
                fontsize=9, fontweight='bold')
    
    # Define data flows
    data_flows = [
        # Authentication flows
        ('Şirket', 'P1: Kullanıcı\nKimlik Doğrulama', 'Giriş Bilgileri'),
        ('Müteahhit', 'P1: Kullanıcı\nKimlik Doğrulama', 'Giriş Bilgileri'),
        ('P1: Kullanıcı\nKimlik Doğrulama', 'D1: Kullanıcılar', 'Kullanıcı Verisi'),
        
        # Project management flows
        ('Şirket', 'P2: Proje\nYönetimi', 'Proje Bilgileri'),
        ('P2: Proje\nYönetimi', 'D2: Projeler', 'Proje Verisi'),
        ('P2: Proje\nYönetimi', 'D4: Kriterler', 'Kriter Tanımları'),
        
        # Application flows
        ('Müteahhit', 'P3: Başvuru\nİşleme', 'Başvuru + Belgeler'),
        ('P3: Başvuru\nİşleme', 'D3: Başvurular', 'Başvuru Verisi'),
        ('P3: Başvuru\nİşleme', 'D5: Belgeler', 'Belge Dosyaları'),
        
        # AI evaluation flows
        ('D5: Belgeler', 'P4: AI\nDeğerlendirme', 'Belge İçeriği'),
        ('AI Sistemi', 'P4: AI\nDeğerlendirme', 'AI Analizi'),
        ('P4: AI\nDeğerlendirme', 'D6: Değerlendirmeler', 'AI Puanları'),
        
        # TOPSIS analysis flows
        ('D3: Başvurular', 'P5: TOPSIS\nAnalizi', 'Başvuru Verisi'),
        ('D4: Kriterler', 'P5: TOPSIS\nAnalizi', 'Kriter Ağırlıkları'),
        ('D6: Değerlendirmeler', 'P5: TOPSIS\nAnalizi', 'Değerlendirme Puanları'),
        ('P5: TOPSIS\nAnalizi', 'D6: Değerlendirmeler', 'TOPSIS Sonuçları'),
        
        # Reporting flows
        ('D6: Değerlendirmeler', 'P6: Rapor\nOluşturma', 'Analiz Sonuçları'),
        ('P6: Rapor\nOluşturma', 'D7: Raporlar', 'PDF Raporları'),
        ('P6: Rapor\nOluşturma', 'Şirket', 'Analiz Raporları'),
        ('P6: Rapor\nOluşturma', 'Admin', 'Sistem Raporları')
    ]
    
    # Helper function to get entity center
    def get_entity_center(name):
        if name in external_entities:
            return external_entities[name]['pos']
        elif name in processes:
            return processes[name]['pos']
        elif name in data_stores:
            return data_stores[name]['pos']
        return None
    
    # Draw data flows
    for flow in data_flows:
        start_entity, end_entity, label = flow
        start_pos = get_entity_center(start_entity)
        end_pos = get_entity_center(end_entity)
        
        if start_pos and end_pos:
            # Calculate arrow positions (avoid overlapping with entities)
            start_x, start_y = start_pos
            end_x, end_y = end_pos
            
            # Simple offset to avoid entity boundaries
            dx = end_x - start_x
            dy = end_y - start_y
            length = np.sqrt(dx**2 + dy**2)
            
            if length > 0:
                offset = 0.8  # Offset from entity edge
                start_x += (dx/length) * offset
                start_y += (dy/length) * offset
                end_x -= (dx/length) * offset
                end_y -= (dy/length) * offset
            
            # Draw arrow
            ax.annotate('', xy=(end_x, end_y), xytext=(start_x, start_y),
                       arrowprops=dict(arrowstyle='->', color=process_colors['flow'], 
                                     lw=1.5, alpha=0.8))
            
            # Add label
            mid_x, mid_y = (start_x + end_x) / 2, (start_y + end_y) / 2
            ax.text(mid_x, mid_y, label, ha='center', va='center', 
                   fontsize=7, color='black', fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.2", facecolor='white', 
                           alpha=0.9, edgecolor=process_colors['flow']))
    
    # Add title
    ax.text(9, 13.5, 'Construct Circular - Veri Akış Diagramı (DFD)', 
            ha='center', va='center', fontsize=16, fontweight='bold')
    
    # Add legend
    legend_elements = [
        mpatches.Patch(color=process_colors['external'], label='Dış Varlıklar (External Entities)'),
        mpatches.Patch(color=process_colors['process'], label='İşlemler (Processes)'),
        mpatches.Patch(color=process_colors['datastore'], label='Veri Depoları (Data Stores)'),
        mpatches.Patch(color=process_colors['flow'], label='Veri Akışları (Data Flows)')
    ]
    
    ax.legend(handles=legend_elements, loc='lower right', bbox_to_anchor=(0.98, 0.02))
    
    # Add process descriptions
    process_desc = """
Süreç Açıklamaları:
P1: Kullanıcı kimlik doğrulama ve yetkilendirme
P2: Proje oluşturma, düzenleme ve kriter tanımlama  
P3: Müteahhit başvurularını işleme ve belge yükleme
P4: AI tabanlı belge analizi ve otomatik puanlama
P5: Fuzzy TOPSIS çok kriterli karar analizi
P6: PDF rapor oluşturma ve görselleştirme
"""
    
    ax.text(0.5, 1, process_desc, ha='left', va='bottom', fontsize=8,
            bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    return fig

def create_system_architecture_diagram():
    """Create system architecture diagram"""
    
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Define layers
    layers = {
        'Sunum Katmanı\n(Presentation Layer)': {
            'pos': (8, 10.5), 'size': (14, 1.5), 'color': '#3498db',
            'components': ['HTML/CSS/JavaScript', 'Bootstrap UI', 'Jinja2 Templates', 'Multi-language Support']
        },
        'Uygulama Katmanı\n(Application Layer)': {
            'pos': (8, 8.5), 'size': (14, 1.5), 'color': '#2ecc71',
            'components': ['Flask Framework', 'Blueprint Architecture', 'Form Validation', 'Session Management']
        },
        'İş Mantığı Katmanı\n(Business Logic Layer)': {
            'pos': (8, 6.5), 'size': (14, 1.5), 'color': '#e74c3c',
            'components': ['TOPSIS Algorithm', 'AI Evaluation', 'Role-based Access', 'Draft System']
        },
        'Veri Erişim Katmanı\n(Data Access Layer)': {
            'pos': (8, 4.5), 'size': (14, 1.5), 'color': '#f39c12',
            'components': ['SQLAlchemy ORM', 'Database Models', 'Query Optimization', 'Transaction Management']
        },
        'Veri Katmanı\n(Data Layer)': {
            'pos': (8, 2.5), 'size': (14, 1.5), 'color': '#9b59b6',
            'components': ['PostgreSQL Database', 'File Storage', 'Document Management', 'Backup Systems']
        }
    }
    
    # External services
    external_services = {
        'OpenAI API': {'pos': (2, 6.5), 'size': (2.5, 1), 'color': '#1abc9c'},
        'Email Service': {'pos': (2, 4.5), 'size': (2.5, 1), 'color': '#e67e22'},
        'File Storage': {'pos': (14, 2.5), 'size': (2.5, 1), 'color': '#95a5a6'}
    }
    
    # Draw layers
    for name, props in layers.items():
        x, y = props['pos']
        width, height = props['size']
        
        # Main layer box
        rect = FancyBboxPatch((x-width/2, y-height/2), width, height,
                             boxstyle="round,pad=0.1", 
                             facecolor=props['color'], 
                             edgecolor='black',
                             alpha=0.7,
                             linewidth=2)
        ax.add_patch(rect)
        
        # Layer title
        ax.text(x, y+height/3, name, ha='center', va='center', 
                fontsize=12, fontweight='bold', color='white')
        
        # Components
        components_text = ' • '.join(props['components'])
        ax.text(x, y-height/4, components_text, ha='center', va='center', 
                fontsize=9, color='white', wrap=True)
    
    # Draw external services
    for name, props in external_services.items():
        x, y = props['pos']
        width, height = props['size']
        
        rect = FancyBboxPatch((x-width/2, y-height/2), width, height,
                             boxstyle="round,pad=0.1", 
                             facecolor=props['color'], 
                             edgecolor='black',
                             alpha=0.8,
                             linewidth=1.5)
        ax.add_patch(rect)
        
        ax.text(x, y, name, ha='center', va='center', 
                fontsize=10, fontweight='bold', color='white')
    
    # Draw connections
    connections = [
        ((2, 6.5), (8, 6.5)),  # OpenAI to Business Logic
        ((2, 4.5), (8, 4.5)),  # Email to Data Access
        ((14, 2.5), (8, 2.5))  # File Storage to Data Layer
    ]
    
    for start, end in connections:
        ax.annotate('', xy=end, xytext=start,
                   arrowprops=dict(arrowstyle='<->', color='black', lw=2))
    
    # Add title
    ax.text(8, 11.7, 'Construct Circular - Sistem Mimarisi', 
            ha='center', va='center', fontsize=16, fontweight='bold')
    
    # Add architecture notes
    arch_notes = """
Mimari Özellikler:
• Katmanlı Mimari (Layered Architecture)
• MVC Pattern (Model-View-Controller)
• RESTful API Design
• Modular Blueprint Structure
• Scalable Database Design
"""
    
    ax.text(0.5, 0.5, arch_notes, ha='left', va='bottom', fontsize=9,
            bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    return fig

def main():
    """Generate all diagrams"""
    
    print("Veri akış diagramları oluşturuluyor...")
    
    # Create diagrams
    print("1. Veritabanı ERD diagramı...")
    erd_fig = create_database_erd()
    erd_fig.savefig('Construct_Circular_Database_ERD.png', dpi=300, bbox_inches='tight')
    
    print("2. Veri akış diagramı...")
    dfd_fig = create_data_flow_diagram()
    dfd_fig.savefig('Construct_Circular_Data_Flow_Diagram.png', dpi=300, bbox_inches='tight')
    
    print("3. Sistem mimarisi diagramı...")
    arch_fig = create_system_architecture_diagram()
    arch_fig.savefig('Construct_Circular_System_Architecture.png', dpi=300, bbox_inches='tight')
    
    plt.close('all')
    
    print("✅ Tüm diagramlar başarıyla oluşturuldu:")
    print("📊 Construct_Circular_Database_ERD.png")
    print("🔄 Construct_Circular_Data_Flow_Diagram.png") 
    print("🏗️ Construct_Circular_System_Architecture.png")

if __name__ == "__main__":
    main()