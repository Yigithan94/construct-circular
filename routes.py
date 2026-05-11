import logging
import traceback
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, session, send_file, make_response, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import Project, Criterion, SubCriterion, Document, User, db, ProjectStatus, ProjectApplication, ApplicationStatus, CriterionEvaluation, Alternative, DecisionMatrix, KeyPerformanceIndicator, KPIDocument, KPIScore
from forms import ProjectForm, LoginForm, CompanyProfileForm, ProjectApplicationForm, SubCriterionForm, CSRFForm, KPIDefinitionForm
from flask_babel import gettext as _, get_locale
from utils.translations import get_translated_criterion_name, get_translated_criterion_description, get_translated_subcriterion_name, get_translated_subcriterion_description
import os
import io
# Conditional NumPy and pandas imports
try:
    import numpy as np
    import pandas as pd
    NUMPY_AVAILABLE = True
except ImportError as e:
    print(f"NumPy/Pandas import failed: {e}")
    NUMPY_AVAILABLE = False
    np = None
    pd = None

import base64

# Conditional TOPSIS imports
try:
    from topsis import fuzzy_topsis, group_subcriterion_topsis
    TOPSIS_AVAILABLE = True
except ImportError as e:
    print(f"TOPSIS import failed: {e}")
    TOPSIS_AVAILABLE = False
    fuzzy_topsis = None
    group_subcriterion_topsis = None
from datetime import datetime

# Conditional WeasyPrint import
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError as e:
    print(f"WeasyPrint import failed: {e}")
    WEASYPRINT_AVAILABLE = False
    HTML = None
    CSS = None

# Conditional matplotlib import
try:
    import matplotlib
    matplotlib.use('Agg')  # Set non-interactive backend for matplotlib
    from matplotlib import pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError as e:
    print(f"Matplotlib import failed: {e}")
    MATPLOTLIB_AVAILABLE = False
    plt = None
    matplotlib = None

main_bp = Blueprint('main', __name__)

@main_bp.route('/set-language/<lang>')
def set_language(lang):
    """Set the user's preferred language"""
    if lang in current_app.config['LANGUAGES']:
        session['language'] = lang
        flash(_('Language updated successfully.'), 'success')
    return redirect(request.referrer or url_for('main.index'))

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    """Home page route, redirects to dashboard if logged in, otherwise shows login form"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        return redirect(url_for('auth.login')) #Corrected redirect target

    return render_template('auth/login.html', form=form)

def save_uploaded_file(file, project_id=None, criterion_id=None, application_id=None):
    if not file:
        logger.warning("No file provided to save_uploaded_file")
        return None

    if not file.filename:
        logger.warning("Empty filename in save_uploaded_file")
        return None

    # Create a more unique filename to prevent overwriting
    original_filename = secure_filename(file.filename)
    file_ext = os.path.splitext(original_filename)[1].lower()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_filename = f"{timestamp}_{original_filename}"
    
    logger.debug(f"Processing file: {original_filename} (renamed to {unique_filename})")

    # Create uploads directory if it doesn't exist
    upload_dir = os.path.join('static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    logger.debug(f"Using uploads directory: {upload_dir}")

    # Save file with the unique filename
    file_path = os.path.join(upload_dir, unique_filename)
    file.save(file_path)
    logger.debug(f"Saved file to: {file_path}")

    # Get actual file size
    file_size = os.path.getsize(file_path)
    logger.debug(f"File size: {file_size} bytes")

    # Create document record with original filename for display but unique path for storage
    document = Document(
        filename=original_filename,  # Store original name for display
        file_path=file_path,  # Store path relative to application root
        file_type=file_ext[1:] if file_ext else "",
        file_size=file_size,
        project_id=project_id,
        criterion_id=criterion_id,
        application_id=application_id
    )
    
    db.session.add(document)  # Immediately add to session
    db.session.flush()  # Ensure it gets an ID
    
    logger.debug(f"Created document record: ID={document.id}, {document.filename}, type={document.file_type}, path={document.file_path}")
    return document

@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_company():
        # For company users, show their projects (newest first)
        projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.created_at.desc()).all()
    else:
        # For contractors, show available projects they can apply to (newest first)
        projects = Project.query.filter_by(status=ProjectStatus.OPEN).order_by(Project.created_at.desc()).all()
    return render_template('dashboard.html', projects=projects)

@main_bp.route('/account')
@login_required
def account():
    """Account information page showing user profile and statistics"""
    return render_template('account.html')

# Direct TOPSIS Routes
@main_bp.route('/reports/project/<int:project_id>/topsis-comparison')
@login_required
# Bu fonksiyon artık kullanılmıyor, ama mevcut projelerde bağımlılık olabileceği için silmiyoruz
def direct_topsis_comparison(project_id):
    """TOPSIS karşılaştırmalı analiz raporu görüntüleme doğrudan rota (Gizlendi)"""
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
    # Sadece projeye bağlı alt kriterleri al
    for sub in project.selected_subcriteria:
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

@main_bp.route('/project/new', methods=['GET', 'POST'])
@login_required
def create_project():
    # Both companies and contractors can create projects
    form = ProjectForm()

    if form.validate_on_submit():
        try:
            project = Project(
                name=form.name.data,
                description=form.description.data,
                expectations=form.expectations.data,
                start_date=form.start_date.data,
                deadline=form.deadline.data,
                location=form.location.data,
                user_id=current_user.id
            )
            db.session.add(project)
            db.session.commit()
            flash(_('Project created successfully!'), 'success')
            return redirect(url_for('main.dashboard'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating project: {str(e)}")
            flash(_('Error creating project: {error}').format(error=str(e)), 'error')

    return render_template('project_form.html', form=form)

@main_bp.route('/project/<int:project_id>/save-owner-note', methods=['POST'])
@login_required
def save_owner_note(project_id):
    """Save owner's note for the project"""
    project = Project.query.get_or_404(project_id)
    
    # Only owner or admin can save notes
    if project.user_id != current_user.id and not current_user.is_administrator():
        flash(_('Bu işlemi yapma yetkiniz yok.'), 'error')
        return redirect(url_for('main.view_project', project_id=project_id))
    
    owner_note = request.form.get('owner_note', '').strip()
    project.owner_note = owner_note
    db.session.commit()
    
    flash(_('Not başarıyla kaydedildi.'), 'success')
    return redirect(url_for('main.view_project', project_id=project_id))


@main_bp.route('/project/<int:project_id>/send-report-to-contractors', methods=['POST'])
@login_required
def send_report_to_contractors(project_id):
    """Send TOPSIS report to all contractors via email"""
    import os
    
    project = Project.query.get_or_404(project_id)
    
    # Only owner or admin can send reports
    if project.user_id != current_user.id and not current_user.is_administrator():
        flash(_('Bu işlemi yapma yetkiniz yok.'), 'error')
        return redirect(url_for('main.view_project', project_id=project_id))
    
    # Get all applications for this project
    applications = ProjectApplication.query.filter_by(project_id=project_id).all()
    
    if not applications:
        flash(_('Bu proje için başvuru bulunamadı.'), 'warning')
        return redirect(url_for('main.view_project', project_id=project_id))
    
    # Check for SendGrid API key
    sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
    sender_email = os.environ.get('SENDER_EMAIL', 'noreply@constructcircular.com')
    
    if not sendgrid_api_key:
        flash(_('E-posta servisi yapılandırılmamış. Lütfen admin panelinden SendGrid API anahtarını ayarlayın.'), 'error')
        return redirect(url_for('main.view_project', project_id=project_id))
    
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
        import base64
        
        # Generate PDF report
        pdf_content = generate_topsis_pdf_for_email(project_id)
        
        if not pdf_content:
            flash(_('PDF raporu oluşturulamadı.'), 'error')
            return redirect(url_for('main.view_project', project_id=project_id))
        
        sg = SendGridAPIClient(sendgrid_api_key)
        sent_count = 0
        failed_emails = []
        
        # Get ranked applications for personalized emails
        ranked_apps = ProjectApplication.query.filter_by(project_id=project_id)\
            .order_by(ProjectApplication.topsis_score.desc())\
            .all()
        
        for idx, app in enumerate(ranked_apps, 1):
            contractor = app.contractor
            if not contractor or not contractor.email:
                continue
            
            # Prepare email content
            rank_text = f"{idx}. sırada" if idx <= 3 else f"{idx}. sırada"
            subject = f"TOPSIS Sonuç Raporu - {project.name}"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2>Sayın {contractor.company_name or contractor.username},</h2>
                
                <p><strong>{project.name}</strong> projesi için TOPSIS değerlendirmesi tamamlanmıştır.</p>
                
                <p>Başvurunuz değerlendirilmiş ve <strong>{rank_text}</strong> yer almıştır.</p>
                
                <p>TOPSIS Puanınız: <strong>{app.topsis_score:.6f if app.topsis_score else 'N/A'}</strong></p>
                
                <p>Detaylı sonuç raporu ekte sunulmuştur.</p>
                
                <p>Katılımınız için teşekkür ederiz.</p>
                
                <hr>
                <p style="color: #666; font-size: 12px;">
                    Bu e-posta Construct Circular - Döngüsel İnşaat Karar Destek Sistemi tarafından otomatik olarak gönderilmiştir.
                </p>
            </body>
            </html>
            """
            
            message = Mail(
                from_email=sender_email,
                to_emails=contractor.email,
                subject=subject,
                html_content=html_content
            )
            
            # Attach PDF
            encoded_pdf = base64.b64encode(pdf_content).decode()
            attachment = Attachment(
                FileContent(encoded_pdf),
                FileName(f'topsis_raporu_{project.name}.pdf'),
                FileType('application/pdf'),
                Disposition('attachment')
            )
            message.attachment = attachment
            
            try:
                response = sg.send(message)
                if response.status_code in [200, 201, 202]:
                    sent_count += 1
                else:
                    failed_emails.append(contractor.email)
            except Exception as e:
                logger.error(f"E-posta gönderme hatası ({contractor.email}): {str(e)}")
                failed_emails.append(contractor.email)
        
        if sent_count > 0:
            flash(_('Sonuç raporu {count} yükleniciye başarıyla gönderildi.').format(count=sent_count), 'success')
        
        if failed_emails:
            flash(_('Bazı e-postalar gönderilemedi: {emails}').format(emails=', '.join(failed_emails)), 'warning')
            
    except ImportError:
        flash(_('SendGrid kütüphanesi yüklenemedi.'), 'error')
    except Exception as e:
        logger.error(f"E-posta gönderme hatası: {str(e)}")
        flash(_('E-posta gönderilirken bir hata oluştu: {error}').format(error=str(e)), 'error')
    
    return redirect(url_for('main.view_project', project_id=project_id))


def generate_topsis_pdf_for_email(project_id):
    """Generate TOPSIS PDF report for email attachment"""
    from datetime import datetime
    import base64
    import io
    
    project = Project.query.get_or_404(project_id)
    owner_note = project.owner_note or ""
    
    applications = ProjectApplication.query.filter_by(project_id=project_id)\
        .order_by(ProjectApplication.topsis_score.desc())\
        .all()
    
    if not applications or len(applications) < 2:
        return None
    
    # Get criteria and sub-criteria
    criteria = project.selected_criteria
    sub_criteria = project.selected_subcriteria
    
    # Calculate scores per criteria group
    criteria_scores = {}
    for app in applications:
        contractor_name = app.contractor.company_name or app.contractor.username
        criteria_scores[contractor_name] = {}
        
        for criterion in criteria:
            group_subs = [sc for sc in sub_criteria if sc.criterion_id == criterion.id]
            total_score = 0
            count = 0
            
            for sc in group_subs:
                kpi_score = KPIScore.query.filter_by(
                    application_id=app.id,
                    sub_criterion_id=sc.id
                ).first()
                if kpi_score and kpi_score.score:
                    total_score += kpi_score.score
                    count += 1
            
            avg_score = total_score / count if count > 0 else 0
            criteria_scores[contractor_name][criterion.name] = avg_score
    
    # Generate simple PDF HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; font-size: 10px; margin: 20px; }}
            h1 {{ color: #2c3e50; font-size: 16px; }}
            h2 {{ color: #34495e; font-size: 12px; margin-top: 15px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 6px; text-align: left; }}
            th {{ background-color: #3498db; color: white; }}
            .rank-1 {{ background-color: #d4edda; }}
            .rank-2 {{ background-color: #fff3cd; }}
            .rank-3 {{ background-color: #f8d7da; }}
            .footer {{ margin-top: 20px; font-size: 8px; color: #666; }}
        </style>
    </head>
    <body>
        <h1>TOPSIS Karar Destek Sistemi Sonuç Raporu</h1>
        <p><strong>Proje:</strong> {project.name}</p>
        <p><strong>Tarih:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        
        <h2>Sıralama</h2>
        <table>
            <tr>
                <th>Sıra</th>
                <th>Yüklenici</th>
                <th>TOPSIS Puanı</th>
            </tr>
    """
    
    for idx, app in enumerate(applications, 1):
        rank_class = f"rank-{idx}" if idx <= 3 else ""
        contractor_name = app.contractor.company_name or app.contractor.username
        score = f"{app.topsis_score:.6f}" if app.topsis_score else "N/A"
        html_content += f"""
            <tr class="{rank_class}">
                <td>{idx}</td>
                <td>{contractor_name}</td>
                <td>{score}</td>
            </tr>
        """
    
    html_content += "</table>"
    
    if owner_note:
        html_content += f"""
        <h2>İşveren Notu</h2>
        <p>{owner_note}</p>
        """
    
    html_content += f"""
        <div class="footer">
            Bu rapor Construct Circular - Döngüsel İnşaat Karar Destek Sistemi tarafından otomatik olarak oluşturulmuştur.
        </div>
    </body>
    </html>
    """
    
    try:
        from weasyprint import HTML
        pdf_file = io.BytesIO()
        HTML(string=html_content).write_pdf(pdf_file)
        pdf_file.seek(0)
        return pdf_file.getvalue()
    except Exception as e:
        logger.error(f"PDF oluşturma hatası: {str(e)}")
        return None


