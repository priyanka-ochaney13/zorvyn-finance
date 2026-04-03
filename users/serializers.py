from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles validation and creation of new users.
    """
    
    # Write-only field for password confirmation
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'role']
        extra_kwargs = {
            'password': {'write_only': True},  
            'email': {'required': True},       
        }
    
    def validate(self, attrs):
        #Check that the two password fields match.
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def validate_password(self, value):
        """
        Validate password using Django's built-in validators.
        Checks for: length, common passwords, similarity to username, etc.
        """
        validate_password(value)
        return value
    
    def create(self, validated_data):
        # Remove password2 as it's not needed for user creation
        validated_data.pop('password2')
        
        # Create user using create_user method (handles password hashing)
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Validates credentials and returns user if valid.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """
        Authenticate user with username and password.
        """
        username = attrs.get('username')
        password = attrs.get('password')
        
        # Try to authenticate user
        user = authenticate(username=username, password=password)
        
        if not user:
            raise serializers.ValidationError({
                'error': 'Invalid username or password'
            })
        
        if not user.is_active:
            raise serializers.ValidationError({
                'error': 'User account is inactive'
            })
        
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying user information.
    Used for listing users and showing user details.
    """
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user status (active/inactive).
    Only allows updating is_active field.
    """
    
    class Meta:
        model = User
        fields = ['is_active']
