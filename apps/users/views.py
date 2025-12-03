"""
User views
"""

from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.contrib.auth import get_user_model
import logging

from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    ChangePasswordSerializer,
    UserUpdateSerializer,
)

User = get_user_model()
logger = logging.getLogger(__name__)


class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint
    
    Create a new user account with email and password
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=['Authentication'],
        responses={
            201: OpenApiResponse(description='User created successfully'),
            400: OpenApiResponse(description='Validation error'),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        logger.info(f"New user registered: {user.email}")

        return Response({
            'success': True,
            'message': 'User registered successfully',
            'data': {
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    """
    User login endpoint
    
    Authenticate user and return JWT tokens
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = UserLoginSerializer

    @extend_schema(
        tags=['Authentication'],
        request=UserLoginSerializer,
        responses={
            200: OpenApiResponse(description='Login successful'),
            401: OpenApiResponse(description='Invalid credentials'),
        }
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']

        # Update last login IP
        user.last_login_ip = request.META.get('REMOTE_ADDR')
        user.save(update_fields=['last_login_ip', 'updated_at'])

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        logger.info(f"User logged in: {user.email}")

        return Response({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }
        }, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update user profile
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Users'],
        responses={200: UserSerializer}
    )
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response({
            'success': True,
            'data': serializer.data
        })

    @extend_schema(
        tags=['Users'],
        request=UserUpdateSerializer,
        responses={200: UserSerializer}
    )
    def patch(self, request, *args, **kwargs):
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        logger.info(f"User profile updated: {request.user.email}")

        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'data': UserSerializer(request.user).data
        })


class ChangePasswordView(APIView):
    """
    Change user password
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Users'],
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(description='Password changed successfully'),
            400: OpenApiResponse(description='Validation error'),
        }
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        logger.info(f"Password changed: {request.user.email}")

        return Response({
            'success': True,
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    """
    User logout endpoint
    
    Blacklist the refresh token
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Authentication'],
        request={'refresh': 'string'},
        responses={
            200: OpenApiResponse(description='Logout successful'),
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            logger.info(f"User logged out: {request.user.email}")

            return Response({
                'success': True,
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)