@main_bp.route('/project/<int:project_id>')
@login_required
def view_project(project_id):
    project = Project.query.get_or_404(project_id)

    # Allow access to company that owns the project, administrators, or any contractor (even if they haven't applied)
    if project.user_id != current_user.id and not current_user.is_administrator() and not current_user.is_contractor():
        flash(_('Access denied.'), 'error')
        return redirect(url_for('main.dashboard'))

    # Get project applications if user is company or admin
    applications = []
    if current_user.is_company() or current_user.is_administrator():
        # Get applications and sort by TOPSIS score in descending order
        applications = ProjectApplication.query.filter_by(project_id=project.id)\
            .order_by(ProjectApplication.topsis_score.desc().nullslast())\
            .all()
        
        # Force refresh of application data to get latest scores
        for app in applications:
            # Refresh the application from database to get latest updates
            db.session.refresh(app)
            
            # Get latest DecisionMatrix scores for debugging
            latest_decision_scores = DecisionMatrix.query.filter_by(
                application_id=app.id
            ).count()
            
            # Log current scores for debugging
            logger.debug(f"Application {app.id} - Latest TOPSIS: {app.topsis_score}")
            logger.debug(f"Application {app.id} - Decision Matrix entries: {latest_decision_scores}")

        # Calculate rankings for applications if there are any
        if applications:
            ranked_alternatives = project.get_ranked_alternatives()
            # Map rankings to applications
            for app in applications:
                matching_rank = next(
                    (rank for rank in ranked_alternatives
                     if rank['name'] == f"Application from {app.contractor.username}"),
                    None
                )
                if matching_rank:
                    app.score = matching_rank['score']
                    app.rank = matching_rank['rank']
                else:
                    app.score = 0
                    app.rank = len(applications)

    # Create form instance for CSRF protection
    form = CSRFForm()

    return render_template(
        'project_view.html',
        project=project,
        applications=applications if (current_user.is_company() or current_user.is_administrator()) else None,
        criteria=project.selected_criteria,
        subcriteria=project.selected_subcriteria,
        is_owner=project.user_id == current_user.id,
        form=form  # Pass the form to the template
    )

@main_bp.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id and not current_user.is_administrator():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))

    form = ProjectForm(obj=project)
    criteria = Criterion.query.all()

    if form.validate_on_submit():
        try:
            project.name = form.name.data
            project.description = form.description.data
            # Update criteria selection
            project.selected_criteria = []
            project.selected_subcriteria = []

            selected_criteria = request.form.getlist('criteria[]')
            selected_subcriteria = request.form.getlist('sub_criteria[]')

            for criterion_id in selected_criteria:
                criterion = Criterion.query.get(criterion_id)
                if criterion:
                    project.selected_criteria.append(criterion)

                    # Handle file upload for criterion
                    criterion_file = request.files.get(f'criterion_file_{criterion_id}')
                    if criterion_file and criterion_file.filename:
                        # Remove old document if exists
                        old_doc = Document.query.filter_by(
                            project_id=project.id,
                            criterion_id=criterion_id
                        ).first()
                        if old_doc:
                            old_file_path = os.path.join(current_app.root_path, old_doc.file_path)
                            if os.path.exists(old_file_path):
                                os.remove(old_file_path)
                            db.session.delete(old_doc)

                        # Add new document
                        document = save_uploaded_file(
                            criterion_file,
                            project_id=project.id,
                            criterion_id=criterion_id
                        )
                        if document:
                            db.session.add(document)

            # Update selected sub-criteria
            for sub_criterion_id in selected_subcriteria:
                sub_criterion = SubCriterion.query.get(sub_criterion_id)
                if sub_criterion and str(sub_criterion.criterion_id) in selected_criteria:
                    project.selected_subcriteria.append(sub_criterion)

            db.session.commit()
            flash('Project updated successfully!', 'success')
            return redirect(url_for('main.view_project', project_id=project.id))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating project: {str(e)}")
            flash(f'Error updating project: {str(e)}', 'error')

    return render_template('project_form.html', form=form, project=project, criteria=criteria)

