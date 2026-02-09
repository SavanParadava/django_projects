from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager


class CustomUser(AbstractUser):
    email = models.EmailField(_("email address"), unique=True, null=True)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    ROLE_CHOICES = [
        ('ADMIN', 'admin'),
        ('RETAILER', 'retailer'),
        ('CUSTOMER', 'customer'),
    ]

    role = models.CharField(max_length=20,
                            choices=ROLE_CHOICES,
                            default='CUSTOMER')

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.username


class PasswordReset(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


class IpCount(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    first_request_time = models.DateTimeField(auto_now_add=True)
    tokens_spent = models.IntegerField(default=1)
