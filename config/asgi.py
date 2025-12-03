"""
ASGI config for SmartLock Backend
For async/WebSocket support (future use)
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_asgi_application()

print("✅ ASGI application loaded")