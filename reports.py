from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, send_file, make_response
from flask_login import login_required, current_user
from models import Project, Criterion, SubCriterion, Document, User, db, ProjectStatus, ProjectApplication, ApplicationStatus, CriterionEvaluation, Alternative, DecisionMatrix
from flask_babel import gettext as _
import io
import base64
from datetime import datetime
import logging
# Conditional WeasyPrint import
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError as e:
    print(f"WeasyPrint import failed in reports.py: {e}")
    WEASYPRINT_AVAILABLE = False
    HTML = None

# Conditional NumPy import
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError as e:
    print(f"NumPy import failed in reports.py: {e}")
    NUMPY_AVAILABLE = False
    np = None

# Conditional matplotlib import
try:
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError as e:
    print(f"Matplotlib import failed in reports.py: {e}")
    MATPLOTLIB_AVAILABLE = False
    plt = None
    matplotlib = None

logger = logging.getLogger(__name__)

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/project/<int:project_id>/topsis-comparison', methods=['GET'])
@login_required
def topsis_comparison(project_id):
    """TOPSIS karşılaştırmalı analiz raporu görüntüleme"""
    project = Project.query.get_or_404(project_id)

    # Proje sahibi veya admin değilse erişimi engelle
    if not (current_user.id == project.user_id or current_user.is_administrator()):
        flash(_('Bu sayfaya erişim yetkiniz yok.'), 'error')
        return redirect(url_for('main.dashboard'))

    # Projeye ait başvuruları TOPSIS puanlarına göre sırala
    applications = ProjectApplication.query.filter_by(project_id=project_id)\
        .order_by(ProjectApplication.topsis_score.desc().nullslast())\
        .all()

    if not applications or len(applications) < 2:
        flash(_('En az 2 başvuru olması gerekmektedir.'), 'warning')
        return redirect(url_for('main.view_project', project_id=project_id))
    
    # Kriterlere göre puanları hesapla
    criterion_scores = {}
    subcriterion_scores = {}
    
    # Kriter puanları için veri hesapla
    for criterion in project.selected_criteria:
        # Her kriter için başvuruların puanlarını topla
        scores = []
        for app in applications:
            # Criterion için DecisionMatrix kayıtlarını al
            decisions = DecisionMatrix.query.join(SubCriterion)\
                .filter(DecisionMatrix.application_id == app.id,
                        SubCriterion.criterion_id == criterion.id)\
                .all()
            
            if decisions:
                # Alt kriterlerin ortalama puanını al
                avg_score = sum(d.score for d in decisions) / len(decisions)
                scores.append((app.id, avg_score))
        
        # Puanları normalize et ve rank'leri hesapla
        if scores:
            max_score = max(s[1] for s in scores)
            for app_id, score in scores:
                normalized_score = score / 7  # 7 maksimum puan
                percentage = (score / max_score) * 100
                rank = sorted(scores, key=lambda x: x[1], reverse=True).index((app_id, score)) + 1
                criterion_scores[(app_id, criterion.id)] = {
                    'score': int(score),
                    'normalized_score': normalized_score,
                    'percentage': percentage,
                    'rank': rank
                }
    
    # Alt kriterler için aynı hesaplamayı yap
    for sub in SubCriterion.query.all():
        scores = []
        for app in applications:
            decision = DecisionMatrix.query.filter_by(
                application_id=app.id,
                sub_criterion_id=sub.id
            ).first()
            
            if decision:
                scores.append((app.id, decision.score))
        
        if scores:
            max_score = max(s[1] for s in scores)
            for app_id, score in scores:
                normalized_score = score / 7  # 7 maksimum puan
                percentage = (score / max_score) * 100
                rank = sorted(scores, key=lambda x: x[1], reverse=True).index((app_id, score)) + 1
                subcriterion_scores[(app_id, sub.id)] = {
                    'score': int(score),
                    'normalized_score': normalized_score,
                    'percentage': percentage,
                    'rank': rank
                }
    
    return render_template(
        'reports/topsis_comparison.html',
        project=project,
        applications=applications,
        ranked_applications=applications,
        criterion_scores=criterion_scores,
        subcriterion_scores=subcriterion_scores
    )


