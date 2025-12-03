"""
Custom validators
"""

from django.core.exceptions import ValidationError
import re


def validate_pin_code(value):
    """
    Validate PIN code (4-8 digits)
    """
    if not re.match(r'^\d{4,8}$', str(value)):
        raise ValidationError('PIN code must be 4-8 digits')


def validate_nfc_uid(value):
    """
    Validate NFC UID format
    """
    if not re.match(r'^[0-9A-Fa-f:]{8,23}$', value):
        raise ValidationError('Invalid NFC UID format')


def validate_device_id(value):
    """
    Validate device ID format
    """
    if not re.match(r'^[A-Z0-9_]{6,32}$', value):
        raise ValidationError('Device ID must be 6-32 uppercase alphanumeric characters')