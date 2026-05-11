import os
import logging
from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel, get_locale
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
csrf = CSRFProtect()
login_manager = LoginManager()
babel = Babel()

# create the app
app = Flask(__name__)

# Apply ProxyFix to handle X-Forwarded headers from Replit's proxy
# This ensures Flask sees the correct protocol (HTTPS) and host
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Configure Jinja2 environment for translations
app.jinja_env.add_extension('jinja2.ext.i18n')

# setup a secret key, required by sessions
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///fuzzy_topsis.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 250 * 1024 * 1024  # 250MB max file size
app.config["WTF_CSRF_ENABLED"] = False  # Disable CSRF protection temporarily to fix form issues
# app.config["WTF_CSRF_TIME_LIMIT"] = None  # No time limit for CSRF tokens
app.config['BABEL_DEFAULT_LOCALE'] = 'tr'  # Changed default to Turkish
app.config['LANGUAGES'] = {
    'en': 'English',
    'tr': 'Türkçe'
}

# Session cookie settings for cross-domain compatibility (preview iframe)
# SameSite=None is required for cookies to work in iframe (Replit preview)
# Secure=True is required when SameSite=None (cookies only sent over HTTPS)
# ProxyFix above ensures Flask sees the request as HTTPS via X-Forwarded-Proto
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Required for iframe/cross-site context
app.config['SESSION_COOKIE_SECURE'] = True  # Required with SameSite=None
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access
app.config['REMEMBER_COOKIE_SAMESITE'] = 'None'
app.config['REMEMBER_COOKIE_SECURE'] = True

def get_locale_selector():
    if 'language' in session:
        return session['language']
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys())

# initialize the app with extensions
db.init_app(app)
csrf.init_app(app)
login_manager.init_app(app)
babel.init_app(app, locale_selector=get_locale_selector)

# Configure login manager
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Lütfen giriş yapın.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Add template context processor for get_locale
@app.context_processor
def utility_processor():
    return dict(get_locale=get_locale)

# Create application context
with app.app_context():
    try:
        # Import models first
        from models import User, Project, Criterion, SubCriterion, Document, Alternative, CriterionEvaluation, ProjectApplication

        # Import and register blueprints
        from auth import auth_bp
        from routes import main_bp
        from admin import admin_bp
        from admin_login import admin_login_bp
        from reports import reports_bp as reports_folder_bp

        # Register blueprints without url_prefix unless specifically needed
        app.register_blueprint(auth_bp)
        app.register_blueprint(main_bp)
        app.register_blueprint(admin_bp)  # URL prefix is defined in blueprint
        app.register_blueprint(admin_login_bp)  # URL prefix is defined in blueprint
        app.register_blueprint(reports_folder_bp, url_prefix='/reports')

        # Create all tables
        db.create_all()
        logger.info("Database tables created successfully")
        logger.info("Blueprints registered successfully")
    except Exception as e:
        logger.error(f"Error during initialization: {str(e)}")
        raise

# Error handlers
@app.errorhandler(413)
def request_entity_too_large(error):
    from flask import flash, redirect, url_for, request
    from flask_babel import _
    flash(_('The uploaded file is too large. Please upload a file smaller than 250MB.'), 'error')
    # Try to redirect back to the previous page, or dashboard as fallback
    return redirect(request.referrer or url_for('main.dashboard'))