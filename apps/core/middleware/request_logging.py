"""
Request logging middleware
"""

import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('apps')


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Log all requests with timing
    """
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            logger.info(
                f"{request.method} {request.path} "
                f"[{response.status_code}] "
                f"{duration:.2f}s"
            )
        
        return response