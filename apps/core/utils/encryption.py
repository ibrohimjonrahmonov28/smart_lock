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


def generate_device_hmac(device_id, timestamp, nfc_uid_or_pin, device_secret):
    """
    Generate HMAC signature for device communication
    Combines device_id, timestamp, and access code (NFC UID or PIN)

    Args:
        device_id: Device UUID
        timestamp: Unix timestamp (int or str)
        nfc_uid_or_pin: NFC UID or PIN code
        device_secret: Device secret key

    Returns:
        HMAC signature (hex string)
    """
    message = f"{device_id}:{timestamp}:{nfc_uid_or_pin}"
    signature = hmac.new(
        device_secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

    return signature


def verify_device_hmac(device_id, timestamp, nfc_uid_or_pin, signature, device_secret):
    """
    Verify HMAC signature for device communication

    Args:
        device_id: Device UUID
        timestamp: Unix timestamp (int or str)
        nfc_uid_or_pin: NFC UID or PIN code
        signature: HMAC signature to verify
        device_secret: Device secret key

    Returns:
        bool: True if signature is valid
    """
    expected = generate_device_hmac(device_id, timestamp, nfc_uid_or_pin, device_secret)
    return hmac.compare_digest(signature, expected)