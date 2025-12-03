"""
Custom exception handlers
"""

from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Log the error
        logger.error(
            f"Exception: {exc.__class__.__name__} | "
            f"Detail: {str(exc)} | "
            f"Context: {context.get('view', 'Unknown')}"
        )

        # Customize error response format
        custom_response = {
            'success': False,
            'error': {
                'message': str(exc),
                'code': response.status_code,
            }
        }

        # Add field errors for validation errors
        if isinstance(exc, ValidationError):
            custom_response['error']['fields'] = response.data

        response.data = custom_response

    return response