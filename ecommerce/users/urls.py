from django.urls import path
from .views import *

urlpatterns = [
    path('register-customer/', CustomerRegistration.as_view(), name='register-customer'),
    path('register-retailer/', RetailerRegistration.as_view(), name='register-retailer'),
    path('verify/', VerifyOTP.as_view(), name='verify'),
    path('forgot-password/', RequestPasswordReset.as_view(), name='request-password-reset'),
    path('password-reset/<str:token>/', ResetPassword.as_view(), name='password-reset-confirm'),
    path('profile/', UserProfile.as_view(), name='user-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]