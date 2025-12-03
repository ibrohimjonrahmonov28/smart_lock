"""
Security middleware
"""

from django.utils.deprecation import MiddlewareMixin
from .models import SecurityEvent, AuditLog
import logging

logger = logging.getLogger('apps.security')


class SecurityLoggingMiddleware(MiddlewareMixin):
    """
    Log security-relevant events
    """
    
    SENSITIVE_PATHS = [
        '/api/v1/auth/login/',
        '/api/v1/auth/register/',
        '/api/v1/devices/',
        '/admin/',
    ]

    def process_request(self, request):
        """Log request if it's security-relevant"""
        request._security_start = True

    def process_response(self, request, response):
        """Log response if security-relevant"""
        
        if not hasattr(request, '_security_start'):
            return response
        
        # Check if path is sensitive
        is_sensitive = any(
            request.path.startswith(path) 
            for path in self.SENSITIVE_PATHS
        )
        
        if not is_sensitive:
            return response
        
        # Log failed authentication attempts
        if request.path.startswith('/api/v1/auth/login/') and response.status_code == 401:
            try:
                SecurityEvent.objects.create(
                    event_type='LOGIN_FAILED',
                    severity='MEDIUM',
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    description=f'Failed login attempt from {self.get_client_ip(request)}'
                )
            except Exception as e:
                logger.error(f"Error logging security event: {str(e)}")
        
        return response

    @staticmethod
    def get_client_ip(request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip