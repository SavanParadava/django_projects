from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,
                                     validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=['ADMIN', 'HR', 'EMPLOYEE'],
                                   default='EMPLOYEE')

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password2', 'first_name',
            'last_name', 'role'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('Passwords don\'t match')
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update user with proper password hashing"""

        validated_data.pop('password2', None)

        password = validated_data.pop('password', None)

        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name',
                                                 instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.role = validated_data.get('role', instance.role)

        if password:
            instance.set_password(password)

        instance.save()

        return instance


class UserSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'role',
            'date_joined', 'photo_url'
        ]
        read_only_fields = ['id', 'date_joined']

    def get_photo_url(self, user):
        if user.photo and hasattr(user.photo, 'url'):

            # print(user.photo.url)
            request = self.context['request']
            return request.build_absolute_uri(user.photo.url)
        return None


class UserPhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['photo']
