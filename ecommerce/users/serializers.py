from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True,
        validators=[UniqueValidator(
                        queryset=CustomUser.objects.all(),
                        lookup='iexact',
                        message='Duplicate Email Already exists'
                    )])
    password = serializers.CharField(write_only=True,
                                     required=False,
                                     validators=[validate_password])
    role = serializers.ChoiceField(choices=['ADMIN', 'RETAILER', 'CUSTOMER'],
                                   default='CUSTOMER')
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name', 'role', 'is_verified', 'otp')
        extra_kwargs = {
            'email': {
                'validators': [
                    UniqueValidator(
                        queryset=CustomUser.objects.all(),
                        lookup='iexact',
                        message='Duplicate Email Already exists'
                    )
                ]
            },
            'username': {
                'validators': [
                    UniqueValidator(
                        queryset=CustomUser.objects.all(),
                        message='Duplicate Username Already exists'
                    )
                ]
            }
        }
    
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop("password",None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    # def validate_email(self, value):
    #     lower_email = value.lower()
    #     # If update
    #     query = CustomUser.objects.filter(email__iexact=lower_email)
    #     if self.instance:
    #         query = query.exclude(pk=self.instance.pk)
        
    #     if query.exists():
    #         raise serializers.ValidationError("Duplicate Email Already exists")
    #     return lower_email
    
    # def validate_username(self, value):
    #     query = CustomUser.objects.filter(username=value)
    #     if self.instance:
    #         query = query.exclude(pk=self.instance.pk)
            
    #     if query.exists():
    #         raise serializers.ValidationError("Duplicate Username Already exists")
    #     return value

class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data