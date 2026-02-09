from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.conf import settings
from smtplib import SMTPException
import random
import logging

logger = logging.getLogger(__name__)


def generate_otp(length=6):
    otp_chars = "0123456789"
    otp = ''.join(random.choice(otp_chars) for _ in range(length))
    return otp


def send_otp(email, otp):
    subject = 'Verify Your Email'
    from_email = settings.EMAIL_HOST_USER
    to_email = [email]

    html_message = f"""
    <html>
        <body>
            <p>Hello,</p>
            <p>Thank you for registering. Please use the verification code below to verify your email address:</p>
            <div style="background-color: #f4f4f4; padding: 15px; text-align: center; border-radius: 5px; margin: 20px 0;">
                <span style="font-size: 24px; font-weight: bold; letter-spacing: 5px; color: #333;">{otp}</span>
            </div>
            <p>If you did not request this verification, please ignore this email.</p>
            <br>
            <p>Best regards,<br>The Team</p>
        </body>
    </html>
    """

    plain_message = strip_tags(html_message)

    try:
        send_mail(subject,
                  plain_message,
                  from_email,
                  to_email,
                  html_message=html_message,
                  fail_silently=False)
        return True
    except SMTPException as e:
        logger.error(f"Failed to send OTP email to {email}: {e}")
        return False


def send_password_reset_link(email, link):
    subject = 'Reset Your Password'
    from_email = settings.EMAIL_HOST_USER
    to_email = [email]

    html_message = f"""
    <html>
        <body>
            <p>Hello,</p>
            <p>We received a request to reset your password.</p>
            <p>Click the link below to set a new password:</p>
            <p>
                <a href="{link}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Reset Password
                </a>
            </p>
            <p>Or copy and paste this URL into your browser:</p>
            <p>{link}</p>
            <p>If you didn't request this, you can safely ignore this email.</p>
            <br>
            <p>Best regards,<br>The Team</p>
        </body>
    </html>
    """

    plain_message = strip_tags(html_message)

    try:
        send_mail(subject,
                  plain_message,
                  from_email,
                  to_email,
                  html_message=html_message,
                  fail_silently=False)
        return True
    except SMTPException as e:
        logger.error(f"Failed to send password reset email to {email}: {e}")
        return False
