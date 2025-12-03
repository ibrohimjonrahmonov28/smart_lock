"""
Django management command to run MQTT bridge
This keeps MQTT connection alive and processes messages
"""

from django.core.management.base import BaseCommand
import signal
import sys
import time
import logging

logger = logging.getLogger('mqtt')


class Command(BaseCommand):
    help = 'Run MQTT bridge to handle device communication'

    def __init__(self):
        super().__init__()
        self.should_stop = False

    def handle(self, *args, **options):
        """
        Start MQTT bridge
        """
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        self.stdout.write(self.style.SUCCESS('🚀 Starting MQTT bridge...'))

        from mqtt.client import start_mqtt_client, stop_mqtt_client

        # Connect to MQTT broker
        if start_mqtt_client():
            self.stdout.write(self.style.SUCCESS('✅ MQTT bridge started successfully'))
            
            # Keep the process alive
            try:
                while not self.should_stop:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            finally:
                self.stdout.write(self.style.WARNING('🛑 Stopping MQTT bridge...'))
                stop_mqtt_client()
                self.stdout.write(self.style.SUCCESS('✅ MQTT bridge stopped'))
        else:
            self.stdout.write(self.style.ERROR('❌ Failed to start MQTT bridge'))
            sys.exit(1)

    def signal_handler(self, sig, frame):
        """
        Handle shutdown signals
        """
        self.stdout.write(self.style.WARNING(f'\n⚠️  Received signal {sig}. Shutting down...'))
        self.should_stop = True