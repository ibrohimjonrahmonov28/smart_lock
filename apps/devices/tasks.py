"""
Device Celery tasks
"""

from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def send_unlock_command(device_id, user_id, duration=5, ip_address=None):
    """
    Send unlock command to device via MQTT
    """
    from .models import Device, DeviceLog
    from mqtt.client import mqtt_publish
    
    try:
        device = Device.objects.get(id=device_id)
        user = User.objects.get(id=user_id)
        
        # Prepare MQTT payload
        import json
        import time
        import secrets
        from apps.core.utils.encryption import generate_hmac_signature
        
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
    from .models import Device, DeviceLog
    from mqtt.client import mqtt_publish
    
    try:
        device = Device.objects.get(id=device_id)
        user = User.objects.get(id=user_id)
        
        import json
        import time
        import secrets
        from apps.core.utils.encryption import generate_hmac_signature
        
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
    from .models import Device, DeviceLog
    
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
def check_device_battery_status():
    """
    Check all devices for low battery (Periodic task)
    """
    from .models import Device
    
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