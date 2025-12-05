"""
Access utilities - PIN generation
"""

import secrets
import string


def generate_random_pin(length=6):
    """
    Random PIN kod yaratish (cryptographic secure)

    Args:
        length: PIN uzunligi (default: 6)

    Returns:
        str: Random PIN kod (masalan: "847293")

    Example:
        >>> pin = generate_random_pin()
        >>> print(pin)
        "738492"

        >>> pin = generate_random_pin(4)
        >>> print(pin)
        "9284"
    """
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def generate_memorable_pin(length=6):
    """
    Esda qoladigan PIN yaratish (juft raqamlar)

    Args:
        length: PIN uzunligi

    Returns:
        str: PIN kod

    Example:
        >>> pin = generate_memorable_pin()
        >>> print(pin)
        "224466"
    """
    digits = string.digits
    pin = ''
    for _ in range(length // 2):
        digit = secrets.choice(digits)
        pin += digit * 2  # Har bir raqamni 2 marta takrorlash
    return pin
