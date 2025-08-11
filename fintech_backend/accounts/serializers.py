"""
Serializers for the accounts app.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, Account, Profile


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'phone_number', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password.')

        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""
    class Meta:
        model = Profile
        fields = [
            'avatar', 'address_line_1', 'address_line_2', 'city', 
            'state', 'postal_code', 'country', 'identity_verified'
        ]
        read_only_fields = ['identity_verified']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data."""
    profile = ProfileSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 
            'full_name', 'phone_number', 'date_of_birth', 'is_verified', 
            'date_joined', 'profile'
        ]
        read_only_fields = ['id', 'email', 'username', 'is_verified', 'date_joined']


class AccountSerializer(serializers.ModelSerializer):
    """Serializer for account data."""
    masked_account_number = serializers.CharField(read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Account
        fields = [
            'id', 'account_number', 'masked_account_number', 'account_type', 
            'balance', 'available_balance', 'status', 'is_primary', 
            'created_at', 'user_email'
        ]
        read_only_fields = [
            'id', 'account_number', 'masked_account_number', 'balance', 
            'available_balance', 'created_at', 'user_email'
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password."""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match.")
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value