from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import (
    UserRegistrationSerializer, 
    LoginSerializer,
    UserSerializer,
    UserStatusUpdateSerializer
)


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    
    POST /api/users/register/
    Body: {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "SecurePass123",
        "password2": "SecurePass123",
        "role": "viewer"  (optional, defaults to viewer)
    }
    
    Returns: User data (without password)
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]  # Anyone can register (no auth required)
    
    def create(self, request, *args, **kwargs):
        """
        Handle user registration with custom response format.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Return user data without password
        user_data = UserSerializer(user).data
        
        return Response({
            'message': 'User registered successfully',
            'user': user_data
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    """
    API endpoint for user login with JWT token generation.
    
    POST /api/users/login/
    Body: {
        "username": "john_doe",
        "password": "SecurePass123"
    }
    
    Returns: JWT access and refresh tokens + user data
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]  # Anyone can attempt to login
    
    def post(self, request, *args, **kwargs):
        """
        Authenticate user and return JWT tokens.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Generate JWT tokens for the user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    """
    API endpoint to list all users.
    Only accessible to authenticated users.
    
    GET /api/users/
    
    Returns: List of all users with pagination
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserStatusUpdateView(generics.UpdateAPIView):
    """
    API endpoint to update user status (activate/deactivate).
    Only accessible to authenticated users.
    
    PATCH /api/users/<id>/status/
    Body: {
        "is_active": false
    }
    
    Returns: Updated user data
    """
    queryset = User.objects.all()
    serializer_class = UserStatusUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        """
        Update user status with custom response.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'message': 'User status updated successfully',
            'user': UserSerializer(instance).data
        }, status=status.HTTP_200_OK)
