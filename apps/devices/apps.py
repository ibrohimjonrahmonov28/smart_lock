"""
Devices app configuration
"""

from django.apps import AppConfig


class DevicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.devices'
    verbose_name = 'Devices'

    def ready(self):
        """Import signals when app is ready"""
        import apps.devices.signals  # noqa