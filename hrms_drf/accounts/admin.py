from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
User = get_user_model()

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + ( (None, {'fields': ('role',)}),)
    list_display = [
        "email",
        "username",
        "is_staff",
        "is_active",
        "role",
    ]

admin.site.register(User,CustomUserAdmin)