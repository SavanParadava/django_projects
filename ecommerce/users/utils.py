import random
from django.core.mail import send_mail
from django.conf import settings

def generate_otp(length=6):
    otp_chars = "0123456789" 
    otp = ''.join(random.choice(otp_chars) for _ in range(length))
    return otp

def send_otp_email(email, otp):
    subject = 'Verification OTP'
    message = f'Your OTP for email verification is: {otp}. Please use this OTP to verify your email.'
    from_email = settings.EMAIL_HOST_USER
    to_email = [email]
    send_mail(subject, message, from_email, to_email)
