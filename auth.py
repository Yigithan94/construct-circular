from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db, UserRole
from forms import CompanyRegistrationForm, ContractorRegistrationForm, LoginForm
from flask_babel import gettext as _
from utils.email_utils import send_password_reset_email
import logging
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import os

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)

# Initialize serializer for password reset
serializer = URLSafeTimedSerializer(os.environ.get('FLASK_SECRET_KEY', 'your-secret-key'))

@auth_bp.route('/register/company', methods=['GET', 'POST'])
def register_company():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = CompanyRegistrationForm()
    if form.validate_on_submit():
        try:
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                password_hash=generate_password_hash(form.password.data),
                role=UserRole.COMPANY,
                company_name=form.company_name.data,
                company_description=form.company_description.data
            )

            db.session.add(new_user)
            db.session.commit()

            logger.info(f"Company registered successfully: {form.email.data}")
            flash(_('Kayıt başarılı! Lütfen giriş yapın.'), 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Company registration error: {str(e)}")
            flash(_('Kayıt sırasında bir hata oluştu. Lütfen tekrar deneyin.'), 'danger')

    return render_template('auth/company_register.html', form=form)

@auth_bp.route('/register/contractor', methods=['GET', 'POST'])
def register_contractor():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = ContractorRegistrationForm()
    if form.validate_on_submit():
        try:
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                password_hash=generate_password_hash(form.password.data),
                role=UserRole.CONTRACTOR,
                contractor_specialization=form.contractor_specialization.data,
                contractor_experience=form.contractor_experience.data
            )

            db.session.add(new_user)
            db.session.commit()

            logger.info(f"Contractor registered successfully: {form.email.data}")
            flash(_('Kayıt başarılı! Lütfen giriş yapın.'), 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Contractor registration error: {str(e)}")
            flash(_('Kayıt sırasında bir hata oluştu. Lütfen tekrar deneyin.'), 'danger')

    return render_template('auth/contractor_register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            logger.debug(f"Login attempt - Email: {form.email.data}, Role: {form.role.data}")
            user = User.query.filter_by(email=form.email.data).first()

            if user:
                logger.debug(f"User found - DB Role: {user.role.value}, Form Role: {form.role.data}")
                if check_password_hash(user.password_hash, form.password.data):
                    if user.role.value == form.role.data:
                        login_user(user)
                        logger.info(f"User logged in successfully: {form.email.data}")
                        flash(_('Logged in successfully!'), 'success')
                        next_page = request.args.get('next')
                        return redirect(next_page if next_page else url_for('main.dashboard'))
                    else:
                        logger.warning(f"Role mismatch - User: {form.email.data}, Expected: {user.role.value}, Got: {form.role.data}")
                        flash(_('Seçilen rol bu hesap için geçersiz.'), 'danger')
                else:
                    logger.warning(f"Invalid password for user: {form.email.data}")
                    flash(_('Geçersiz email veya şifre.'), 'danger')
            else:
                logger.warning(f"No user found with email: {form.email.data}")
                flash(_('Geçersiz email veya şifre.'), 'danger')

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash(_('Giriş yapılırken bir hata oluştu. Lütfen tekrar deneyin.'), 'danger')

    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('You have been logged out.'), 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            try:
                token = serializer.dumps(user.email, salt='password-reset-salt')
                reset_url = url_for('auth.reset_password', token=token, _external=True)

                if send_password_reset_email(user.email, reset_url):
                    flash(_('Şifre sıfırlama talimatları email adresinize gönderildi.'), 'success')
                    logger.info(f"Password reset email sent to {email}")
                else:
                    flash(_('Email gönderilirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.'), 'danger')
                    logger.error(f"Failed to send password reset email to {email}")
            except Exception as e:
                logger.error(f"Password reset error for {email}: {str(e)}")
                flash(_('Bir hata oluştu. Lütfen daha sonra tekrar deneyin.'), 'danger')
        else:
            flash(_('Şifre sıfırlama talimatları email adresinize gönderildi.'), 'success')
            logger.warning(f"Password reset attempted for non-existent email: {email}")

        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
        user = User.query.filter_by(email=email).first()

        if not user:
            flash(_('Geçersiz şifre sıfırlama linki.'), 'danger')
            return redirect(url_for('auth.login'))

        if request.method == 'POST':
            password = request.form.get('password')
            password_confirm = request.form.get('password_confirm')

            if not password or not password_confirm:
                flash(_('Lütfen tüm alanları doldurun.'), 'danger')
            elif password != password_confirm:
                flash(_('Şifreler eşleşmiyor.'), 'danger')
            else:
                user.password_hash = generate_password_hash(password)
                db.session.commit()
                flash(_('Şifreniz başarıyla güncellendi. Lütfen yeni şifrenizle giriş yapın.'), 'success')
                logger.info(f"Password reset successful for user {email}")
                return redirect(url_for('auth.login'))

        return render_template('auth/reset_password.html')

    except SignatureExpired:
        flash(_('Şifre sıfırlama linkinin süresi dolmuş.'), 'danger')
        logger.warning(f"Expired password reset token used")
        return redirect(url_for('auth.forgot_password'))
    except Exception as e:
        flash(_('Geçersiz şifre sıfırlama linki.'), 'danger')
        logger.error(f"Invalid password reset token: {str(e)}")
        return redirect(url_for('auth.login'))