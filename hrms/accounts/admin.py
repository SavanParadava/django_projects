from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + ( (None, {'fields': ('role',)}),)
    list_display = [
        "email",
        "username",
        "is_staff",
        "is_active",
        "role",
    ]

admin.site.register(CustomUser,CustomUserAdmin)