"""
Production Settings for Docker Deployment
"""

from .base import *

# Debug OFF
DEBUG = env.bool('DEBUG', default=False)

# Allowed Hosts
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])

# ==============================================================================
# SENTRY (Error Tracking)
# ==============================================================================

SENTRY_DSN = env('SENTRY_DSN', default='')

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment='production',
    )

# ==============================================================================
# SECURITY SETTINGS
# ==============================================================================

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# HTTPS Proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ==============================================================================
# DATABASE (Production with PostgreSQL)
# ==============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT', default='5432'),
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# ==============================================================================
# CACHE (Longer timeout)
# ==============================================================================

CACHES['default']['TIMEOUT'] = 3600  # 1 hour

# ==============================================================================
# EMAIL (Production SMTP)
# ==============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# ==============================================================================
# LOGGING (Less verbose)
# ==============================================================================

LOGGING['handlers']['console']['level'] = 'WARNING'
LOGGING['loggers']['django']['level'] = 'WARNING'
LOGGING['loggers']['apps']['level'] = 'INFO'

print("🚀 Production settings loaded")