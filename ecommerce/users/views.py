from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from datetime import timedelta
from .permissions import IsAdmin
from .utils import generate_otp, send_otp, send_password_reset_link
from .models import CustomUser
from .models import PasswordReset
from .serializers import CustomUserSerializer, ResetPasswordRequestSerializer, ResetPasswordSerializer


class VerifyOTP(APIView):

    def post(self, request):
        email = request.data.get('email')
        otp_entered = request.data.get('otp')

        try:
            user = CustomUser.objects.get(email=email, otp=otp_entered)
            user.is_verified = True
            user.save()
            return Response({'message': 'Email verified successfully.'},
                            status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'detail': 'Invalid OTP'},
                            status=status.HTTP_400_BAD_REQUEST)


class CustomerRegistration(APIView):

    def post(self, request, *args, **kwargs):
        request.data['role'] = 'CUSTOMER'
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():

            user = serializer.save()

            otp = generate_otp()
            user.otp = otp
            user.save()

            send_otp(user.email, otp)

            return Response(
                {
                    'message':
                        'Customer registered successfully. OTP sent to your email.'
                },
                status=status.HTTP_201_CREATED)

        is_duplicate = False
        for field, errors in serializer.errors.items():
            for error in errors:
                if getattr(error, 'code', '') == 'unique':
                    is_duplicate = True
                    break
            if is_duplicate:
                break

        final_status = status.HTTP_409_CONFLICT if is_duplicate else status.HTTP_400_BAD_REQUEST

        return Response(serializer.errors, status=final_status)


class RetailerRegistration(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, *args, **kwargs):
        request.data['role'] = 'RETAILER'
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():

            user = serializer.save()

            otp = generate_otp()
            user.otp = otp
            user.save()

            send_otp(user.email, otp)

            return Response(
                {
                    'message':
                        'Retailer registered successfully. OTP sent to your email.'
                },
                status=status.HTTP_201_CREATED)

        is_duplicate = False
        for field, errors in serializer.errors.items():
            for error in errors:
                if getattr(error, 'code', '') == 'unique':
                    is_duplicate = True
                    break
            if is_duplicate:
                break

        final_status = status.HTTP_409_CONFLICT if is_duplicate else status.HTTP_400_BAD_REQUEST

        return Response(serializer.errors, status=final_status)


class RequestPasswordReset(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
        user = CustomUser.objects.filter(email__iexact=email).first()
        if not email:
            return Response({"error": "Email is required"},
                            status=status.HTTP_400_BAD_REQUEST)
        redirect_url = request.data.get('redirect_url', '')

        if user:
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            reset = PasswordReset(email=email, token=token)
            reset.save()

            reset_url = f"{redirect_url}?token={token}"
            send_password_reset_link(user.email, reset_url)

            return Response(
                {'success': 'We have sent you a link to reset your password'},
                status=status.HTTP_200_OK)
        else:
            return Response({"error": "User with credentials not found"},
                            status=status.HTTP_404_NOT_FOUND)


class ResetPassword(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = []

    def post(self, request, token):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reset_obj = PasswordReset.objects.filter(token=token).first()

        expiry_period = timedelta(hours=1)
        if not reset_obj or (timezone.now() - reset_obj.created_at
                             > expiry_period):
            return Response({'error': 'Invalid or expired token'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.filter(email=reset_obj.email).first()

        if user:
            user.set_password(serializer.validated_data['new_password'])
            user.is_verified = True
            user.save()

            PasswordReset.objects.filter(email=reset_obj.email).delete()

            return Response({'success': 'Password updated'},
                            status=status.HTTP_200_OK)

        return Response({'error': 'User not found'},
                        status=status.HTTP_404_NOT_FOUND)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response({'message': 'Password changed successfully'},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfile(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer

    def get_object(self):
        return self.request.user
