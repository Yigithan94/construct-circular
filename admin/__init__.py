from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from models import db, Project, Criterion, SubCriterion, Document, UserRole, User, ProjectApplication
from admin.forms import CriterionForm, SubCriterionForm
from functools import wraps
import logging
import os
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            logger.warning("Unauthenticated user attempted to access admin page")
            flash('Lütfen önce giriş yapın.', 'error')
            return redirect(url_for('auth.login'))

        if not current_user.is_administrator():
            logger.warning(f"Non-admin user {current_user.username} attempted to access admin page")
            flash('Bu sayfaya erişim yetkiniz yok.', 'error')
            return redirect(url_for('main.dashboard'))

        return f(*args, **kwargs)
    return decorated_function

# Her route'a login_required ve admin_required ekleyelim
@admin_bp.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard showing an overview of system data"""
    criteria = Criterion.query.all()
    projects = Project.query.all()
    users = User.query.all()
    users_count = len(users)

    stats = {
        'total_projects': len(projects),
        'total_criteria': len(criteria),
        'total_users': users_count,
        'total_applications': ProjectApplication.query.count()
    }

    return render_template('admin/index.html', 
                         stats=stats,
                         criteria=criteria,
                         projects=projects)

@admin_bp.route('/manage-criteria')
@login_required
@admin_required
def manage_criteria():
    """Display criteria management interface"""
    criteria = Criterion.query.all()
    return render_template('admin/criteria.html', criteria=criteria)

@admin_bp.route('/criteria/<int:criterion_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_criterion(criterion_id):
    """Delete a criterion"""
    criterion = Criterion.query.get_or_404(criterion_id)

    try:
        db.session.delete(criterion)
        db.session.commit()
        flash('Kriter başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting criterion: {str(e)}")
        flash('Kriter silinirken bir hata oluştu.', 'error')

    return redirect(url_for('admin.manage_criteria'))

@admin_bp.route('/criteria/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_criterion():
    """Create a new criterion"""
    form = CriterionForm()

    if form.validate_on_submit():
        try:
            criterion = Criterion(
                name=form.name.data,
                description=form.description.data,
                weight=form.weight.data,
                is_cost=form.is_cost.data
            )
            db.session.add(criterion)
            db.session.commit()
            flash('Kriter başarıyla oluşturuldu.', 'success')
            return redirect(url_for('admin.manage_criteria'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating criterion: {str(e)}")
            flash('Kriter oluşturulurken bir hata oluştu.', 'error')

    return render_template('admin/criterion_form.html', form=form)

@admin_bp.route('/criteria/<int:criterion_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_criterion(criterion_id):
    """Edit an existing criterion"""
    criterion = Criterion.query.get_or_404(criterion_id)
    form = CriterionForm(obj=criterion)

    if form.validate_on_submit():
        try:
            criterion.name = form.name.data
            criterion.description = form.description.data
            criterion.weight = form.weight.data
            criterion.is_cost = form.is_cost.data
            db.session.commit()
            flash('Kriter başarıyla güncellendi.', 'success')
            return redirect(url_for('admin.manage_criteria'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating criterion: {str(e)}")
            flash('Kriter güncellenirken bir hata oluştu.', 'error')

    return render_template('admin/criterion_form.html', form=form, criterion=criterion)

@admin_bp.route('/sub-criteria/<int:criterion_id>/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_sub_criterion(criterion_id):
    """Create a new sub-criterion"""
    criterion = Criterion.query.get_or_404(criterion_id)
    form = SubCriterionForm(criterion_id=criterion_id)

    if form.validate_on_submit():
        try:
            sub_criterion = SubCriterion(
                name=form.name.data,
                description=form.description.data,
                weight=form.weight.data,
                criterion_id=criterion_id
            )
            db.session.add(sub_criterion)
            db.session.commit()
            flash('Alt kriter başarıyla oluşturuldu.', 'success')
            return redirect(url_for('admin.manage_criteria'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating sub-criterion: {str(e)}")
            flash('Alt kriter oluşturulurken bir hata oluştu.', 'error')

    return render_template('admin/sub_criterion_form.html', form=form, criterion=criterion)

@admin_bp.route('/sub-criteria/<int:sub_criterion_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_sub_criterion(sub_criterion_id):
    """Edit an existing sub-criterion"""
    sub_criterion = SubCriterion.query.get_or_404(sub_criterion_id)
    form = SubCriterionForm(criterion_id=sub_criterion.criterion_id, obj=sub_criterion)

    if form.validate_on_submit():
        try:
            sub_criterion.name = form.name.data
            sub_criterion.description = form.description.data
            sub_criterion.weight = form.weight.data
            db.session.commit()
            flash('Alt kriter başarıyla güncellendi.', 'success')
            return redirect(url_for('admin.manage_criteria'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating sub-criterion: {str(e)}")
            flash('Alt kriter güncellenirken bir hata oluştu.', 'error')

    return render_template('admin/sub_criterion_form.html', 
                         form=form, 
                         sub_criterion=sub_criterion,
                         criterion=sub_criterion.criterion)

@admin_bp.route('/sub-criteria/<int:sub_criterion_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_sub_criterion(sub_criterion_id):
    """Delete a sub-criterion"""
    sub_criterion = SubCriterion.query.get_or_404(sub_criterion_id)

    try:
        db.session.delete(sub_criterion)
        db.session.commit()
        flash('Alt kriter başarıyla silindi.', 'success')
        return redirect(url_for('admin.manage_criteria'))
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting sub-criterion: {str(e)}")
        flash('Alt kriter silinirken bir hata oluştu.', 'error')
        return redirect(url_for('admin.manage_criteria'))

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """Display user management interface"""
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    """Toggle admin status for a user"""
    user = User.query.get_or_404(user_id)

    # Prevent self-demotion
    if user == current_user:
        flash('Kendi yönetici durumunuzu değiştiremezsiniz.', 'error')
        return redirect(url_for('admin.manage_users'))

    try:
        user.is_admin = not user.is_admin
        db.session.commit()
        flash(f'Yönetici ayrıcalıkları {user.username} için başarıyla {"verildi" if user.is_admin else "kaldırıldı"}.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error toggling admin status: {str(e)}")
        flash('Kullanıcı yönetici durumu güncellenirken bir hata oluştu.', 'error')

    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)

    # Prevent self-deletion
    if user == current_user:
        flash('Kendi hesabınızı silemezsiniz.', 'error')
        return redirect(url_for('admin.manage_users'))

    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'Kullanıcı {user.username} silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting user: {str(e)}")
        flash('Kullanıcı silinirken bir hata oluştu.', 'error')

    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/project-applications')
@login_required
@admin_required
def project_applications():
    """View all project applications"""
    applications = ProjectApplication.query.all()
    return render_template('admin/project_applications.html', applications=applications)

@admin_bp.route('/project-applications/<int:application_id>')
@login_required
@admin_required
def view_application(application_id):
    """View details of a specific application"""
    application = ProjectApplication.query.get_or_404(application_id)
    return render_template('admin/project_application_detail.html', application=application)

@admin_bp.route('/project-applications/<int:application_id>/status', methods=['POST'])
@login_required
@admin_required
def update_application_status(application_id):
    """Update the status of an application"""
    application = ProjectApplication.query.get_or_404(application_id)
    new_status = request.form.get('status')

    try:
        application.status = new_status
        db.session.commit()
        flash('Başvuru durumu başarıyla güncellendi.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating application status: {str(e)}")
        flash('Başvuru durumu güncellenirken bir hata oluştu.', 'error')

    return redirect(url_for('admin.project_applications'))

def save_document(file, criterion_id):
    """Helper function to save uploaded documents"""
    if not file:
        return None

    filename = secure_filename(file.filename)
    file_ext = os.path.splitext(filename)[1].lower()

    # Create uploads directory if it doesn't exist
    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # Save file
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)

    # Create document record
    document = Document(
        filename=filename,
        file_path=os.path.join('static', 'uploads', filename),
        file_type=file_ext[1:],  # Remove the dot from extension
        file_size=os.path.getsize(file_path),
        criterion_id=criterion_id
    )

    return document