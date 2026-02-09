from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class EmailBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to fetch the user by email
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None

        # Check the password and if the user is active
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
