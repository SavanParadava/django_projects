from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta
from django.utils import timezone


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ("admin",'Admin'),
        ("hr", 'HR'),
        ("employee",'Employee'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    failed_attempts = models.SmallIntegerField(default=0)
    blocked_until = models.DateTimeField(null=True, blank=True)

    def block_for_time(self, duration_minutes):
        self.failed_attempts = 0
        self.blocked_until = timezone.now() + timedelta(minutes=duration_minutes)
        self.save()

    def unblock_if_expired(self):
        if self.blocked_until and timezone.now() > self.blocked_until:
            self.failed_attempts = 0
            self.blocked_until = None
            self.save()
            return True
        return False
    
    def increment_failed_count(self):
        self.failed_attempts += 1
        self.save()
    
    def reset_failed_count(self):
        self.failed_attempts = 0
        self.save()

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = 'admin'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"