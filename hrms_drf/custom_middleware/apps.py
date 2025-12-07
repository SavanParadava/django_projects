from django.apps import AppConfig


class CustomMiddlewareConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "custom_middleware"
