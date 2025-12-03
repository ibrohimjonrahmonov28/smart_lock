"""
SmartLock Backend URL Configuration
Production-ready API routing
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for monitoring
    """
    return Response({
        'status': 'healthy',
        'service': 'SmartLock Backend',
        'version': '1.0.0',
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    API Root - Welcome message
    """
    return Response({
        'message': 'Welcome to SmartLock Backend API',
        'version': '1.0.0',
        'docs': request.build_absolute_uri('/api/docs/'),
        'endpoints': {
            'auth': request.build_absolute_uri('/api/v1/auth/'),
            'devices': request.build_absolute_uri('/api/v1/devices/'),
            'access': request.build_absolute_uri('/api/v1/access/'),
            'security': request.build_absolute_uri('/api/v1/security/'),
        }
    })


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Health check
    path('health/', health_check, name='health-check'),
    
    # API Root
    path('api/', api_root, name='api-root'),
    
    # API v1
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/devices/', include('apps.devices.urls')),
    path('api/v1/access/', include('apps.access.urls')),
    path('api/v1/security/', include('apps.security.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom admin site config
admin.site.site_header = 'SmartLock Backend Admin'
admin.site.site_title = 'SmartLock Admin'
admin.site.index_title = 'Welcome to SmartLock Backend Administration'