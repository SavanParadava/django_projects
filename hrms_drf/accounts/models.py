from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('HR', 'HR'),
        ('EMPLOYEE', 'Employee'),
    ]

    role = models.CharField(max_length=20,
                            choices=ROLE_CHOICES,
                            default='EMPLOYEE')
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True)

    def save(self, *args, **kwargs):
        """Auto-set role to ADMIN if superuser"""
        if self.is_superuser:
            self.role = 'ADMIN'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"
