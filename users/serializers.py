from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from djoser.serializers import TokenCreateSerializer
from rest_framework.exceptions import ValidationError
from user_agents import parse as parse_ua

from .models import DogProfile, EmailVerification, CustomUser
from .utils import generate_code, send_verification_email

User = get_user_model()

# ===========================
# User Serializer
# ===========================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'role', 'is_verified']


# ===========================
# User Registration
# ===========================
class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password']

    def create(self, validated_data):
        request = self.context.get('request')
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')
        user_agent = parse_ua(user_agent_string)

        if 'Android' in user_agent_string or user_agent.is_mobile:
            role = 'customer'
        else:
            role = 'inventory_manager'

        user = User.objects.create(
            email=validated_data['email'],
            role=role,
            is_active=False,
            is_verified=False,
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


# ===========================
# Login Serializer
# ===========================
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = authenticate(request=self.context.get('request'), email=email, password=password)
        if not user:
            raise ValidationError("Invalid email or password.")

        if not user.is_verified:
            raise ValidationError("Please verify your email before logging in.")

        data['user'] = user
        return data


# ===========================
# Token Response Serializer
# ===========================
class CustomTokenCreateSerializer(TokenCreateSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        if not user.is_verified:
            raise ValidationError("Please verify your email before logging in.")

        data['user'] = {
            'id': user.id,
            'email': user.email,
            'role': user.role,
        }
        return data


# ===========================
# Verification Code Serializer
# ===========================
class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.ChoiceField(choices=[('register', 'register'), ('reset', 'reset')])


class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=5)
    purpose = serializers.ChoiceField(choices=[('register', 'register'), ('reset', 'reset')])


# ===========================
# Password Reset Serializer
# ===========================
class ResetPasswordWithCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=5)
    new_password = serializers.CharField(min_length=6)
    purpose = serializers.ChoiceField(choices=[('reset', 'reset')])


# ===========================
# Dog Profile Serializer
# ===========================
class DogProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DogProfile
        fields = [
            'name',
            'breed',
            'gender',
            'life_stage',
            'size',
            'coat_type',
            'lifestyle',
            'health_considerations'
        ]

