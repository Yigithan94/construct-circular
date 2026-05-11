from app import app, db
from models import User
from werkzeug.security import generate_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

with app.app_context():
    try:
        user = User.query.filter_by(email='kalyon@example.com').first()
        
        if user:
            # Update password to "123456"
            user.password_hash = generate_password_hash("123456")
            db.session.commit()
            logger.info(f"Password updated successfully for user: {user.email}")
        else:
            logger.error("User not found")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating password: {str(e)}")