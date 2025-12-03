"""
Celery configuration for SmartLock Backend
Production-ready async task processing
"""

import os
from celery import Celery
from celery.signals import setup_logging

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Create Celery app
app = Celery('smartlock')

# Load config from Django settings (namespace='CELERY')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()


@setup_logging.connect
def config_loggers(*args, **kwargs):
    """Configure Celery logging to use Django logging"""
    from logging.config import dictConfig
    from django.conf import settings
    dictConfig(settings.LOGGING)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery"""
    print(f'Request: {self.request!r}')


# Celery Beat Schedule (Periodic Tasks)
app.conf.beat_schedule = {
    # Clean expired guest codes every hour
    'clean-expired-guest-codes': {
        'task': 'apps.access.tasks.clean_expired_guest_codes',
        'schedule': 3600.0,  # Every hour
    },
    # Check device battery status every 6 hours
    'check-device-battery': {
        'task': 'apps.devices.tasks.check_device_battery_status',
        'schedule': 21600.0,  # Every 6 hours
    },
    # Generate daily security report
    'daily-security-report': {
        'task': 'apps.security.tasks.generate_daily_report',
        'schedule': {
            'hour': 23,
            'minute': 59,
        },
    },
}

print("✅ Celery configured successfully")