"""
Development Settings
"""

from .base import *

# Debug mode ON
DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# CORS - Allow all origins
CORS_ALLOW_ALL_ORIGINS = True

# Email - Console backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable SSL
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Celery - Eager mode (optional)
# CELERY_TASK_ALWAYS_EAGER = True
# CELERY_TASK_EAGER_PROPAGATES = True

# Verbose logging
LOGGING['loggers']['apps']['level'] = 'DEBUG'
LOGGING['loggers']['mqtt']['level'] = 'DEBUG'

print("⚙️  Development settings loaded")
print(f"📂 BASE_DIR: {BASE_DIR}")
print(f"💾 Database: PostgreSQL ({DATABASES['default']['NAME']}@{DATABASES['default']['HOST']})")