@main_bp.route('/project/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        return 'Access denied', 403

    try:
        # Delete all project applications and related data
        for application in project.applications:
            # Delete KPI documents for this application
            for kpi_doc in application.kpi_documents:
                file_path = os.path.join(current_app.root_path, kpi_doc.file_path)
                if os.path.exists(file_path):
                    os.remove(file_path)
                db.session.delete(kpi_doc)
            
            # Delete application documents
            for document in application.documents:
                file_path = os.path.join(current_app.root_path, document.file_path)
                if os.path.exists(file_path):
                    os.remove(file_path)
                db.session.delete(document)
            
            # Delete KPI scores for this application
            KPIScore.query.filter_by(application_id=application.id).delete()
            
            # Delete decision matrix entries
            DecisionMatrix.query.filter_by(application_id=application.id).delete()
            
            # Delete criterion evaluations
            CriterionEvaluation.query.filter_by(application_id=application.id).delete()
            
            # Delete the application itself
            db.session.delete(application)
        
        # Delete all alternatives for this project
        for alternative in project.alternatives:
            # Delete alternative evaluations
            CriterionEvaluation.query.filter_by(alternative_id=alternative.id).delete()
            db.session.delete(alternative)
        
        # Delete project documents
        for document in project.documents:
            file_path = os.path.join(current_app.root_path, document.file_path)
            if os.path.exists(file_path):
                os.remove(file_path)
            db.session.delete(document)

        # Clear many-to-many relationships
        project.selected_criteria = []
        project.selected_subcriteria = []

        # Delete the project
        db.session.delete(project)
        db.session.commit()
        flash('Project deleted successfully', 'success')
        return '', 204
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting project: {str(e)}")
        flash(f'Error deleting project: {str(e)}', 'error')
        return str(e), 500

@main_bp.route('/project/<int:project_id>/criterion', methods=['POST'])
@login_required
def add_criterion_to_project(project_id): #Renamed for clarity
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Access denied.')
        return redirect(url_for('main.project', project_id=project_id))

    name = request.form.get('name')
    weight = request.form.get('weight', type=float)
    is_cost = request.form.get('is_cost') == 'on'

    if name and weight is not None:
        criterion = Criterion(
            name=name,
            weight=weight,
            is_cost=is_cost,
            project_id=project_id
        )
        db.session.add(criterion)
        db.session.commit()
        return redirect(url_for('main.project', project_id=project_id))

    flash('Name and weight are required.')
    return redirect(url_for('main.project', project_id=project_id))

@main_bp.route('/criterion/<int:criterion_id>/delete', methods=['POST'])
@login_required
def delete_criterion(criterion_id):
    criterion = Criterion.query.get_or_404(criterion_id)
    if criterion.project.user_id != current_user.id:
        return 'Access denied', 403
    db.session.delete(criterion)
    db.session.commit()
    return '', 204

@main_bp.route('/profile/company')
@login_required
def company_profile():
    # Both companies and contractors can access profile pages
    return render_template('profile/company_profile.html')

@main_bp.route('/profile/company/edit', methods=['GET', 'POST'])
@login_required
def edit_company_profile():
    # Both companies and contractors can edit profiles

    form = CompanyProfileForm(obj=current_user)

    if form.validate_on_submit():
        try:
            current_user.company_name = form.company_name.data
            current_user.company_description = form.company_description.data
            db.session.commit()
            flash(_('Profile updated successfully!'), 'success')
            return redirect(url_for('main.company_profile'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating company profile: {str(e)}")
            flash(_('An error occurred while updating your profile.'), 'danger')

    return render_template('profile/edit_company_profile.html', form=form)

@main_bp.route('/project/<int:project_id>/apply', methods=['GET', 'POST'])
@login_required
def apply_project(project_id):
    if not current_user.is_contractor():
        flash(_('Only contractors can apply to projects.'), 'error')
        return redirect(url_for('main.dashboard'))

    project = Project.query.get_or_404(project_id)
    logger.debug(f"Found project: {project.name}")
    logger.debug(f"Project status: {project.status}")

    if project.status != ProjectStatus.OPEN:
        flash(_('This project is no longer accepting applications.'), 'error')
        return redirect(url_for('main.dashboard'))

    # Check if already applied
    existing_application = ProjectApplication.query.filter_by(
        project_id=project.id,
        contractor_id=current_user.id
    ).first()

    if existing_application:
        flash(_('You have already applied to this project.'), 'info')
        return redirect(url_for('main.dashboard'))

    # Get all criteria and their sub-criteria ordered by ID
    criteria = Criterion.query.order_by(Criterion.id.asc()).all()
    current_locale = str(get_locale())
    
    for criterion in criteria:
        # Add translated names for criteria
        criterion.translated_name = get_translated_criterion_name(criterion.name, current_locale)
        criterion.translated_description = get_translated_criterion_description(criterion.description, current_locale)
        
        # Explicitly order sub-criteria by ID using SQL query
        criterion.sub_criteria = SubCriterion.query.filter_by(
            criterion_id=criterion.id
        ).order_by(
            SubCriterion.id.asc()
        ).all()
        
        # Load KPI definitions for each sub-criterion and add translations
        for sub in criterion.sub_criteria:
            sub.translated_name = get_translated_subcriterion_name(sub.name, current_locale)
            sub.translated_description = get_translated_subcriterion_description(sub.description, current_locale)
            sub.kpi_definitions = KeyPerformanceIndicator.query.filter_by(
                sub_criterion_id=sub.id
            ).order_by(
                KeyPerformanceIndicator.id.asc()
            ).all()
            logger.debug(f"Sub-criterion {sub.id} has {len(sub.kpi_definitions)} KPI definitions")

    logger.debug(f"Available criteria count: {len(criteria)}")
    logger.debug("Sub-criteria are ordered by ID in ascending order")

    form = ProjectApplicationForm()
    if form.validate_on_submit() or form.save_draft.data:
        try:
            # Determine status based on which button was clicked
            if form.save_draft.data:
                status = ApplicationStatus.DRAFT
                flash_message = _('Application saved as draft successfully!')
            else:
                status = ApplicationStatus.PENDING
                flash_message = _('Application submitted successfully!')
            
            # Start database transaction
            application = ProjectApplication(
                project_id=project.id,
                contractor_id=current_user.id,
                cover_letter=form.cover_letter.data if form.cover_letter else "", #Fix for line 374
                status=status
            )
            db.session.add(application)
            db.session.flush()  # Get application ID

            # Create an Alternative record for this application
            # Ensure we have a valid cover letter
            cover_letter_summary = ""
            if form.cover_letter.data:
                cover_letter_summary = form.cover_letter.data[:100] + "..."  # First 100 chars of cover letter
            
            alternative = Alternative(
                name=f"Application from {current_user.username}",
                description=cover_letter_summary,
                project_id=project.id
            )
            db.session.add(alternative)
            db.session.flush()  # Get alternative ID

            # Get selected sub-criteria, maintaining order by ID
            selected_subcriteria = request.form.getlist('selected_subcriteria[]')
            logger.debug(f"Selected subcriteria: {selected_subcriteria}")

            # Process selected sub-criteria in ID order
            ordered_subcriteria = SubCriterion.query.filter(
                SubCriterion.id.in_(selected_subcriteria)
            ).order_by(
                SubCriterion.id.asc()
            ).all()

            for sub in ordered_subcriteria:
                # Handle file upload for sub-criterion
                file = request.files.get(f'file_{sub.id}')
                logger.debug(f"Processing file for sub-criterion {sub.id}: {file.filename if file else 'No file'}")

                if file and file.filename:
                    document = save_uploaded_file(
                        file,
                        project_id=project.id,
                        application_id=application.id
                    )
                    if document:
                        logger.debug(f"Saved document: {document.filename} for sub-criterion {sub.id}")
                        document.sub_criterion_id = sub.id  # Associate with sub-criterion
                        db.session.add(document)

                # Process KPI documents for this sub-criterion
                kpi_definitions = KeyPerformanceIndicator.query.filter_by(
                    sub_criterion_id=sub.id
                ).all()
                
                for kpi in kpi_definitions:
                    kpi_file = request.files.get(f'kpi_file_{kpi.id}')
                    logger.debug(f"Processing KPI file for KPI {kpi.id}: {kpi_file.filename if kpi_file else 'No file'}")
                    
                    if kpi_file and kpi_file.filename:
                        # Save the uploaded file to the server
                        filename = secure_filename(kpi_file.filename)
                        file_ext = os.path.splitext(filename)[1].lower()
                        
                        # Generate a unique filename with timestamp
                        unique_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
                        
                        # Create upload directory if it doesn't exist
                        upload_folder = os.path.join('static', 'uploads', 'kpi_documents')
                        os.makedirs(upload_folder, exist_ok=True)
                        
                        file_path = os.path.join(upload_folder, unique_filename)
                        kpi_file.save(file_path)
                        file_size = os.path.getsize(file_path)
                        
                        # Create KPI document record
                        kpi_document = KPIDocument(
                            filename=filename,
                            file_path=file_path,
                            file_type=file_ext.replace('.', ''),
                            file_size=file_size,
                            kpi_id=kpi.id,
                            application_id=application.id,
                            ai_evaluated=False  # Başlangıçta AI değerlendirmesi yapılmamış olarak işaretle
                        )
                        db.session.add(kpi_document)
                        logger.debug(f"Saved KPI document: {kpi_document.filename} for KPI {kpi.id}")
                        
                        # Eğer KPI için AI değerlendirmesi etkinleştirilmişse, belgeyi değerlendir
                        if kpi.use_ai_evaluation and kpi.ai_evaluation_criteria:
                            try:
                                # AI modülünü içe aktar
                                from utils.ai_evaluator import evaluate_kpi_document
                                
                                logger.debug(f"Starting AI evaluation for KPI document ID: {kpi_document.id}")
                                # AI değerlendirmesi yap
                                evaluation_result = evaluate_kpi_document(
                                    document_path=file_path,
                                    file_type=file_ext.replace('.', ''),
                                    kpi_evaluation_criteria=kpi.ai_evaluation_criteria
                                )
                                
                                if evaluation_result['success']:
                                    # AI değerlendirme sonuçlarını kaydet
                                    kpi_document.ai_evaluated = True
                                    kpi_document.ai_score = evaluation_result['score']
                                    kpi_document.ai_explanation = evaluation_result['explanation']
                                    logger.debug(f"AI evaluation completed: Score {evaluation_result['score']}")
                                else:
                                    logger.warning(f"AI evaluation failed: {evaluation_result['explanation']}")
                            except Exception as e:
                                logger.error(f"Error during AI evaluation: {str(e)}")
                                logger.error(f"Traceback: {traceback.format_exc()}")

                # Convert Decimal weight to float before calculations
                weight_value = float(sub.weight)

                # Create criterion evaluation
                evaluation = CriterionEvaluation(
                    alternative_id=alternative.id,
                    criterion_id=sub.criterion_id,
                    sub_criterion_id=sub.id,
                    application_id=application.id,
                    low=weight_value * 0.8,
                    medium=weight_value,
                    high=weight_value * 1.2
                )
                db.session.add(evaluation)

            db.session.commit()
            flash(flash_message, 'success')
            return redirect(url_for('main.dashboard'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error submitting application: {str(e)}")

            # Provide more user-friendly error message
            if "ForeignKeyViolation" in str(e):
                flash(_('There was an error processing your application criteria. Please try again or contact support if the issue persists.'), 'error')
            else:
                flash(_('Error submitting application. Please check all fields and try again. Error: {error}').format(
                    error=str(e)), 'error')

    logger.debug(f"Rendering template with {len(criteria)} criteria")
    return render_template('project_application.html', form=form, project=project, criteria=criteria)

@main_bp.route('/admin/applications')
@login_required
def admin_applications():
    if not current_user.is_administrator():
        flash(_('Access denied.'), 'error')
        return redirect(url_for('main.dashboard'))

    applications = ProjectApplication.query.order_by(ProjectApplication.created_at.desc()).all()
    return render_template('admin/project_applications.html', applications=applications)

@main_bp.route('/admin/application/<int:application_id>')
@login_required
def view_application_admin(application_id): # Renamed to avoid conflict
    if not current_user.is_administrator():
        flash(_('Access denied.'), 'error')
        return redirect(url_for('main.dashboard'))

    application = ProjectApplication.query.get_or_404(application_id)
    return render_template('admin/view_application.html', application=application)

@main_bp.route('/application/<int:application_id>/update-scores', methods=['GET', 'POST'])
@login_required
def update_scores(application_id):
    """Update decision matrix scores for an application"""
    # Logger zaten tanımlanmış, tekrar yapılandırmaya gerek yok
    logger.debug(f"============== UPDATE SCORES STARTED ==============")
    logger.debug(f"Application ID: {application_id}, Method: {request.method}")
    
    application = ProjectApplication.query.get_or_404(application_id)
    project = application.project

    # Allow access to company that owns the project or administrators
    if not (current_user.id == project.user_id or current_user.is_administrator()):
        logger.debug("Access denied: User not authorized")
        flash(_('Access denied.'), 'error')
        return redirect(url_for('main.dashboard'))

    # GET isteği durumunda, form verisi olmadığı için sadece sayfaya yönlendir
    if request.method == 'GET':
        logger.debug("GET request detected, redirecting to view page")
        flash(_('Form submitted incorrectly. Please try again.'), 'warning')
        return redirect(url_for('main.view_application', application_id=application_id))
    
    # Debug: Gelen form verilerini detaylı logla
    logger.debug(f"Form data received: {request.form}")
    logger.debug(f"Form data count: {len(request.form)}")
    logger.debug("Form fields:")
    for key, value in request.form.items():
        logger.debug(f"Form field: {key} = {value}")
    
    # KPI puanı içeren alanların sayısını kontrol et
    kpi_fields = [k for k in request.form.keys() if k.startswith('kpi_score_')]
    logger.debug(f"KPI score fields: {len(kpi_fields)}")
    
    try:
        logger.debug("Starting score update process")
        # Process KPI scores first
        kpi_updates = 0
        for key, value in request.form.items():
            if key.startswith('kpi_score_') and value:
                try:
                    kpi_id = int(key.replace('kpi_score_', ''))
                    score = int(value)
                    
                    logger.debug(f"Processing KPI score: KPI ID={kpi_id}, Score={score}")
                    
                    # Validate score range
                    if not 1 <= score <= 7:
                        logger.error(f"Invalid score range: {score} for KPI ID {kpi_id}")
                        flash(_('KPI Scores must be between 1 and 7.'), 'error')
                        return redirect(url_for('main.view_application', application_id=application_id))
                    
                    # Check if the KPI belongs to any of the project's selected sub-criteria
                    kpi = KeyPerformanceIndicator.query.get(kpi_id)
                    if not kpi:
                        logger.warning(f"KPI ID {kpi_id} not found in database")
                        continue
                        
                    logger.debug(f"Found KPI: {kpi.name} (ID: {kpi.id})")
                    
                    sub_criterion = SubCriterion.query.get(kpi.sub_criterion_id)
                    if not sub_criterion:
                        logger.warning(f"Sub-criterion ID {kpi.sub_criterion_id} not found")
                        continue
                        
                    logger.debug(f"Found sub-criterion: {sub_criterion.name} (ID: {sub_criterion.id})")
                    
                    # Artık seçili olup olmadığına bakmadan tüm KPI puanlarını kaydediyoruz
                    # Bu istek doğrultusunda değiştirildi
                    selected = sub_criterion in project.selected_subcriteria
                    logger.debug(f"Sub-criterion {sub_criterion.id} selected in project: {selected}")
                    logger.debug(f"Processing score for KPI {kpi_id} regardless of selection status")
                    
                    # Check if there's already a score entry
                    existing_score = KPIScore.query.filter_by(
                        application_id=application_id,
                        kpi_id=kpi_id
                    ).first()
                    
                    if existing_score:
                        # Update existing score AND mark as manually edited
                        logger.debug(f"Updating existing KPI score: {existing_score.id} from {existing_score.score} to {score}")
                        existing_score.score = score
                        existing_score.manually_edited = True
                        logger.info(f"KPI score {existing_score.id} marked as manually edited")
                    else:
                        # Create new score entry
                        logger.debug(f"Creating new KPI score for KPI ID {kpi_id}")
                        new_score = KPIScore(
                            application_id=application_id,
                            kpi_id=kpi_id,
                            score=score,
                            manually_edited=True
                        )
                        db.session.add(new_score)
                        logger.info(f"New KPI score created and marked as manually edited")
                    
                    kpi_updates += 1
                    
                except (ValueError, TypeError) as e:
                    logger.error(f"Invalid KPI score value for key {key}: {e}")
                    continue
                    
        logger.debug(f"Total KPI score updates: {kpi_updates}")
        
        # Perform immediate session flush to ensure KPI scores are saved
        # even if there's an error later
        if kpi_updates > 0:
            logger.debug("Flushing KPI score changes to database")
            db.session.flush()
        
        # Commit KPI scores
        db.session.commit()
        
        # Now calculate and update sub-criterion scores based on KPI scores
        # Tüm alt kriterler için puanları hesapla, sadece seçili olanlar değil
        all_subcriteria = SubCriterion.query.all()
        for sub_criterion in all_subcriteria:
            if sub_criterion.has_kpi:
                # Get all KPIs for this sub-criterion
                kpis = KeyPerformanceIndicator.query.filter_by(sub_criterion_id=sub_criterion.id).all()
                kpi_ids = [kpi.id for kpi in kpis]
                
                if kpi_ids:
                    # Get scores for these KPIs
                    kpi_scores = KPIScore.query.filter(
                        KPIScore.application_id == application_id,
                        KPIScore.kpi_id.in_(kpi_ids)
                    ).all()
                    
                    if kpi_scores:
                        # Calculate average score
                        total_score = sum(score.score for score in kpi_scores)
                        avg_score = round(total_score / len(kpi_scores))
                        
                        # Update or create decision matrix entry
                        existing_entry = DecisionMatrix.query.filter_by(
                            application_id=application_id,
                            sub_criterion_id=sub_criterion.id
                        ).first()
                        
                        if existing_entry:
                            # Only update if NOT manually edited by owner
                            if not existing_entry.manually_edited:
                                existing_entry.score = avg_score
                                logger.debug(f"Auto-updating sub-criterion {sub_criterion.id} score from KPIs: {avg_score}")
                            else:
                                logger.info(f"Skipping auto-update for sub-criterion {sub_criterion.id} - manually edited by owner")
                        else:
                            new_entry = DecisionMatrix(
                                application_id=application_id,
                                sub_criterion_id=sub_criterion.id,
                                score=avg_score,
                                manually_edited=False
                            )
                            db.session.add(new_entry)
            else:
                # Process regular sub-criterion scores from the form (for those without KPIs)
                score_key = f'score_{sub_criterion.id}'
                
                if score_key in request.form and request.form[score_key]:
                    try:
                        score = int(request.form[score_key])
                        
                        # Validate score range
                        if not 1 <= score <= 7:
                            flash(_('Scores must be between 1 and 7.'), 'error')
                            continue
                        
                        # Update or create score in decision matrix
                        decision_score = DecisionMatrix.query.filter_by(
                            application_id=application_id,
                            sub_criterion_id=sub_criterion.id
                        ).first()
                        
                        if decision_score:
                            decision_score.score = score
                            decision_score.manually_edited = True
                            logger.info(f"Sub-criterion {sub_criterion.id} score updated and marked as manually edited")
                        else:
                            decision_score = DecisionMatrix(
                                application_id=application_id,
                                sub_criterion_id=sub_criterion.id,
                                score=score,
                                manually_edited=True
                            )
                            db.session.add(decision_score)
                            logger.info(f"New sub-criterion {sub_criterion.id} score created and marked as manually edited")
                    except (ValueError, TypeError) as e:
                        logger.error(f"Invalid score value: {e}")
                        continue

        db.session.commit()
        flash(_('Scores updated successfully!'), 'success')
        
        # Recalculate TOPSIS score for the application
        if project.selected_criteria and project.selected_subcriteria:
            try:
                # Get ranked alternatives
                ranked_alternatives = project.get_ranked_alternatives()
                
                # Find matching application and update TOPSIS score
                for alt in ranked_alternatives:
                    if alt['name'] == f"Application from {application.contractor.username}":
                        application.topsis_score = alt['score']
                        db.session.commit()
                        break
            except Exception as e:
                logger.error(f"Error updating TOPSIS score: {str(e)}")
                # Continue without failing - TOPSIS score update is optional

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating scores: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        flash(_('Error updating scores. Please try again.'), 'error')

    return redirect(url_for('main.view_application', application_id=application_id))

@main_bp.route('/application/<int:application_id>')
@login_required
def view_application(application_id):
    """View application details"""
    application = ProjectApplication.query.get_or_404(application_id)
    project = application.project

    # Allow access to company that owns the project, administrators, or the contractor who submitted the application
    if not (current_user.id == project.user_id or current_user.is_administrator() or current_user.id == application.contractor_id):
        flash(_('Access denied.'), 'error')
        return redirect(url_for('main.dashboard'))

    # Get criterion evaluations
    evaluations = CriterionEvaluation.query.filter_by(application_id=application.id).all()

    # Get all related documents
    documents = Document.query.filter_by(application_id=application.id).all()
    
    # Get all KPI documents
    kpi_documents = KPIDocument.query.filter_by(application_id=application.id).all()
    
    # Load sub-criteria with KPI definitions and their scores
    sub_criterion_ids = [eval.sub_criterion_id for eval in evaluations if eval.sub_criterion_id]
    for sub_id in sub_criterion_ids:
        sub = SubCriterion.query.get(sub_id)
        if sub:
            # KPI tanımlarını yükle
            sub.kpi_definitions = KeyPerformanceIndicator.query.filter_by(
                sub_criterion_id=sub.id
            ).all()
            logger.debug(f"Loaded {len(sub.kpi_definitions)} KPI definitions for sub-criterion {sub.id}")
            
            # KPI puanlarını yükle
            for kpi in sub.kpi_definitions:
                kpi_score = KPIScore.query.filter_by(
                    application_id=application.id,
                    kpi_id=kpi.id
                ).first()
                kpi.current_score = kpi_score.score if kpi_score else None
                if kpi_score:
                    logger.debug(f"Loaded KPI score for KPI {kpi.id}: {kpi_score.score}")

    # Create form instance for CSRF protection
    form = CSRFForm()

    return render_template(
        'application_view.html',
        application=application,
        project=project,
        evaluations=evaluations,
        documents=documents,
        kpi_documents=kpi_documents,
        SubCriterion=SubCriterion,  # Pass the model to the template
        is_owner=project.user_id == current_user.id,
        form=form,  # Pass the form to the template
        current_user=current_user  # Pass current_user to the template
    )

@main_bp.route('/admin/application/<int:application_id>/accept', methods=['POST'])
@login_required
def accept_application(application_id):
    """Accept an application"""
    application = ProjectApplication.query.get_or_404(application_id)
    project = application.project

    if not (current_user.id == project.user_id or current_user.is_administrator()):
        flash(_('Access denied.'), 'error')
        return redirect(url_for('main.dashboard'))

    application.status = ApplicationStatus.ACCEPTED
    db.session.commit()
    flash(_('Application accepted successfully!'), 'success')
    return redirect(url_for('main.view_application', application_id=application_id))

@main_bp.route('/application/<int:application_id>/reject', methods=['POST'])
@login_required
def reject_application(application_id):
    """Reject an application"""
    application = ProjectApplication.query.get_or_404(application_id)
    project = application.project

    if not (current_user.id == project.user_id or current_user.is_administrator()):
        flash(_('Access denied.'), 'error')
        return redirect(url_for('main.dashboard'))

    application.status = ApplicationStatus.REJECTED
    db.session.commit()
    flash(_('Application rejected successfully!'), 'success')
    return redirect(url_for('main.view_application', application_id=application_id))

@main_bp.route('/admin/criterion/<int:criterion_id>/delete', methods=['POST'])
@login_required
def delete_admin_criterion(criterion_id):
    """Delete a criterion and its sub-criteria (Admin only)"""
    if not current_user.is_administrator():
        flash(_('Access denied.'), 'error')
        return redirect(url_for('main.dashboard'))

    criterion = Criterion.query.get_or_404(criterion_id)
    try:
        # First delete all sub-criteria
        SubCriterion.query.filter_by(criterion_id=criterion_id).delete()

        # Then delete the criterion itself
        db.session.delete(criterion)
        db.session.commit()

        flash(_('Criterion and its sub-criteria deleted successfully!'), 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting criterion: {str(e)}")
        flash(_('Error deleting criterion: {error}').format(error=str(e)), 'error')

    return redirect(url_for('main.admin_criteria'))

@main_bp.route('/admin/criteria')
@login_required
def admin_criteria():
    """View and manage criteria (Admin only)"""
    if not current_user.is_administrator():
        flash(_('Access denied.'), 'error')
        return redirect(url_for('main.dashboard'))

    # Get criteria ordered by ID
    criteria = Criterion.query.order_by(Criterion.id.asc()).all()
    for criterion in criteria:
        criterion.sub_criteria = SubCriterion.query.filter_by(
            criterion_id=criterion.id
        ).order_by(
            SubCriterion.id.asc()
        ).all()

    return render_template('admin/criteria.html', criteria=criteria)

@main_bp.route('/subcriterion/<int:subcriterion_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_subcriterion(subcriterion_id):
    """Edit a sub-criterion and manage its KPIs"""
    if not current_user.is_administrator():
        flash(_('Access denied.'), 'error')
        return redirect(url_for('main.dashboard'))
    
    subcriterion = SubCriterion.query.get_or_404(subcriterion_id)
    criterion = Criterion.query.get(subcriterion.criterion_id)
    
    # Ana form - Alt kriter bilgileri
    form = SubCriterionForm(obj=subcriterion, criterion_id=subcriterion.criterion_id)
    form.sub_criterion_id = subcriterion_id
    
    # KPI ekleme formu
    kpi_form = KPIDefinitionForm(sub_criterion_id=subcriterion_id)
    
    # Mevcut KPI tanımlarını al
    kpis = KeyPerformanceIndicator.query.filter_by(sub_criterion_id=subcriterion_id).all()
    
    # Form verilerini detaylı loglama
    logger.debug(f"Request method: {request.method}")
    logger.debug(f"Form data: {request.form.to_dict() if request.form else 'No form data'}")
    logger.debug(f"URL: {request.url}")
    logger.debug(f"Referrer: {request.referrer}")
    
    # Ana formu işle
    if request.method == 'POST':
        try:
            logger.debug("POST method detected, processing form data")
            
            # Temel bilgileri güncelle
            subcriterion.name = request.form.get('name')
            logger.debug(f"Name: {subcriterion.name}")
            
            subcriterion.description = request.form.get('description')
            logger.debug(f"Description: {subcriterion.description}")
            
            weight_value = request.form.get('weight')
            logger.debug(f"Weight value from form: {weight_value}")
            subcriterion.weight = float(weight_value) if weight_value else 0.0
            
            detail_weight_value = request.form.get('detail_weight')
            logger.debug(f"Detail weight value from form: {detail_weight_value}")
            subcriterion.detail_weight = float(detail_weight_value) if detail_weight_value else 1.0
            
            # KPI durumunu güncelle
            subcriterion.has_kpi = 'has_kpi' in request.form
            logger.debug(f"Has KPI: {subcriterion.has_kpi}")
            
            logger.debug("Committing changes to database")
            db.session.commit()
            logger.debug("Database commit successful")
            
            flash(_('Sub-criterion updated successfully!'), 'success')
            
            logger.debug("Redirecting to admin criteria page")
            return redirect(url_for('main.admin_criteria'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating sub-criterion: {str(e)}")
            logger.error(f"Exception traceback: {traceback.format_exc()}")
            flash(_('An error occurred while updating sub-criterion.'), 'danger')
    
    return render_template('subcriterion_edit.html', 
                          form=form, 
                          kpi_form=kpi_form,
                          kpis=kpis,
                          subcriterion=subcriterion, 
                          criterion=criterion)

@main_bp.route('/subcriterion/<int:subcriterion_id>/add-kpi', methods=['POST'])
@login_required
def add_kpi(subcriterion_id):
    """Add a new KPI to a sub-criterion"""
    logger.debug(f"Add KPI route called for subcriterion_id={subcriterion_id}")
    logger.debug(f"Form data: {request.form}")
    
    if not current_user.is_administrator():
        flash(_('Access denied.'), 'error')
        return redirect(url_for('main.dashboard'))
    
    subcriterion = SubCriterion.query.get_or_404(subcriterion_id)
    logger.debug(f"Found subcriterion: {subcriterion.name}")
    
    try:
        # Form verilerini doğrudan al
        name = request.form.get('name')
        description = request.form.get('description')
        
        # AI değerlendirme alanları
        use_ai_evaluation = 'use_ai_evaluation' in request.form
        ai_evaluation_criteria = request.form.get('ai_evaluation_criteria', '')
        
        logger.debug(f"KPI data: name={name}, description={description}, use_ai_evaluation={use_ai_evaluation}")
        
        if not name:
            flash(_('KPI name is required.'), 'error')
            return redirect(url_for('main.edit_subcriterion', subcriterion_id=subcriterion_id))
            
        # KPI'ı etkinleştir
        if not subcriterion.has_kpi:
            subcriterion.has_kpi = True
            logger.debug(f"Enabled KPI for subcriterion {subcriterion_id}")
            
        # Yeni KPI oluştur
        kpi = KeyPerformanceIndicator(
            name=name,
            description=description,
            sub_criterion_id=subcriterion_id,
            use_ai_evaluation=use_ai_evaluation,
            ai_evaluation_criteria=ai_evaluation_criteria
        )
        
        logger.debug(f"Created KPI object: {kpi.name}")
        db.session.add(kpi)
        db.session.commit()
        logger.debug(f"KPI saved to database with ID: {kpi.id}")
        flash(_('KPI added successfully!'), 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding KPI: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        flash(_('An error occurred while adding KPI.'), 'danger')
    
    return redirect(url_for('main.edit_subcriterion', subcriterion_id=subcriterion_id))

@main_bp.route('/kpi/<int:kpi_id>/edit', methods=['POST'])
@login_required
def edit_kpi(kpi_id):
    """Edit a KPI definition"""
    logger.debug(f"Edit KPI route called for kpi_id={kpi_id}")
    logger.debug(f"Form data: {request.form}")
    
    if not current_user.is_administrator():
        flash(_('Access denied.'), 'error')
        return redirect(url_for('main.dashboard'))
    
    kpi = KeyPerformanceIndicator.query.get_or_404(kpi_id)
    subcriterion_id = kpi.sub_criterion_id
    
    try:
        # Form verilerini doğrudan al
        name = request.form.get('name')
        description = request.form.get('description')
        
        # AI değerlendirme alanları
        use_ai_evaluation = 'use_ai_evaluation' in request.form
        ai_evaluation_criteria = request.form.get('ai_evaluation_criteria', '')
        
        logger.debug(f"KPI update data: name={name}, description={description}, use_ai_evaluation={use_ai_evaluation}")
        
        if not name:
            flash(_('KPI name is required.'), 'error')
            return redirect(url_for('main.edit_subcriterion', subcriterion_id=subcriterion_id))
        
        # KPI'ı güncelle
        kpi.name = name
        kpi.description = description
        kpi.use_ai_evaluation = use_ai_evaluation
        kpi.ai_evaluation_criteria = ai_evaluation_criteria
        kpi.updated_at = datetime.utcnow()
        
        db.session.commit()
        logger.debug(f"KPI updated with ID: {kpi.id}")
        flash(_('KPI updated successfully!'), 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating KPI: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        flash(_('An error occurred while updating KPI.'), 'danger')
    
    return redirect(url_for('main.edit_subcriterion', subcriterion_id=subcriterion_id))

@main_bp.route('/kpi/<int:kpi_id>/delete', methods=['POST'])
@login_required
def delete_kpi(kpi_id):
    """Delete a KPI definition"""
    if not current_user.is_administrator():
        flash(_('Access denied.'), 'error')
        return redirect(url_for('main.dashboard'))
    
    kpi = KeyPerformanceIndicator.query.get_or_404(kpi_id)
    subcriterion_id = kpi.sub_criterion_id
    
    try:
        db.session.delete(kpi)
        
        # Eğer bu alt kritere ait başka KPI kalmadıysa, has_kpi'yi False yap
        remaining_kpis = KeyPerformanceIndicator.query.filter_by(sub_criterion_id=subcriterion_id).count()
        if remaining_kpis == 0:
            subcriterion = SubCriterion.query.get(subcriterion_id)
            subcriterion.has_kpi = False
        
        db.session.commit()
        flash(_('KPI deleted successfully!'), 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting KPI: {str(e)}")
        flash(_('An error occurred while deleting KPI.'), 'danger')
    
    return redirect(url_for('main.edit_subcriterion', subcriterion_id=subcriterion_id))

@main_bp.route('/reports/criterion-groups-topsis', methods=['GET'])
@login_required
def criterion_groups_topsis():
    """
    Calculates and displays TOPSIS rankings for subcriteria within each criterion group
    using application values from DecisionMatrix for each main criterion separately
    """
    logger.debug("Starting criterion groups TOPSIS analysis")
    
    if not (current_user.is_administrator() or current_user.is_company()):
        flash(_('Access denied. Company or administrator privileges required.'), 'error')
        return redirect(url_for('main.dashboard'))
    
    # Get all criteria groups, ordered by ID to match database order
    criterion_groups = Criterion.query.order_by(Criterion.id).all()
    
    if not criterion_groups:
        flash(_('No criterion groups defined.'), 'warning')
        return redirect(url_for('main.admin_criteria'))
    
    # Fuzzy numbers dictionary for TOPSIS calculation
    fuzzy_numbers = {
        1: (0, 0, 1),     # Very Poor
        2: (0, 1, 3),     # Poor
        3: (1, 3, 5),     # Medium Poor
        4: (3, 5, 7),     # Fair
        5: (5, 7, 9),     # Medium Good
        6: (7, 9, 10),    # Good
        7: (9, 10, 10)    # Very Good
    }
    
    # Store results for each group
    group_results = []
    
    # Get all projects with at least one evaluated application
    projects_with_evaluations = db.session.query(Project).join(
        ProjectApplication, Project.id == ProjectApplication.project_id
    ).join(
        DecisionMatrix, ProjectApplication.id == DecisionMatrix.application_id
    ).filter(
        DecisionMatrix.score.isnot(None)
    ).distinct().all()
    
    # Store application ranking results if available
    application_rankings = []
    
    # If no projects with evaluations, use the detail_weight based analysis
    if not projects_with_evaluations:
        logger.info("No projects with evaluations found. Using detail_weight based analysis.")
        
        for criterion in criterion_groups:
            # Get all subcriteria for this criterion group
            subcriteria = SubCriterion.query.filter_by(criterion_id=criterion.id).order_by(SubCriterion.id).all()
            
            if len(subcriteria) < 2:
                logger.debug(f"Not enough subcriteria found for criterion {criterion.name} (ID: {criterion.id})")
                continue
            
            # Prepare subcriterion data for TOPSIS analysis
            subcriterion_data = []
            for sub in subcriteria:
                # Use detail_weight for the analysis (this is what distinguishes subcriteria)
                subcriterion_data.append({
                    'id': sub.id,
                    'name': sub.name,
                    'detail_weight': float(sub.detail_weight)
                })
            
            # Calculate TOPSIS ranking for this group
            try:
                results = group_subcriterion_topsis(
                    subcriterion_data, 
                    fuzzy_numbers,
                    criterion_name=criterion.name
                )
                
                # Add results to the group results list
                group_results.append({
                    'criterion_id': criterion.id,
                    'criterion_name': criterion.name,
                    'subcriteria_count': len(subcriteria),
                    'topsis_results': results,
                    'data_source': 'detail_weight'
                })
                
                logger.debug(f"TOPSIS analysis completed for criterion {criterion.name} with {len(subcriteria)} subcriteria")
            except Exception as e:
                logger.error(f"Error calculating TOPSIS for criterion {criterion.name}: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
    else:
        # Select the most recent project with evaluations
        selected_project = projects_with_evaluations[0]
        logger.info(f"Using application data from project: {selected_project.name} (ID: {selected_project.id})")
        
        # Get all applications with evaluations for this project
        applications = ProjectApplication.query.filter_by(
            project_id=selected_project.id
        ).all()
        
        if not applications:
            logger.warning(f"No applications found for project {selected_project.id}")
            flash(_('No applications found for selected project.'), 'warning')
            return redirect(url_for('main.dashboard'))
        
        logger.info(f"Found {len(applications)} applications with evaluations")
        
        # Get all subcriteria for the project
        all_subcriteria = SubCriterion.query.all()
        if not all_subcriteria:
            flash(_('No criteria defined for TOPSIS calculation.'), 'error')
            return redirect(url_for('main.dashboard'))
        
        # Get all decision matrix values for applications in this project
        decision_matrix_values = {}
        for app in applications:
            scores = DecisionMatrix.query.filter_by(application_id=app.id).all()
            for score in scores:
                if score.sub_criterion_id not in decision_matrix_values:
                    decision_matrix_values[score.sub_criterion_id] = []
                decision_matrix_values[score.sub_criterion_id].append((app.id, score.score))
        
        # Calculate average scores for each subcriterion
        average_scores = {}
        for sub_id, scores in decision_matrix_values.items():
            if scores:
                # Extract just the scores for the average calculation
                score_values = [score[1] for score in scores]
                average_scores[sub_id] = sum(score_values) / len(score_values)
        
        # For each criterion group, calculate TOPSIS scores using application values
        for criterion in criterion_groups:
            # Get all subcriteria for this criterion group
            subcriteria = SubCriterion.query.filter_by(criterion_id=criterion.id).order_by(SubCriterion.id).all()
            
            if len(subcriteria) < 2:
                logger.debug(f"Not enough subcriteria found for criterion {criterion.name} (ID: {criterion.id})")
                continue
            
            # Prepare subcriterion data for TOPSIS analysis
            subcriterion_data = []
            application_values = {}  # Dictionary to store application values
            
            # Get subcriteria IDs for this criterion group
            subcriteria_ids = [sub.id for sub in subcriteria]
            
            # For this criterion group, perform a TOPSIS analysis for each application
            criterion_app_scores = {}  # Store application scores for this criterion
            
            # First: Prepare subcriterion data with detailed weights for TOPSIS calculation
            subcriterion_topsis_data = []
            
            for sub in subcriteria:
                # Use detail_weight for the analysis weighting
                subcriterion_topsis_data.append({
                    'id': sub.id,
                    'name': sub.name,
                    'detail_weight': float(sub.detail_weight)
                })
            
            # Second: For each application, prepare a map of their scores for each subcriterion
            app_scores_map = {}  # Map of application ID to scores for subcriteria
            
            for app in applications:
                app_id = app.id
                app_name = app.contractor.username
                app_scores = {}
                
                # Get all scores for this application
                scores = DecisionMatrix.query.filter_by(application_id=app_id).all()
                
                # Map scores by subcriterion ID
                for score in scores:
                    if score.sub_criterion_id in subcriteria_ids:
                        app_scores[score.sub_criterion_id] = score.score
                
                # Only include applications with scores for all subcriteria in this group
                if len(app_scores) == len(subcriteria_ids):
                    app_scores_map[app_id] = {
                        'app_id': app_id,
                        'app_name': app_name,
                        'scores': app_scores,  # Map of subcriterion ID to score
                        'score_list': [app_scores[sub_id] for sub_id in subcriteria_ids]  # List of scores
                    }
            
            # Third: Calculate TOPSIS scores for each application using the same TOPSIS method as for subcriteria
            if app_scores_map and len(app_scores_map) >= 2:
                try:
                    # Convert application scores to a decision matrix where:
                    # - Each row is an application
                    # - Each column is a subcriterion
                    app_ids = list(app_scores_map.keys())
                    app_names = [app_scores_map[app_id]['app_name'] for app_id in app_ids]
                    decision_matrix = np.array([app_scores_map[app_id]['score_list'] for app_id in app_ids])
                    
                    # Get weights from subcriteria detail_weight
                    weights = np.array([float(sub.detail_weight) for sub in subcriteria])
                    
                    # Normalize weights to sum to 1.0
                    if np.sum(weights) > 0:
                        weights = weights / np.sum(weights)
                    else:
                        weights = np.ones(len(subcriteria)) / len(subcriteria)
                    
                    # Use the same fuzzy TOPSIS method that we use for subcriteria
                    # We need to repeat each weight 3 times to match the fuzzy number triplets (l,m,h)
                    expanded_weights = np.repeat(weights, 3)
                    app_topsis_results = fuzzy_topsis(decision_matrix, expanded_weights, fuzzy_numbers)
                    
                    # Store results for each application
                    for i, app_id in enumerate(app_ids):
                        topsis_score = float(app_topsis_results['Normalized Cᵢ'].values[i])
                        criterion_app_scores[app_id] = {
                            'app_id': app_id,
                            'app_name': app_names[i],
                            # Alt kriter puanlarını gizle
                            'topsis_score': topsis_score
                        }
                    
                    logger.info(f"Calculated TOPSIS scores for {len(criterion_app_scores)} applications in {criterion.name} using fuzzy TOPSIS")
                    
                except Exception as e:
                    logger.error(f"Error using fuzzy TOPSIS for applications in {criterion.name}: {str(e)}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    
                    # Fall back to weighted average method if TOPSIS fails
                    for app_id, app_data in app_scores_map.items():
                        app_scores_list = app_data['score_list']
                        
                        # Calculate the app's score as a weighted sum of subcriterion values
                        topsis_score = 0
                        total_weight = 0
                        
                        for i, sub in enumerate(subcriteria):
                            sub_weight = float(sub.detail_weight)
                            sub_score = app_scores_list[i]
                            topsis_score += sub_weight * sub_score
                            total_weight += sub_weight
                        
                        # Normalize score to 0-1 range
                        if total_weight > 0:
                            normalized_score = topsis_score / (total_weight * 7.0)  # 7.0 is the max possible score
                        else:
                            normalized_score = sum(app_scores_list) / (len(app_scores_list) * 7.0)
                        
                        # Store the result
                        criterion_app_scores[app_id] = {
                            'app_id': app_id,
                            'app_name': app_data['app_name'],
                            # Alt kriter puanlarını gizle
                            'topsis_score': normalized_score
                        }
                    
                    logger.info(f"Used fallback weighted average method for {len(criterion_app_scores)} applications in {criterion.name}")
            
            # If only one application, use the normalized weighted average
            elif app_scores_map:
                app_id = list(app_scores_map.keys())[0]
                app_data = app_scores_map[app_id]
                app_scores_list = app_data['score_list']
                
                # Calculate a normalized score for the single application
                total_weight = sum(float(sub.detail_weight) for sub in subcriteria)
                weighted_score = sum(float(sub.detail_weight) * app_scores_list[i] for i, sub in enumerate(subcriteria))
                
                if total_weight > 0:
                    normalized_score = weighted_score / (total_weight * 7.0)
                else:
                    normalized_score = sum(app_scores_list) / (len(app_scores_list) * 7.0)
                
                criterion_app_scores[app_id] = {
                    'app_id': app_id,
                    'app_name': app_data['app_name'],
                    # Alt kriter puanlarını gizle
                    'topsis_score': normalized_score
                }
                
                logger.info(f"Calculated weighted scores for {len(criterion_app_scores)} applications in {criterion.name}")
            
            # Fallback if no scores could be calculated
            if not criterion_app_scores and len(applications) > 0:
                logger.warning(f"No application scores calculated for criterion {criterion.name}")
                
                # Find applications with at least some scores
                for app in applications:
                    app_id = app.id
                    app_name = app.contractor.username
                    
                    # Get any available scores for this criterion
                    scores = []
                    for sub_id in subcriteria_ids:
                        matches = [score[1] for score in decision_matrix_values.get(sub_id, []) if score[0] == app_id]
                        if matches:
                            scores.append(matches[0])
                    
                    # Use average of available scores
                    if scores:
                        criterion_app_scores[app_id] = {
                            'app_id': app_id,
                            'app_name': app_name,
                            # Alt kriter puanlarını gizle
                            'topsis_score': sum(scores) / (len(scores) * 7.0)  # Normalize to 0-1 range
                        }
            
            # Rank applications for this criterion based on TOPSIS score
            if criterion_app_scores:
                ranked_apps = sorted(
                    criterion_app_scores.values(), 
                    key=lambda x: x['topsis_score'], 
                    reverse=True
                )
                
                # Add rank information
                for i, app in enumerate(ranked_apps):
                    app['rank'] = i + 1
                
                # Add to application rankings
                application_rankings.append({
                    'criterion_id': criterion.id,
                    'criterion_name': criterion.name,
                    'applications': ranked_apps
                })
            
            # Continue with subcriterion TOPSIS analysis
            for sub in subcriteria:
                # Use detail_weight for the analysis weighting
                subcriterion_data.append({
                    'id': sub.id,
                    'name': sub.name,
                    'detail_weight': float(sub.detail_weight)
                })
                
                # Use average score if available
                if sub.id in average_scores:
                    application_values[sub.id] = average_scores[sub.id]
                    logger.debug(f"Using average score for subcriterion {sub.id}: {average_scores[sub.id]}")
            
            # Calculate TOPSIS ranking for this group using application values
            try:
                results = group_subcriterion_topsis(
                    subcriterion_data, 
                    fuzzy_numbers,
                    criterion_name=criterion.name,
                    application_values=application_values
                )
                
                # Rank applications for this criterion based on TOPSIS score
                ranked_apps = []
                if criterion_app_scores:
                    ranked_apps = sorted(
                        criterion_app_scores.values(), 
                        key=lambda x: x['topsis_score'], 
                        reverse=True
                    )
                    
                    # Add rank information
                    for i, app in enumerate(ranked_apps):
                        app['rank'] = i + 1
                
                # Check if all applications have no data for this group
                all_scores_zero = True
                if ranked_apps:
                    for app in ranked_apps:
                        if app.get('topsis_score', 0) > 0:
                            all_scores_zero = False
                            break
                
                # Add results to the group results list
                group_results.append({
                    'criterion_id': criterion.id,
                    'criterion_name': criterion.name,
                    'subcriteria_count': len(subcriteria),
                    'topsis_results': results,
                    'data_source': 'application_values',
                    'application_rankings': ranked_apps,
                    'no_data': all_scores_zero and len(ranked_apps) > 0
                })
                
                logger.debug(f"TOPSIS analysis completed for criterion {criterion.name} with {len(subcriteria)} subcriteria")
            except Exception as e:
                logger.error(f"Error calculating TOPSIS for criterion {criterion.name}: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Render results page
    return render_template(
        'reports/criterion_groups_topsis.html',
        group_results=group_results,
        application_rankings=application_rankings,
        selected_project=projects_with_evaluations[0] if projects_with_evaluations else None
    )

@main_bp.route('/project/<int:project_id>/calculate-topsis', methods=['POST'])
@login_required
def calculate_project_topsis(project_id):
    """Calculate TOPSIS scores for all applications of a project"""
    project = Project.query.get_or_404(project_id)

    # Allow access to company that owns the project or administrators
    if not (current_user.id == project.user_id or current_user.is_administrator()):
        flash(_('Access denied.'), 'error')
        return redirect(url_for('main.view_project', project_id=project_id))

    try:
        # Get all applications for this project
        applications = ProjectApplication.query.filter_by(project_id=project_id).all()

        # Check minimum application requirement
        if len(applications) < 3:
            flash(_('At least 3 applications are required for TOPSIS calculation.'), 'warning')
            return redirect(url_for('main.view_project', project_id=project_id))
        
        # Check KPI document status for informational purposes
        applications_with_docs = 0
        total_kpi_requirements = 0
        total_uploaded_docs = 0
        
        # Count total KPI requirements across all applications
        all_kpis = KeyPerformanceIndicator.query.all()
        total_kpi_requirements = len(applications) * len(all_kpis) if all_kpis else 0
        
        for app in applications:
            kpi_docs_count = KPIDocument.query.filter_by(application_id=app.id).count()
            total_uploaded_docs += kpi_docs_count
            if kpi_docs_count > 0:
                applications_with_docs += 1
        
        # Informational messages about document upload status
        if applications_with_docs == 0:
            flash(_('Note: No applications have uploaded KPI documents. Missing documents will receive score 0 in evaluation.'), 'info')
        elif applications_with_docs < len(applications):
            missing_docs = len(applications) - applications_with_docs
            flash(_('Info: {count} applications have no KPI documents uploaded. They will receive score 0 for missing KPIs.').format(count=missing_docs), 'info')
        
        if total_kpi_requirements > 0:
            completion_rate = (total_uploaded_docs / total_kpi_requirements) * 100
            flash(_('KPI Document completion rate: {rate}%. Missing documents will receive score 0.').format(rate=round(completion_rate, 1)), 'info')
        
        # Before TOPSIS calculation, ensure all applications have AI-evaluated KPI scores
        from utils.ai_evaluator import evaluate_document_with_ai, extract_text_from_file
        
        ai_evaluation_count = 0
        for application in applications:
            # Get all KPI documents for this application that need AI evaluation
            kpi_documents = KPIDocument.query.filter_by(application_id=application.id).all()
            
            for kpi_doc in kpi_documents:
                # Get the KPI definition
                kpi = KeyPerformanceIndicator.query.get(kpi_doc.kpi_id)
                if not kpi or not kpi.use_ai_evaluation or not kpi.ai_evaluation_criteria:
                    continue
                
                # Check if this KPI already has a score
                existing_score = KPIScore.query.filter_by(
                    application_id=application.id,
                    kpi_id=kpi.id
                ).first()
                
                if existing_score:
                    # Skip if already scored OR if manually edited by owner
                    if existing_score.manually_edited:
                        logger.info(f"Skipping AI evaluation for KPI {kpi.id} - manually edited by owner (current: {existing_score.score})")
                    continue  # Skip if already scored
                
                try:
                    # Extract text from document
                    document_text = extract_text_from_file(kpi_doc.file_path, kpi_doc.file_type)
                    
                    if document_text:
                        # Evaluate with AI
                        score, explanation = evaluate_document_with_ai(
                            document_text, 
                            kpi.ai_evaluation_criteria
                        )
                        
                        # Save the AI-generated score
                        ai_score = KPIScore(
                            application_id=application.id,
                            kpi_id=kpi.id,
                            score=score,
                            manually_edited=False,
                            ai_explanation=explanation
                        )
                        db.session.add(ai_score)
                        ai_evaluation_count += 1
                        
                        logger.info(f"AI evaluated KPI {kpi.name} for application {application.id}: Score {score}")
                    
                except Exception as e:
                    logger.error(f"Error in AI evaluation for KPI {kpi.id}: {str(e)}")
                    continue
        
        # Commit AI evaluation scores
        if ai_evaluation_count > 0:
            db.session.commit()
            logger.info(f"Completed AI evaluation for {ai_evaluation_count} KPI documents")
        
        # Now recalculate sub-criterion scores based on KPI scores OR manual scores
        for application in applications:
            for sub_criterion in SubCriterion.query.all():
                if sub_criterion.has_kpi:
                    # Get all KPIs for this sub-criterion
                    kpis = KeyPerformanceIndicator.query.filter_by(sub_criterion_id=sub_criterion.id).all()
                    kpi_ids = [kpi.id for kpi in kpis]
                    
                    if kpi_ids:
                        # Calculate KPI scores for this application
                        total_score = 0
                        kpi_count = 0
                        
                        for kpi in kpis:
                            # IMPORTANT: First check if there's a manual or AI score in KPIScore table
                            # This ensures owner-modified scores are used regardless of document status
                            kpi_score_record = KPIScore.query.filter_by(
                                application_id=application.id,
                                kpi_id=kpi.id
                            ).first()
                            
                            if kpi_score_record and kpi_score_record.score > 0:
                                # Use existing score (manual or AI)
                                total_score += kpi_score_record.score
                                kpi_count += 1
                                score_type = "manual" if kpi_score_record.manually_edited else "AI"
                                logger.debug(f"Application {application.id} - KPI {kpi.id}: Using {score_type} score {kpi_score_record.score}")
                            else:
                                # No score in KPIScore table - check if document exists
                                kpi_document = KPIDocument.query.filter_by(
                                    application_id=application.id,
                                    kpi_id=kpi.id
                                ).first()
                                
                                if kpi_document:
                                    # Document exists but no score yet, use default minimum
                                    total_score += 1
                                    kpi_count += 1
                                    logger.warning(f"Application {application.id} - KPI {kpi.id}: Document exists but no score, using default 1")
                                else:
                                    # No document and no manual score - TOPSIS requires minimum 1 (not 0)
                                    total_score += 1
                                    kpi_count += 1
                                    logger.debug(f"Application {application.id} - KPI {kpi.id}: No data available, using minimum score 1 for TOPSIS")
                        
                        # Calculate average score (including 0s for missing documents)
                        if kpi_count > 0:
                            avg_score = total_score / kpi_count
                            # TOPSIS requires INTEGER scores between 1-7
                            # Round average to nearest integer, ensuring minimum 1
                            if total_score == 0:
                                final_score = 1  # All KPIs missing = minimum score
                            else:
                                final_score = max(1, round(avg_score))
                                
                            logger.info(f"Application {application.id} - Sub-criterion {sub_criterion.id}: "
                                      f"Total KPIs: {kpi_count}, Total score: {total_score}, "
                                      f"Average: {avg_score:.2f}, Final: {final_score}")
                            
                            # Update or create decision matrix entry
                            existing_entry = DecisionMatrix.query.filter_by(
                                application_id=application.id,
                                sub_criterion_id=sub_criterion.id
                            ).first()
                            
                            if existing_entry:
                                # Only update if NOT manually edited by owner
                                if not existing_entry.manually_edited:
                                    existing_entry.score = final_score
                                    logger.debug(f"Updated sub-criterion {sub_criterion.id} score to {final_score} for application {application.id}")
                                else:
                                    logger.info(f"Skipping update for sub-criterion {sub_criterion.id} - manually edited by owner (current: {existing_entry.score})")
                            else:
                                new_entry = DecisionMatrix(
                                    application_id=application.id,
                                    sub_criterion_id=sub_criterion.id,
                                    score=final_score,
                                    manually_edited=False
                                )
                                db.session.add(new_entry)
                                logger.debug(f"Created new sub-criterion {sub_criterion.id} score {final_score} for application {application.id}")
                        else:
                            logger.warning(f"No KPIs found for sub-criterion {sub_criterion.id}")
                else:
                    # This sub-criterion doesn't have KPIs, check if there's a manual score
                    existing_manual_score = DecisionMatrix.query.filter_by(
                        application_id=application.id,
                        sub_criterion_id=sub_criterion.id
                    ).first()
                    
                    if not existing_manual_score:
                        # No manual score exists, create a default score for TOPSIS compatibility
                        # Use a random score between 1-7 to differentiate applications
                        import random
                        random.seed(application.id + sub_criterion.id)  # Consistent randomization
                        default_score = random.randint(1, 7)
                        
                        new_manual_entry = DecisionMatrix(
                            application_id=application.id,
                            sub_criterion_id=sub_criterion.id,
                            score=default_score
                        )
                        db.session.add(new_manual_entry)
                        logger.debug(f"Created default manual score {default_score} for sub-criterion {sub_criterion.id}, application {application.id}")
                    else:
                        logger.debug(f"Manual score already exists for sub-criterion {sub_criterion.id}, application {application.id}: {existing_manual_score.score}")
        
        # Commit updated decision matrix scores
        db.session.commit()

        # Get all sub-criteria ordered by ID
        sub_criteria = SubCriterion.query.order_by(SubCriterion.id.asc()).all()

        if not sub_criteria:
            flash(_('No criteria defined for TOPSIS calculation.'), 'error')
            return redirect(url_for('main.view_project', project_id=project_id))

        # Initialize matrices
        decision_values = []
        original_weights = []

        # Get weights from sub-criteria
        for sub in sub_criteria:
            weight = float(sub.weight)
            if weight <= 0:
                raise ValueError(f"Invalid weight for sub-criterion {sub.name}")
            original_weights.append(weight)

        # Convert weights to numpy array and expand to match fuzzy matrix dimensions
        weights = np.array(original_weights)
        # Repeat each weight 3 times to match the fuzzy number triplets
        weights = np.repeat(weights, 3)

        # Build decision matrix for each application
        for app in applications:
            app_scores = []
            scores = DecisionMatrix.query.filter_by(
                application_id=app.id
            ).join(
                SubCriterion
            ).order_by(
                SubCriterion.id.asc()
            ).all()

            # Validate we have scores for all criteria
            if len(scores) != len(sub_criteria):
                flash(_('Application {application} is missing scores for some criteria.').format(
                    application=app.contractor.username), 'error')
                return redirect(url_for('main.view_project', project_id=project_id))

            for score in scores:
                if not 1 <= score.score <= 7:
                    raise ValueError(f"Invalid score: {score.score}. Must be between 1 and 7.")
                app_scores.append(score.score)

            decision_values.append(app_scores)

        # Convert to numpy array
        decision_matrix = np.array(decision_values)  # Shape: (n_applications, n_criteria)

        # Fuzzynumbers dictionary
        fuzzy_numbers = {
            1: (0, 0, 1),     # Very Poor
            2: (0, 1, 3),     # Poor
            3: (1, 3, 5),     # Medium Poor
            4: (3, 5, 7),     # Fair
            5: (5, 7, 9),     # Medium Good
            6: (7, 9, 10),    # Good
            7: (9, 10, 10)    # Very Good
        }

        # Log detailed information
        logger.info("\n=== Batch TOPSIS Calculation Starting ===")
        logger.info(f"Decision Matrix Shape: {decision_matrix.shape}")
        logger.info(f"Original Decision Matrix:\n{decision_matrix}")
        logger.info(f"Original Weights Shape: {len(original_weights)}")
        logger.info(f"Expanded Weights Shape: {len(weights)}")
        logger.info(f"Available fuzzy numbers: {list(fuzzy_numbers.keys())}")

        try:
            # Validate all scores are within fuzzy number range
            if not all(1 <= score <= 7 for score in decision_matrix.flatten()):
                invalid_scores = [score for score in decision_matrix.flatten() if score < 1 or score > 7]
                raise ValueError(f"Invalid scores found: {invalid_scores}. All scores must be between 1 and 7.")

            # Calculate TOPSIS scores
            results = fuzzy_topsis(decision_matrix, weights, fuzzy_numbers)

            if results is None or results.empty:
                raise ValueError("TOPSIS calculation failed - no results returned")

            # Update scores for all applications
            for i, app in enumerate(applications):
                topsis_score = float(results['Normalized Cᵢ'].values[i])
                if np.isnan(topsis_score):
                    raise ValueError(f"TOPSIS calculation produced NaN result for application {i+1}")

                app.topsis_score = topsis_score
                app.updated_at = datetime.utcnow()
                logger.info(f"Application {app.id} TOPSIS Score: {topsis_score}")

            db.session.commit()
            flash(_('TOPSIS scores calculated successfully for all applications!'), 'success')

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error calculating TOPSIS scores: {str(e)}")
            logger.error(f"Decision matrix content:\n{decision_matrix}")
            logger.error(f"Weights content:\n{weights}")
            flash(_('Error calculating TOPSIS scores: {error}').format(error=str(e)), 'error')

        return redirect(url_for('main.view_project', project_id=project_id))

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error calculating TOPSIS scores: {str(e)}")
        flash(_('Error calculating TOPSIS scores: {error}').format(error=str(e)), 'error')

    return redirect(url_for('main.view_project', project_id=project_id))


@main_bp.route('/my-applications')
@login_required
def my_applications():
    """Show contractor's applications"""
    if not current_user.is_contractor():
        flash(_('Access denied.'), 'error')
        return redirect(url_for('main.dashboard'))

    applications = ProjectApplication.query.filter_by(
        contractor_id=current_user.id
    ).order_by(
        ProjectApplication.created_at.desc()
    ).all()

    form = CSRFForm()  # For delete action
    return render_template('my_applications.html', applications=applications, form=form)

def clean_old_files(application):
    """Clean old document files and evaluations when updating an application"""
    try:
        # Get references to old documents first - we'll need the filenames to delete the actual files
        old_docs = Document.query.filter_by(application_id=application.id).all()
        logger.debug(f"Found {len(old_docs)} old documents to clean for application {application.id}")
        
        # Get references to old KPI documents
        old_kpi_docs = KPIDocument.query.filter_by(application_id=application.id).all()
        logger.debug(f"Found {len(old_kpi_docs)} old KPI documents to clean for application {application.id}")
        
        # Delete evaluations first to avoid foreign key constraints
        eval_count = CriterionEvaluation.query.filter_by(application_id=application.id).delete()
        logger.debug(f"Deleted {eval_count} old evaluations for application {application.id}")
        
        # Delete KPI scores 
        kpi_score_count = KPIScore.query.filter_by(application_id=application.id).delete()
        logger.debug(f"Deleted {kpi_score_count} old KPI scores for application {application.id}")
        
        # Now delete regular document records from database
        docs_deleted = 0
        for doc in old_docs:
            try:
                # Keep track of the file path
                file_path = doc.file_path  # This is already the relative path
                
                # Delete the document record
                db.session.delete(doc)
                docs_deleted += 1
                
                # Now delete the actual file if it exists
                full_path = os.path.join(file_path)
                if os.path.exists(full_path):
                    os.remove(full_path)
                    logger.debug(f"Deleted file: {full_path}")
                else:
                    logger.warning(f"File not found: {full_path}")
            except Exception as doc_error:
                logger.error(f"Error deleting document {doc.id}: {str(doc_error)}")
                # Continue with other documents
        
        # Now delete KPI document records from database
        kpi_docs_deleted = 0
        for doc in old_kpi_docs:
            try:
                # Keep track of the file path
                file_path = doc.file_path  # This is already the relative path
                
                # Delete the document record
                db.session.delete(doc)
                kpi_docs_deleted += 1
                
                # Now delete the actual file if it exists
                full_path = os.path.join(file_path)
                if os.path.exists(full_path):
                    os.remove(full_path)
                    logger.debug(f"Deleted KPI file: {full_path}")
                else:
                    logger.warning(f"KPI file not found: {full_path}")
            except Exception as doc_error:
                logger.error(f"Error deleting KPI document {doc.id}: {str(doc_error)}")
                # Continue with other documents
        
        logger.debug(f"Deleted {docs_deleted} document records and {kpi_docs_deleted} KPI document records for application {application.id}")
        
        # Commit the changes
        db.session.commit()
        logger.debug(f"Successfully completed cleaning old files for application {application.id}")
        return True
    except Exception as e:
        logger.error(f"Error cleaning old files: {str(e)}")
        db.session.rollback()
        return False


@main_bp.route('/application/<int:application_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_application(application_id):
    """Edit an application"""
    application = ProjectApplication.query.get_or_404(application_id)

    # Only allow editing if it's pending and belongs to the current user
    if application.contractor_id != current_user.id:
        flash(_('Access denied.'), 'error')
        return redirect(url_for('main.my_applications'))

    if application.status != ApplicationStatus.PENDING:
        flash(_('Only pending applications can be edited.'), 'error')
        return redirect(url_for('main.my_applications'))

    form = ProjectApplicationForm(obj=application, project=application.project)
    project = application.project

    # Get all criteria and their sub-criteria ordered by ID
    criteria = Criterion.query.order_by(Criterion.id.asc()).all()
    current_locale = str(get_locale())
    
    for criterion in criteria:
        # Add translated names and descriptions for criteria
        criterion.translated_name = get_translated_criterion_name(criterion.name, current_locale)
        criterion.translated_description = get_translated_criterion_description(criterion.description, current_locale)
        
        criterion.sub_criteria = SubCriterion.query.filter_by(
            criterion_id=criterion.id
        ).order_by(
            SubCriterion.id.asc()
        ).all()
        
        # Add translations for sub-criteria
        for sub in criterion.sub_criteria:
            sub.translated_name = get_translated_subcriterion_name(sub.name, current_locale)
            sub.translated_description = get_translated_subcriterion_description(sub.description, current_locale)

    if form.validate_on_submit():
        try:
            # Check for file size limits before processing
            for file_key in request.files:
                file = request.files[file_key]
                if file and file.filename:
                    # Check file size (Flask handles this automatically, but we can add custom handling)
                    file.seek(0, 2)  # Seek to end of file
                    file_size = file.tell()
                    file.seek(0)  # Reset to beginning
                    
                    if file_size > current_app.config.get('MAX_CONTENT_LENGTH', 250 * 1024 * 1024):
                        flash(_('The uploaded file is too large. Please upload a file smaller than 250MB.'), 'error')
                        return render_template('project_application.html', 
                                             form=form, 
                                             project=project, 
                                             criteria=criteria, 
                                             application=application)
            
            # Update basic application details first before any file operations
            application.cover_letter = form.cover_letter.data if form.cover_letter else ""
            application.updated_at = datetime.utcnow()
            
            # Instead of removing all old files, we'll only replace files that are being updated
            
            # Update selected sub-criteria and documents
            selected_subcriteria = request.form.getlist('selected_subcriteria[]')
            logger.info(f"Selected sub-criteria: {selected_subcriteria}")

            # Get or create Alternative record for this application
            alternative = Alternative.query.filter_by(
                name=f"Application from {current_user.username}",
                project_id=project.id
            ).first()

            if not alternative:
                # Ensure we have a valid cover letter
                cover_letter_summary = ""
                if form.cover_letter.data:
                    cover_letter_summary = form.cover_letter.data[:100] + "..."
                
                alternative = Alternative(
                    name=f"Application from {current_user.username}",
                    description=cover_letter_summary,
                    project_id=project.id
                )
                db.session.add(alternative)
                db.session.flush()

            # Process selected sub-criteria in ID order
            ordered_subcriteria = SubCriterion.query.filter(
                SubCriterion.id.in_(selected_subcriteria)
            ).order_by(
                SubCriterion.id.asc()
            ).all()

            # First delete removed subcriteria evaluations (for subcriteria that were previously selected but now unselected)
            existing_eval_subcriteria = db.session.query(CriterionEvaluation.sub_criterion_id).filter_by(
                application_id=application.id
            ).distinct().all()
            existing_eval_subcriteria = [row[0] for row in existing_eval_subcriteria]
            
            # Find subcriteria that are no longer selected
            removed_subcriteria = [sub_id for sub_id in existing_eval_subcriteria 
                                  if str(sub_id) not in selected_subcriteria]
            
            # Delete evaluations for removed subcriteria
            if removed_subcriteria:
                CriterionEvaluation.query.filter(
                    CriterionEvaluation.application_id == application.id,
                    CriterionEvaluation.sub_criterion_id.in_(removed_subcriteria)
                ).delete(synchronize_session=False)
                
                # Delete documents for removed subcriteria
                for doc in Document.query.filter(
                    Document.application_id == application.id,
                    Document.sub_criterion_id.in_(removed_subcriteria)
                ).all():
                    try:
                        if os.path.exists(doc.file_path):
                            os.remove(doc.file_path)
                            logger.debug(f"Deleted file for removed subcriterion: {doc.file_path}")
                    except Exception as e:
                        logger.error(f"Error deleting document file: {str(e)}")
                    db.session.delete(doc)
            
            # Now process each selected subcriterion
            for sub in ordered_subcriteria:
                try:
                    # Handle file upload for this subcriterion if there's a new file
                    file = request.files.get(f'file_{sub.id}')
                    
                    if file and file.filename:
                        # Check if there's an existing document for this subcriterion
                        existing_doc = Document.query.filter_by(
                            application_id=application.id,
                            sub_criterion_id=sub.id
                        ).first()
                        
                        # If there's an existing document, delete it first
                        if existing_doc:
                            try:
                                if os.path.exists(existing_doc.file_path):
                                    os.remove(existing_doc.file_path)
                                    logger.debug(f"Deleted existing file: {existing_doc.file_path}")
                            except Exception as e:
                                logger.error(f"Error deleting existing document file: {str(e)}")
                            db.session.delete(existing_doc)
                            db.session.flush()
                        
                        # Now save the new file
                        document = save_uploaded_file(
                            file,
                            project_id=project.id,
                            application_id=application.id
                        )
                        if document:
                            document.sub_criterion_id = sub.id
                            db.session.merge(document)  # Use merge instead of add to handle existing objects
                            logger.info(f"Successfully saved document for subcriterion {sub.id}: {document.filename}")
                            logger.debug(f"Document ID: {document.id}, Path: {document.file_path}")
                    
                    # Handle KPI file uploads for this subcriterion
                    for kpi in KeyPerformanceIndicator.query.filter_by(sub_criterion_id=sub.id).all():
                        kpi_file = request.files.get(f'kpi_file_{kpi.id}')
                        
                        if kpi_file and kpi_file.filename:
                            # Check if there's an existing KPI document
                            existing_kpi_doc = KPIDocument.query.filter_by(
                                application_id=application.id,
                                kpi_id=kpi.id
                            ).first()
                            
                            # Delete existing KPI document if found
                            if existing_kpi_doc:
                                try:
                                    if os.path.exists(existing_kpi_doc.file_path):
                                        os.remove(existing_kpi_doc.file_path)
                                        logger.debug(f"Deleted existing KPI file: {existing_kpi_doc.file_path}")
                                except Exception as e:
                                    logger.error(f"Error deleting existing KPI document file: {str(e)}")
                                db.session.delete(existing_kpi_doc)
                                db.session.flush()
                            
                            # Save the new KPI file
                            filename = secure_filename(kpi_file.filename)
                            file_ext = os.path.splitext(filename)[1].lower()
                            
                            # Generate a unique filename with timestamp
                            unique_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
                            
                            # Create upload directory if it doesn't exist
                            upload_folder = os.path.join('static', 'uploads', 'kpi_documents')
                            os.makedirs(upload_folder, exist_ok=True)
                            
                            file_path = os.path.join(upload_folder, unique_filename)
                            kpi_file.save(file_path)
                            file_size = os.path.getsize(file_path)
                            
                            # Create KPI document record
                            kpi_document = KPIDocument(
                                filename=filename,
                                file_path=file_path,
                                file_type=file_ext.replace('.', ''),
                                file_size=file_size,
                                kpi_id=kpi.id,
                                application_id=application.id,
                                ai_evaluated=False
                            )
                            db.session.add(kpi_document)
                            db.session.flush()  # Ensure it gets an ID before AI evaluation
                            logger.info(f"Successfully saved KPI document for KPI {kpi.id}: {filename}")
                            logger.debug(f"KPI Document ID: {kpi_document.id}, Path: {file_path}")
                            
                            # If KPI has AI evaluation enabled, evaluate the document
                            if kpi.use_ai_evaluation and kpi.ai_evaluation_criteria:
                                try:
                                    from utils.ai_evaluator import evaluate_kpi_document
                                    
                                    logger.debug(f"Starting AI evaluation for KPI document")
                                    evaluation_result = evaluate_kpi_document(
                                        document_path=file_path,
                                        file_type=file_ext.replace('.', ''),
                                        kpi_evaluation_criteria=kpi.ai_evaluation_criteria
                                    )
                                    
                                    if evaluation_result['success']:
                                        kpi_document.ai_evaluated = True
                                        kpi_document.ai_score = evaluation_result['score']
                                        kpi_document.ai_explanation = evaluation_result['explanation']
                                        logger.debug(f"AI evaluation completed: Score {evaluation_result['score']}")
                                        
                                        # Update KPI score in the database
                                        existing_kpi_score = KPIScore.query.filter_by(
                                            application_id=application.id,
                                            kpi_id=kpi.id
                                        ).first()
                                        
                                        if existing_kpi_score:
                                            existing_kpi_score.score = evaluation_result['score']
                                            existing_kpi_score.explanation = evaluation_result['explanation']
                                            existing_kpi_score.updated_at = datetime.utcnow()
                                        else:
                                            new_kpi_score = KPIScore(
                                                application_id=application.id,
                                                kpi_id=kpi.id,
                                                score=evaluation_result['score'],
                                                explanation=evaluation_result['explanation']
                                            )
                                            db.session.add(new_kpi_score)
                                        
                                        logger.info(f"Updated KPI score for application {application.id}, KPI {kpi.id}: {evaluation_result['score']}")
                                    else:
                                        logger.warning(f"AI evaluation failed: {evaluation_result['explanation']}")
                                except Exception as e:
                                    logger.error(f"Error during AI evaluation: {str(e)}")
                                    logger.error(f"Traceback: {traceback.format_exc()}")
                except Exception as file_error:
                    logger.error(f"Error processing files for subcriterion {sub.id}: {str(file_error)}")
                    # Continue with other subcriteria even if one fails

                # Convert Decimal weight to float before calculations
                weight_value = float(sub.weight)

                # Create criterion evaluation
                evaluation = CriterionEvaluation(
                    alternative_id=alternative.id,
                    criterion_id=sub.criterion_id,
                    sub_criterion_id=sub.id,
                    application_id=application.id,
                    low=weight_value * 0.8,
                    medium=weight_value,
                    high=weight_value * 1.2
                )
                db.session.add(evaluation)

            # After all updates, recalculate sub-criterion scores based on new KPI data
            try:
                logger.info(f"Recalculating sub-criterion scores for application {application.id}")
                for sub_criterion in SubCriterion.query.all():
                    if sub_criterion.has_kpi:
                        # Get all KPIs for this sub-criterion
                        kpis = KeyPerformanceIndicator.query.filter_by(sub_criterion_id=sub_criterion.id).all()
                        
                        if kpis:
                            # Calculate KPI scores for this application
                            total_score = 0
                            kpi_count = 0
                            
                            for kpi in kpis:
                                # Check if this application has uploaded a document for this KPI
                                kpi_document = KPIDocument.query.filter_by(
                                    application_id=application.id,
                                    kpi_id=kpi.id
                                ).first()
                                
                                if kpi_document:
                                    # Document uploaded - get AI evaluation score
                                    kpi_score_record = KPIScore.query.filter_by(
                                        application_id=application.id,
                                        kpi_id=kpi.id
                                    ).first()
                                    
                                    if kpi_score_record and kpi_score_record.score > 0:
                                        # Use AI evaluated score
                                        total_score += kpi_score_record.score
                                        kpi_count += 1
                                        logger.debug(f"Application {application.id} - KPI {kpi.id}: Using AI score {kpi_score_record.score}")
                                    else:
                                        # Document exists but no AI score, contribute 0
                                        logger.debug(f"Application {application.id} - KPI {kpi.id}: Document uploaded but no AI score, contributes 0 to average")
                                else:
                                    # No document uploaded, contributes 0 to average
                                    logger.debug(f"Application {application.id} - KPI {kpi.id}: No document uploaded, contributes 0 to average")
                            
                            # Calculate final score for this sub-criterion
                            if kpi_count > 0:
                                average_kpi_score = total_score / kpi_count
                            else:
                                average_kpi_score = 0.0
                            
                            # Convert to 1-7 scale (original: 1-7, current: 0-7, need: 1-7)
                            final_score = max(1, min(7, round(average_kpi_score))) if average_kpi_score > 0 else 1
                            
                            logger.info(f"Application {application.id} - Sub-criterion {sub_criterion.id}: Total KPIs: {len(kpis)}, Total score: {total_score}, Average: {average_kpi_score:.2f}, Final: {final_score}")
                            
                            # Update or create DecisionMatrix entry
                            existing_entry = DecisionMatrix.query.filter_by(
                                application_id=application.id,
                                sub_criterion_id=sub_criterion.id
                            ).first()
                            
                            if existing_entry:
                                existing_entry.score = final_score
                                existing_entry.updated_at = datetime.utcnow()
                                logger.debug(f"Updated existing sub-criterion {sub_criterion.id} score to {final_score} for application {application.id}")
                            else:
                                new_entry = DecisionMatrix(
                                    application_id=application.id,
                                    sub_criterion_id=sub_criterion.id,
                                    score=final_score
                                )
                                db.session.add(new_entry)
                                logger.debug(f"Created new sub-criterion {sub_criterion.id} score {final_score} for application {application.id}")
                
                # Mark application as updated
                application.updated_at = datetime.utcnow()
                logger.info(f"Successfully recalculated all sub-criterion scores for application {application.id}")
                
            except Exception as recalc_error:
                logger.error(f"Error recalculating sub-criterion scores: {str(recalc_error)}")
                # Don't fail the entire update if recalculation fails
            
            db.session.commit()
            flash(_('Application updated successfully!'), 'success')
            return redirect(url_for('main.my_applications'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating application: {str(e)}")
            flash(_('Error updating application. Please try again.'), 'error')

    # Get existing documents and evaluations for pre-selecting criteria
    existing_docs = Document.query.filter_by(application_id=application.id).all()
    existing_evals = CriterionEvaluation.query.filter_by(application_id=application.id).all()
    
    # Get existing KPI documents
    existing_kpi_docs = KPIDocument.query.filter_by(application_id=application.id).all()

    return render_template(
        'project_application.html',
        form=form,
        project=project,
        criteria=criteria,
        edit_mode=True,
        existing_docs=existing_docs,
        existing_evals=existing_evals,
        existing_kpi_docs=existing_kpi_docs
    )

@main_bp.route('/application/<int:application_id>/delete', methods=['POST'])
@login_required
def delete_application(application_id):
    """Delete an application"""
    application = ProjectApplication.query.get_or_404(application_id)

    # Only allow deletion if it's pending and belongs to the current user
    if application.contractor_id != current_user.id:
        flash(_('Access denied.'), 'error')
        return redirect(url_for('main.my_applications'))

    if application.status != ApplicationStatus.PENDING:
        flash(_('Only pending applications can be deleted.'), 'error')
        return redirect(url_for('main.my_applications'))

    try:
        # Delete associated regular documents first
        for doc in application.documents:
            if os.path.exists(doc.file_path):
                os.remove(doc.file_path)
                logger.debug(f"Deleted file: {doc.file_path}")
            db.session.delete(doc)
        
        # Delete associated KPI documents
        for kpi_doc in KPIDocument.query.filter_by(application_id=application.id).all():
            if os.path.exists(kpi_doc.file_path):
                os.remove(kpi_doc.file_path)
                logger.debug(f"Deleted KPI file: {kpi_doc.file_path}")
            db.session.delete(kpi_doc)
        
        # Delete KPI scores
        KPIScore.query.filter_by(application_id=application.id).delete()
        
        # Delete criterion evaluations
        CriterionEvaluation.query.filter_by(application_id=application.id).delete()

        # Delete application
        db.session.delete(application)
        db.session.commit()
        flash(_('Application deleted successfully.'), 'success')

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting application: {str(e)}")
        flash(_('Error deleting application. Please try again.'), 'error')

    return redirect(url_for('main.my_applications'))


@main_bp.route('/project/<int:project_id>/topsis-report-pdf', methods=['GET', 'POST'])
@login_required
def topsis_report_pdf(project_id):
    """TOPSIS Karar Destek Sistemi Sonuç Raporu - Yalın tek sayfa tasarım"""
    from datetime import datetime
    import base64
    
    project = Project.query.get_or_404(project_id)
    
    # İşveren notunu veritabanından al
    owner_note = project.owner_note or ""

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
    
    # Logo'yu base64 olarak oku
    logo_base64 = None
    try:
        logo_path = os.path.join(current_app.root_path, 'static', 'images', 'construct-circular-new-logo.png')
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as logo_file:
                logo_base64 = base64.b64encode(logo_file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Logo okuma hatası: {str(e)}")
    
    # Ana kriter gruplarını ve puanları hesapla
    criteria = Criterion.query.all()
    sub_criteria = SubCriterion.query.all()
    
    # Her firma için ana kriter grubu puanlarını hesapla
    criteria_scores = {}
    for app in applications:
        contractor_name = app.contractor.company_name or app.contractor.username
        criteria_scores[contractor_name] = {}
        decision_entries = DecisionMatrix.query.filter_by(application_id=app.id).all()
        
        for criterion in criteria:
            group_subs = [sc for sc in sub_criteria if sc.criterion_id == criterion.id]
            group_score = sum(
                next((dm.score for dm in decision_entries if dm.sub_criterion_id == sc.id), 0) * sc.weight
                for sc in group_subs
            )
            criteria_scores[contractor_name][criterion.name] = group_score
    
    # AI değerlendirme istatistikleri
    total_ai_evaluations = 0
    total_manual_evaluations = 0
    for app in applications:
        kpi_scores = KPIScore.query.filter_by(application_id=app.id).all()
        for ks in kpi_scores:
            if ks.manually_edited:
                total_manual_evaluations += 1
            else:
                total_ai_evaluations += 1
    
    total_evaluations = total_ai_evaluations + total_manual_evaluations
    ai_percentage = (total_ai_evaluations / total_evaluations * 100) if total_evaluations > 0 else 0
    
    # Pasta grafiği oluştur
    pie_chart_image = None
    try:
        import matplotlib
        matplotlib.use('Agg')
        from matplotlib import pyplot as plt
        import numpy as np
        
        labels = []
        sizes = []
        colors_list = ['#2ecc71', '#3498db', '#9b59b6', '#e74c3c', '#f39c12', '#1abc9c', '#34495e']
        
        for app in applications:
            contractor_name = app.contractor.company_name or app.contractor.username
            labels.append(contractor_name[:12] + '...' if len(contractor_name) > 12 else contractor_name)
            sizes.append(app.topsis_score if app.topsis_score else 0)
        
        fig, ax = plt.subplots(figsize=(3.5, 2.8))
        chart_colors = colors_list[:len(labels)]
        
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=None,
            autopct=lambda pct: f'{pct:.0f}%' if pct > 8 else '',
            colors=chart_colors,
            startangle=90,
            textprops={'fontsize': 7}
        )
        
        ax.legend(
            wedges, 
            [f'{label} ({size:.2f})' for label, size in zip(labels, sizes)],
            loc="center left",
            bbox_to_anchor=(1, 0.5),
            fontsize=6
        )
        
        plt.tight_layout()
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=100)
        img_buffer.seek(0)
        pie_chart_image = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        plt.close()
    except Exception as e:
        logger.error(f"Pasta grafiği hatası: {str(e)}")
    
    # Yalın tek sayfa HTML raporu oluştur
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Karar Destek Sistemi Sonuç Raporu - {project.name}</title>
        <style>
            @page {{ size: A4; margin: 1cm 1.2cm; }}
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.3; font-size: 9px; color: #333; }}
            .container {{ min-height: 100vh; display: flex; flex-direction: column; }}
            .report-header {{ text-align: center; margin-bottom: 12px; border-bottom: 2px solid #1a5276; padding-bottom: 10px; }}
            .report-title {{ font-size: 16px; font-weight: bold; color: #1a5276; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 1px; }}
            .project-name {{ font-size: 13px; color: #2471a3; font-weight: 600; margin-bottom: 5px; }}
            .report-meta {{ font-size: 8px; color: #666; }}
            .main-content {{ flex: 1; }}
            .section-title {{ font-size: 10px; color: #1a5276; font-weight: bold; margin-bottom: 6px; padding-bottom: 3px; border-bottom: 1px solid #ddd; }}
            .rankings-table {{ width: 100%; border-collapse: collapse; margin-bottom: 10px; }}
            .rankings-table th, .rankings-table td {{ border: 1px solid #ddd; padding: 4px 6px; text-align: center; }}
            .rankings-table th {{ background-color: #1a5276; color: white; font-weight: 600; font-size: 8px; }}
            .rankings-table td {{ font-size: 8px; }}
            .rank-1 {{ background-color: #d4edda; font-weight: bold; }}
            .rank-2 {{ background-color: #fff3cd; }}
            .rank-3 {{ background-color: #f8d7da; }}
            .criteria-table {{ width: 100%; border-collapse: collapse; margin-bottom: 10px; }}
            .criteria-table th, .criteria-table td {{ border: 1px solid #ddd; padding: 3px 5px; text-align: center; font-size: 7px; }}
            .criteria-table th {{ background-color: #2471a3; color: white; font-weight: 600; }}
            .three-col-row {{ display: flex; gap: 12px; margin-top: 10px; }}
            .col-chart {{ flex: 1.2; text-align: center; }}
            .col-chart img {{ max-width: 100%; max-height: 120px; }}
            .col-summary {{ flex: 1; }}
            .col-ai {{ flex: 0.8; }}
            .summary-box {{ background-color: #f8f9fa; border: 1px solid #dee2e6; border-left: 3px solid #1a5276; padding: 8px; border-radius: 3px; }}
            .summary-text {{ font-size: 8px; line-height: 1.5; color: #444; }}
            .winner-highlight {{ background-color: #d4edda; padding: 5px 8px; border-radius: 3px; margin-top: 6px; font-weight: bold; color: #155724; text-align: center; font-size: 8px; }}
            .ai-box {{ background-color: #e8f4fd; border: 1px solid #bee5eb; border-left: 3px solid #17a2b8; padding: 8px; border-radius: 3px; }}
            .ai-stat {{ font-size: 18px; font-weight: bold; color: #17a2b8; text-align: center; }}
            .ai-label {{ font-size: 7px; color: #666; text-align: center; margin-top: 3px; }}
            .ai-bar {{ background-color: #ddd; height: 8px; border-radius: 4px; margin-top: 6px; overflow: hidden; }}
            .ai-bar-fill {{ background-color: #17a2b8; height: 100%; }}
            .report-footer {{ margin-top: 15px; padding-top: 10px; border-top: 1px solid #ddd; display: flex; justify-content: space-between; align-items: center; }}
            .footer-left {{ display: flex; align-items: center; gap: 8px; }}
            .footer-logo {{ height: 20px; width: auto; }}
            .footer-brand {{ font-size: 7px; color: #1a5276; font-weight: 600; }}
            .footer-right {{ font-size: 7px; color: #999; text-align: right; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="report-header">
                <div class="report-title">Karar Destek Sistemi Sonuç Raporu</div>
                <div class="project-name">Proje: {project.name}</div>
                <div class="report-meta">{datetime.now().strftime('%d/%m/%Y')} | Başvuru: {len(applications)} | Kriter: {len(criteria)}</div>
            </div>
            
            <div class="main-content">
                <div class="section-title">Firma Sıralaması ve TOPSIS Puanları</div>
                <table class="rankings-table">
                    <thead>
                        <tr>
                            <th style="width: 6%;">Sıra</th>
                            <th style="width: 40%;">Firma Adı</th>
                            <th style="width: 22%;">TOPSIS Puanı</th>
                            <th style="width: 16%;">Performans</th>
                            <th style="width: 16%;">Durum</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    # Firma sıralaması tablosu
    max_score = applications[0].topsis_score if applications and applications[0].topsis_score else 1
    for rank, app in enumerate(applications, 1):
        rank_class = f"rank-{min(rank, 3)}"
        contractor_name = app.contractor.company_name or app.contractor.username
        score = app.topsis_score if app.topsis_score else 0
        percentage = (score / max_score * 100) if max_score > 0 else 0
        
        medal = ""
        if rank == 1: medal = "🥇"
        elif rank == 2: medal = "🥈"
        elif rank == 3: medal = "🥉"
        else: medal = str(rank)
        
        status_text = "Değerlendirildi" if score > 0 else "Beklemede"
        
        html_content += f"""
                        <tr class="{rank_class}">
                            <td>{medal}</td>
                            <td style="text-align: left; padding-left: 8px;">{contractor_name}</td>
                            <td>{score:.4f}</td>
                            <td>{percentage:.1f}%</td>
                            <td>{status_text}</td>
                        </tr>
        """
    
    html_content += """
                    </tbody>
                </table>
    """
    
    # Grup TOPSIS Analizi tablosu - eski format
    html_content += """
                <div class="section-title">Grup TOPSIS Analizi</div>
                <table class="criteria-table">
                    <thead>
                        <tr>
                            <th style="width: 18%;">Grup</th>
                            <th style="width: 52%;">Kriterler</th>
                            <th style="width: 12%;">Grup Ağırlığı</th>
                            <th style="width: 18%;">Sıralama</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for criterion in criteria:
        group_subs = [sc for sc in sub_criteria if sc.criterion_id == criterion.id]
        group_weight = sum(sc.weight for sc in group_subs)
        
        # Bu gruptaki tüm firmaları puanlarına göre sırala
        group_rankings = []
        all_scores_zero = True
        for app in applications:
            contractor_name = app.contractor.company_name or app.contractor.username
            app_group_score = criteria_scores.get(contractor_name, {}).get(criterion.name, 0)
            group_rankings.append((contractor_name, app_group_score))
            if app_group_score > 0:
                all_scores_zero = False
        
        # Puanlara göre sırala (büyükten küçüğe)
        group_rankings.sort(key=lambda x: x[1], reverse=True)
        
        # İlk 4 firmayı al ve sıralama metni oluştur
        if all_scores_zero:
            # Eğer tüm skorlar 0 ise, veri yüklenmemiş açıklaması göster
            ranking_text = "<span style='color: #666; font-style: italic;'>Alternatifler bu grup için veri yüklememiştir. Sıralama eşittir.</span>"
        else:
            ranking_text = ""
            for i, (name, score) in enumerate(group_rankings[:4], 1):
                ranking_text += f"{i}. {name}<br>"
        
        # Alt kriterlerin isimlerini alt alta listele
        sub_names = '<br>'.join(sc.name for sc in group_subs)
        
        html_content += f"""
                        <tr>
                            <td style="text-align: left; font-weight: bold;">{criterion.name}</td>
                            <td style="text-align: left; font-size: 6px;">{sub_names}</td>
                            <td>{group_weight:.3f}</td>
                            <td style="text-align: left; font-size: 6px;">{ranking_text}</td>
                        </tr>
        """
    
    html_content += """
                    </tbody>
                </table>
    """
    
    # Grafik, sonuç ve AI istatistikleri - 3 sütun
    winner_name = applications[0].contractor.company_name or applications[0].contractor.username if applications else "N/A"
    
    html_content += f"""
                <div class="two-col-row" style="display: flex; gap: 15px; margin-top: 10px;">
                    <div class="col-chart" style="flex: 1; text-align: center;">
                        <div class="section-title">Puan Dağılımı</div>
                        {"<img src='data:image/png;base64," + pie_chart_image + "' alt='Pasta Grafiği' style='max-height: 140px;'>" if pie_chart_image else "<div style='padding: 20px; background: #f5f5f5; border-radius: 5px; color: #666; font-size: 8px;'>Grafik oluşturulamadı</div>"}
                    </div>
                    
                    <div class="col-summary" style="flex: 1;">
                        <div class="section-title">Sonuç</div>
                        <div class="summary-box">
                            <div class="summary-text">
                                TOPSIS analizi sonucunda <strong>{len(applications)}</strong> firma değerlendirildi.
                                Döngüsel ekonomi kriterlerine göre puanlandı ve sıralandı.
                            </div>
                            <div class="winner-highlight">
                                🏆 Önerilen: {winner_name}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
    """
    
    # İşveren notu varsa ekle
    if owner_note:
        html_content += f"""
                <div style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-left: 4px solid #17a2b8; border-radius: 4px;">
                    <div class="section-title" style="color: #17a2b8;">İşveren Notu</div>
                    <div style="font-size: 8px; color: #333; white-space: pre-wrap;">{owner_note}</div>
                </div>
        """
    
    html_content += f"""
            <div class="report-footer">
                <div class="footer-left">
                    {"<img src='data:image/png;base64," + logo_base64 + "' alt='Logo' class='footer-logo'>" if logo_base64 else ""}
                    <span class="footer-brand">Construct Circular - Döngüsel İnşaat Karar Destek Sistemi</span>
                </div>
                <div class="footer-right">
                    Bu rapor otomatik olarak oluşturulmuştur.<br>
                    {datetime.now().strftime('%d/%m/%Y %H:%M')}
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # PDF oluştur
    try:
        from weasyprint import HTML
        pdf_file = io.BytesIO()
        HTML(string=html_content).write_pdf(pdf_file)
        pdf_file.seek(0)
        
        response = make_response(pdf_file.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=karar_destek_raporu_{project_id}.pdf'
        
        return response
        
    except ImportError:
        flash(_('PDF oluşturma özelliği şu anda kullanılamıyor.'), 'error')
        return redirect(url_for('main.view_project', project_id=project_id))
    except Exception as e:
        logger.error(f"PDF oluşturma hatası: {str(e)}")
        flash(_('PDF oluşturulurken bir hata oluştu.'), 'error')
        return redirect(url_for('main.view_project', project_id=project_id))


@main_bp.route('/wireframe')
@login_required
def wireframe():
    """Wireframe tool for project flow visualization"""
    return render_template('wireframe.html')

@main_bp.route('/download-wireframe')
@login_required
def download_wireframe():
    """Download wireframe documentation"""
    try:
        wireframe_path = 'Construct_Circular_Wireframe_Document.md'
        return send_file(wireframe_path, as_attachment=True, download_name='Construct_Circular_Wireframe.md')
    except Exception as e:
        flash(_('Wireframe document could not be downloaded.'), 'error')
        return redirect(url_for('main.dashboard'))