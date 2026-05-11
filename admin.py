from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import User, db, UserRole, Criterion, Project, ProjectApplication
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
import functools
import logging

logger = logging.getLogger(__name__)

# Admin blueprints
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin Login Form
class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Hardcoded admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD_HASH = generate_password_hash('admin1234')

def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Lütfen önce giriş yapın.', 'error')
            return redirect(url_for('admin.login'))

        if not current_user.is_administrator():
            flash('Bu sayfaya erişim yetkiniz yok.', 'error')
            return redirect(url_for('main.dashboard'))

        return f(*args, **kwargs)
    return decorated_function

# Admin routes
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and current_user.is_administrator():
        return redirect(url_for('admin.index'))
        
    form = AdminLoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            try:
                # Find or create admin user
                admin_user = User.query.filter_by(username=ADMIN_USERNAME).first()
                if not admin_user:
                    admin_user = User(
                        username=ADMIN_USERNAME,
                        email='admin@example.com',
                        password_hash=ADMIN_PASSWORD_HASH,
                        is_admin=True,
                        role=UserRole.COMPANY
                    )
                    db.session.add(admin_user)
                    db.session.commit()
                else:
                    # Ensure existing admin user has correct role and is_admin flag
                    if not admin_user.is_admin or admin_user.role != UserRole.COMPANY:
                        admin_user.is_admin = True
                        admin_user.role = UserRole.COMPANY
                        db.session.commit()

                login_user(admin_user)
                flash('Admin paneline hoşgeldiniz!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page if next_page else url_for('admin.index'))

            except Exception as e:
                db.session.rollback()
                logger.error(f"Error during admin login: {str(e)}")
                flash('Giriş sırasında bir hata oluştu. Lütfen tekrar deneyin.', 'error')

        flash('Geçersiz kullanıcı adı veya şifre', 'error')

    return render_template('admin/auth/login.html', form=form)

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Çıkış yaptınız.', 'info')
    return redirect(url_for('admin.login'))

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

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """Display user management interface"""
    users = User.query.all()
    return render_template('admin/users.html', users=users)