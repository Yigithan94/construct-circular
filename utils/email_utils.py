import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

def send_password_reset_email(user_email: str, reset_link: str) -> bool:
    """
    Send password reset email using SMTP
    """
    try:
        # Email configuration
        sender_email = os.environ.get('EMAIL_USER')
        if not sender_email:
            logger.error("EMAIL_USER environment variable not set")
            return False

        password = os.environ.get('EMAIL_PASSWORD')
        if not password:
            logger.error("EMAIL_PASSWORD environment variable not set")
            return False

        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = user_email
        message["Subject"] = "Şifre Sıfırlama Talebi"

        # Email content
        body = f"""
        Merhaba,

        Şifrenizi sıfırlamak için aşağıdaki linke tıklayın:

        {reset_link}

        Bu linkin geçerlilik süresi 1 saattir.

        Eğer şifre sıfırlama talebinde bulunmadıysanız, bu maili dikkate almayın.

        İyi günler,
        """
        message.attach(MIMEText(body, "plain"))

        # Determine SMTP settings based on email provider
        if "@outlook.com" in sender_email.lower() or "@hotmail.com" in sender_email.lower():
            smtp_server = "smtp.office365.com"
            smtp_port = 587
            use_ssl = False
        else:  # Default to Gmail
            smtp_server = "smtp.gmail.com"
            smtp_port = 465
            use_ssl = True

        # Create SMTP session
        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()

        try:
            server.login(sender_email, password)
            server.send_message(message)
            logger.info(f"Password reset email sent to {user_email}")
            return True
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
        finally:
            server.quit()

    except Exception as e:
        logger.error(f"Error in send_password_reset_email: {str(e)}")
        return False