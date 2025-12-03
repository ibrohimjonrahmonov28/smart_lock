"""
Settings package initialization
Automatically loads appropriate settings based on DJANGO_ENV
"""

import os

DJANGO_ENV = os.environ.get('DJANGO_ENV', 'development')

if DJANGO_ENV == 'production':
    from .production import *
else:
    from .development import *

print(f"🚀 Django running in: {DJANGO_ENV.upper()} mode")