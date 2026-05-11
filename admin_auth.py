from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import User, db, UserRole
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
import functools
import logging

logger = logging.getLogger(__name__)
admin_auth_bp = Blueprint('admin_auth', __name__)

# Admin Login Form
class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Hardcoded admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD_HASH = generate_password_hash('admin1234')

def admin_login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_administrator():
            flash('Please log in as administrator.', 'error')
            return redirect(url_for('admin_auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_auth_bp.route('/login', methods=['GET', 'POST'])
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
                    logger.info(f"Creating new admin user: {ADMIN_USERNAME}")
                    admin_user = User(
                        username=ADMIN_USERNAME,
                        email='admin@example.com',
                        password_hash=ADMIN_PASSWORD_HASH,
                        is_admin=True,
                        role=UserRole.COMPANY  # Use the enum value directly
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
                flash('Welcome, Administrator!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page if next_page else url_for('admin.index'))

            except Exception as e:
                db.session.rollback()
                logger.error(f"Error during admin login: {str(e)}")
                flash('Error during login. Please try again.', 'error')
                return redirect(url_for('admin_auth.login'))

        flash('Invalid credentials', 'error')

    return render_template('admin/auth/login.html', form=form)

@admin_auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_auth.login'))