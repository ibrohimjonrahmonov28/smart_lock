"""
Access app configuration
"""

from django.apps import AppConfig


class AccessConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.access'
    verbose_name = 'Access Management'

    def ready(self):
        """Import signals when app is ready"""
        import apps.access.signals  # noqa