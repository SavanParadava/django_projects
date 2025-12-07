from django.db import models

# Create your models here.
class IpCount(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    first_request_time = models.DateTimeField(auto_now_add=True)
    tokens_spent = models.IntegerField(default=1)
