from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):

        if not user.is_verified:
            raise AuthenticationFailed(
                "User is not verified. Try Forgot Password to verify")

        token = super().get_token(user)
        token['role'] = user.role
        token['email'] = user.email

        return token
