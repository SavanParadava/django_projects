from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import CustomUser
from datetime import timedelta
from django.utils import timezone


class CustomUserCreationForm(AdminUserCreationForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email")

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email")

class ModifiedAuthenticationForm(AuthenticationForm):

    def fetch_error_1(self,user):
        return ValidationError(
                    f"Please enter a correct {user.username} and password. Note that both fields may be case-sensitive. You have {3 - user.failed_attempts} Attempts Left.",
                    code="invalid_login",
                    params={"username": self.username_field.verbose_name},
                )

    def fetch_error_2(self,user):
        return ValidationError(
                    f"Your account has been blocked for {user.blocked_until-timezone.now()}",
                    code="invalid_login",
                )

    def confirm_login_allowed(self, user):
        if user.blocked_until and not user.unblock_if_expired():
            raise self.fetch_error_2(user)
        
        if not user.blocked_until:
            user.reset_failed_count()
        
        return super().confirm_login_allowed(user)
    
    
    def get_invalid_login_error(self):
        try:
            user = CustomUser.objects.get(username = self.cleaned_data.get("username"))
        except:
            return ValidationError(
            self.error_messages["invalid_login"],
            code="invalid_login",
            params={"username": self.username_field.verbose_name},
        )
        
        if user.blocked_until and not user.unblock_if_expired():
            return self.fetch_error_2(user)
        
        user.increment_failed_count()
        
        if user.failed_attempts >= 3:
            user.block_for_time(10)
            return self.fetch_error_2(user)
        
        return self.fetch_error_1(user)