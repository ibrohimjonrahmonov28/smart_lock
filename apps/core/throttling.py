"""
Custom throttling classes
"""

from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class UnlockRateThrottle(UserRateThrottle):
    """
    Throttle for unlock/lock operations
    20 requests per hour per user
    """
    rate = '20/hour'
    scope = 'unlock'


class VerifyRateThrottle(UserRateThrottle):
    """
    Throttle for verification operations
    100 requests per hour per user
    """
    rate = '100/hour'
    scope = 'verify'


class AuthRateThrottle(AnonRateThrottle):
    """
    Throttle for authentication endpoints
    5 requests per minute
    """
    rate = '5/minute'
    scope = 'auth'