@reports_bp.route('/project/<int:project_id>/topsis-report-pdf', methods=['GET'])
@login_required
def download_topsis_report(project_id):
    """TOPSIS karşılaştırmalı analiz raporunu PDF olarak indir"""
    project = Project.query.get_or_404(project_id)

    # Proje sahibi veya admin değilse erişimi engelle
    if not (current_user.id == project.user_id or current_user.is_administrator()):
        flash(_('Bu sayfaya erişim yetkiniz yok.'), 'error')
        return redirect(url_for('main.dashboard'))

    # Projeye ait başvuruları TOPSIS puanlarına göre sırala
    applications = ProjectApplication.query.filter_by(project_id=project_id)\
        .order_by(ProjectApplication.topsis_score.desc())\
        .all()

    if not applications or len(applications) < 2:
        flash(_('En az 2 başvuru olması gerekmektedir.'), 'warning')
        return redirect(url_for('main.view_project', project_id=project_id))
    
    # Kriter puanlarını hesapla (topsis_comparison route'u ile aynı)
    criterion_scores = {}
    subcriterion_scores = {}
    
    # Kriter puanları için veri hesapla
    for criterion in project.selected_criteria:
        scores = []
        for app in applications:
            decisions = DecisionMatrix.query.join(SubCriterion)\
                .filter(DecisionMatrix.application_id == app.id,
                        SubCriterion.criterion_id == criterion.id)\
                .all()
            
            if decisions:
                avg_score = sum(d.score for d in decisions) / len(decisions)
                scores.append((app.id, avg_score))
        
        if scores:
            max_score = max(s[1] for s in scores)
            for app_id, score in scores:
                normalized_score = score / 7
                percentage = (score / max_score) * 100
                rank = sorted(scores, key=lambda x: x[1], reverse=True).index((app_id, score)) + 1
                criterion_scores[(app_id, criterion.id)] = {
                    'score': int(score),
                    'normalized_score': normalized_score,
                    'percentage': percentage,
                    'rank': rank
                }
    
    # Alt kriterler için aynı hesaplamayı yap
    for sub in SubCriterion.query.all():
        scores = []
        for app in applications:
            decision = DecisionMatrix.query.filter_by(
                application_id=app.id,
                sub_criterion_id=sub.id
            ).first()
            
            if decision:
                scores.append((app.id, decision.score))
        
        if scores:
            max_score = max(s[1] for s in scores)
            for app_id, score in scores:
                normalized_score = score / 7
                percentage = (score / max_score) * 100
                rank = sorted(scores, key=lambda x: x[1], reverse=True).index((app_id, score)) + 1
                subcriterion_scores[(app_id, sub.id)] = {
                    'score': int(score),
                    'normalized_score': normalized_score,
                    'percentage': percentage,
                    'rank': rank
                }
    
    # Pasta grafiği oluştur (TOPSIS puanlarına göre)
    pie_chart_image = None
    radar_chart_image = None
    
    if MATPLOTLIB_AVAILABLE and NUMPY_AVAILABLE:
        try:
            # Pasta grafiği için veri hazırla
            labels = []
            sizes = []
            colors_list = ['#2ecc71', '#3498db', '#9b59b6', '#e74c3c', '#f39c12', '#1abc9c', '#34495e']
            
            for i, app in enumerate(applications):
                contractor_name = app.contractor.company_name or app.contractor.username
                labels.append(contractor_name)
                sizes.append(app.topsis_score if app.topsis_score else 0)
            
            # Normalize sizes for pie chart
            total = sum(sizes) if sum(sizes) > 0 else 1
            
            # Pasta grafiği oluştur
            fig, ax = plt.subplots(figsize=(6, 5))
            
            # Renkleri ayarla
            chart_colors = colors_list[:len(labels)]
            
            # Pasta dilimlerini oluştur
            wedges, texts, autotexts = ax.pie(
                sizes, 
                labels=None,
                autopct=lambda pct: f'{pct:.1f}%' if pct > 5 else '',
                colors=chart_colors,
                startangle=90,
                explode=[0.05 if i == 0 else 0 for i in range(len(sizes))],
                shadow=False
            )
            
            # Legend ekle (sağ tarafta)
            ax.legend(
                wedges, 
                [f'{label} ({size:.4f})' for label, size in zip(labels, sizes)],
                title="Firmalar",
                loc="center left",
                bbox_to_anchor=(1, 0, 0.5, 1),
                fontsize=8
            )
            
            plt.tight_layout()
            
            # Grafiği base64 formatına dönüştür
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
            img_buffer.seek(0)
            pie_chart_image = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            plt.close()
            
        except Exception as e:
            logger.error(f"Pasta grafiği oluşturma hatası: {str(e)}")
    else:
        logger.warning("Matplotlib veya NumPy mevcut değil, grafik oluşturulamıyor")
    
    # Logo'yu base64 olarak oku
    logo_base64 = None
    try:
        import os
        logo_path = os.path.join(current_app.root_path, 'static', 'images', 'construct-circular-new-logo.png')
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as logo_file:
                logo_base64 = base64.b64encode(logo_file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Logo okuma hatası: {str(e)}")
    
    # PDF için template'i render et
    html_content = render_template(
        'reports/topsis_pdf_report.html',
        project=project,
        applications=applications,
        ranked_applications=applications,
        criterion_scores=criterion_scores,
        subcriterion_scores=subcriterion_scores,
        radar_chart_image=radar_chart_image,
        pie_chart_image=pie_chart_image,
        logo_base64=logo_base64,
        now=datetime.now()
    )
    
    # HTML'i PDF'e dönüştür
    try:
        if not WEASYPRINT_AVAILABLE:
            flash(_('PDF oluşturma özelliği şu anda kullanılamıyor.'), 'error')
            return redirect(url_for('reports.topsis_comparison', project_id=project_id))
            
        pdf_file = io.BytesIO()
        HTML(string=html_content).write_pdf(pdf_file)
        pdf_file.seek(0)
        
        # PDF'i response olarak gönder
        response = make_response(pdf_file.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=topsis_rapor_{project_id}.pdf'
        
        return response
    
    except Exception as e:
        logger.error(f"PDF oluşturma hatası: {str(e)}")
        flash(_('PDF oluşturulurken bir hata oluştu: {error}').format(error=str(e)), 'error')
        return redirect(url_for('reports.topsis_comparison', project_id=project_id))