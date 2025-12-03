"""
Encryption utilities
"""

import hashlib
import hmac
from django.conf import settings


def hash_pin_code(pin_code):
    """
    Hash PIN code using SHA256
    """
    return hashlib.sha256(str(pin_code).encode()).hexdigest()


def verify_pin_code(pin_code, hashed_pin):
    """
    Verify PIN code against hash
    """
    return hash_pin_code(pin_code) == hashed_pin


def generate_hmac_signature(device_id, timestamp, secret_key=None):
    """
    Generate HMAC signature for device authentication
    """
    if secret_key is None:
        secret_key = settings.SECRET_KEY
    
    message = f"{device_id}:{timestamp}"
    signature = hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return signature


def verify_hmac_signature(device_id, timestamp, signature, secret_key=None):
    """
    Verify HMAC signature
    """
    expected = generate_hmac_signature(device_id, timestamp, secret_key)
    return hmac.compare_digest(signature, expected)