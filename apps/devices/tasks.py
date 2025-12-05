"""
Device Celery tasks
"""

import json
import logging
import secrets
import time

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Device, DeviceLog
from apps.core.utils.encryption import generate_hmac_signature
from mqtt.client import mqtt_publish

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def send_unlock_command(device_id, user_id, duration=5, ip_address=None):
    """
    Send unlock command to device via MQTT
    """
    try:
        device = Device.objects.get(id=device_id)
        user = User.objects.get(id=user_id)

        # Prepare MQTT payload
        timestamp = int(time.time())
        nonce = secrets.token_hex(16)
        
        payload = {
            'command': 'unlock',
            'duration': duration,
            'nonce': nonce,
            'timestamp': timestamp,
            'signature': generate_hmac_signature(
                device.device_id,
                str(timestamp),
                device.device_secret
            )
        }
        
        # Publish to MQTT
        topic = f"device/{device.device_id}/command"
        mqtt_publish(topic, json.dumps(payload))
        
        # Log event
        DeviceLog.objects.create(
            device=device,
            user=user,
            event_type='UNLOCK_APP',
            description=f'Unlock command sent via app (duration: {duration}s)',
            ip_address=ip_address,
            success=True
        )
        
        logger.info(f"Unlock command sent to {device.device_id}")
        return {'success': True, 'device_id': device.device_id}
        
    except Exception as e:
        logger.error(f"Error sending unlock command: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def send_lock_command(device_id, user_id, ip_address=None):
    """
    Send lock command to device via MQTT
    """
    try:
        device = Device.objects.get(id=device_id)
        user = User.objects.get(id=user_id)

        timestamp = int(time.time())
        nonce = secrets.token_hex(16)
        
        payload = {
            'command': 'lock',
            'nonce': nonce,
            'timestamp': timestamp,
            'signature': generate_hmac_signature(
                device.device_id,
                str(timestamp),
                device.device_secret
            )
        }
        
        topic = f"device/{device.device_id}/command"
        mqtt_publish(topic, json.dumps(payload))
        
        DeviceLog.objects.create(
            device=device,
            user=user,
            event_type='LOCK',
            description='Lock command sent via app',
            ip_address=ip_address,
            success=True
        )
        
        logger.info(f"Lock command sent to {device.device_id}")
        return {'success': True}
        
    except Exception as e:
        logger.error(f"Error sending lock command: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def log_device_event(device_id, event_type, description='', user_id=None, success=True):
    """
    Log device event
    """
    try:
        device = Device.objects.get(id=device_id)
        user = User.objects.get(id=user_id) if user_id else None
        
        DeviceLog.objects.create(
            device=device,
            user=user,
            event_type=event_type,
            description=description,
            success=success
        )
        
        return {'success': True}
    except Exception as e:
        logger.error(f"Error logging device event: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def auto_unlock_if_no_response(device_id, duration=5):
    """
    Auto-unlock device if no MQTT response received (for testing/fallback)
    Runs 3 seconds after unlock command sent
    """
    try:
        device = Device.objects.get(id=device_id)

        # If device is still locked after 3 seconds, unlock it
        if device.is_locked:
            device.is_locked = False
            device.last_unlock = timezone.now()
            device.save(update_fields=['is_locked', 'last_unlock', 'updated_at'])

            logger.info(f"Auto-unlocked device (no MQTT response): {device.device_id}")
            return {'success': True, 'auto_unlocked': True}
        else:
            logger.info(f"Device already unlocked via MQTT: {device.device_id}")
            return {'success': True, 'auto_unlocked': False}

    except Device.DoesNotExist:
        logger.error(f"Device not found: {device_id}")
        return {'success': False, 'error': 'Device not found'}
    except Exception as e:
        logger.error(f"Error auto-unlocking device: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def auto_lock_if_no_response(device_id):
    """
    Auto-lock device if no MQTT response received (for testing/fallback)
    Runs 3 seconds after lock command sent
    """
    try:
        device = Device.objects.get(id=device_id)

        # If device is still unlocked after 3 seconds, lock it
        if not device.is_locked:
            device.is_locked = True
            device.last_lock = timezone.now()
            device.save(update_fields=['is_locked', 'last_lock', 'updated_at'])

            logger.info(f"Auto-locked device (no MQTT response): {device.device_id}")
            return {'success': True, 'auto_locked': True}
        else:
            logger.info(f"Device already locked via MQTT: {device.device_id}")
            return {'success': True, 'auto_locked': False}

    except Device.DoesNotExist:
        logger.error(f"Device not found: {device_id}")
        return {'success': False, 'error': 'Device not found'}
    except Exception as e:
        logger.error(f"Error auto-locking device: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def check_device_battery_status():
    """
    Check all devices for low battery (Periodic task)
    """
    try:
        low_battery_devices = Device.objects.filter(
            status='ACTIVE',
            battery_level__lte=20
        )

        for device in low_battery_devices:
            # Send notification
            logger.warning(f"Low battery detected: {device.device_id} ({device.battery_level}%)")

            # TODO: Send email/telegram notification to owner

        return {'success': True, 'count': low_battery_devices.count()}
    except Exception as e:
        logger.error(f"Error checking battery status: {str(e)}")
        return {'success': False, 'error': str(e)}