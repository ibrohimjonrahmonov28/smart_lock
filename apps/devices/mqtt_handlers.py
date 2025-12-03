"""
MQTT message handlers for devices
"""

import json
import logging
from django.utils import timezone
from .models import Device, DeviceLog

logger = logging.getLogger('mqtt')


def handle_device_status(device_id, payload):
    """
    Handle device status updates
    
    Expected payload:
    {
        "status": "online/offline",
        "is_locked": true/false,
        "battery_level": 85,
        "timestamp": 1234567890
    }
    """
    try:
        device = Device.objects.get(device_id=device_id)
        
        # Update device status
        device.is_online = payload.get('status') == 'online'
        device.is_locked = payload.get('is_locked', device.is_locked)
        device.battery_level = payload.get('battery_level', device.battery_level)
        device.last_seen = timezone.now()
        
        device.save(update_fields=[
            'is_online',
            'is_locked',
            'battery_level',
            'last_seen',
            'updated_at'
        ])
        
        # Log status change
        if device.is_online:
            DeviceLog.objects.create(
                device=device,
                event_type='DEVICE_ONLINE',
                description='Device came online',
                success=True
            )
        
        logger.info(f"Device status updated: {device_id}")
        
    except Device.DoesNotExist:
        logger.error(f"Device not found: {device_id}")
    except Exception as e:
        logger.error(f"Error handling device status: {str(e)}")


def handle_unlock_response(device_id, payload):
    """
    Handle unlock response from device
    
    Expected payload:
    {
        "success": true,
        "method": "app/nfc/pin/physical",
        "timestamp": 1234567890
    }
    """
    try:
        device = Device.objects.get(device_id=device_id)
        
        success = payload.get('success', False)
        method = payload.get('method', 'unknown')
        
        if success:
            device.is_locked = False
            device.last_unlock = timezone.now()
            device.save(update_fields=['is_locked', 'last_unlock', 'updated_at'])
            
            # Map method to event type
            event_type_map = {
                'app': 'UNLOCK_APP',
                'nfc': 'UNLOCK_NFC',
                'pin': 'UNLOCK_PIN',
                'physical': 'UNLOCK_PHYSICAL',
            }
            
            event_type = event_type_map.get(method, 'UNLOCK')
            
            DeviceLog.objects.create(
                device=device,
                event_type=event_type,
                description=f'Device unlocked via {method}',
                success=True
            )
            
            logger.info(f"Device unlocked: {device_id} via {method}")
        else:
            error_msg = payload.get('error', 'Unknown error')
            logger.error(f"Unlock failed: {device_id} - {error_msg}")
            
    except Device.DoesNotExist:
        logger.error(f"Device not found: {device_id}")
    except Exception as e:
        logger.error(f"Error handling unlock response: {str(e)}")


def handle_lock_response(device_id, payload):
    """
    Handle lock response from device
    """
    try:
        device = Device.objects.get(device_id=device_id)
        
        success = payload.get('success', False)
        
        if success:
            device.is_locked = True
            device.last_lock = timezone.now()
            device.save(update_fields=['is_locked', 'last_lock', 'updated_at'])
            
            DeviceLog.objects.create(
                device=device,
                event_type='LOCK',
                description='Device locked',
                success=True
            )
            
            logger.info(f"Device locked: {device_id}")
            
    except Device.DoesNotExist:
        logger.error(f"Device not found: {device_id}")
    except Exception as e:
        logger.error(f"Error handling lock response: {str(e)}")


def handle_battery_low(device_id, payload):
    """
    Handle low battery alert
    """
    try:
        device = Device.objects.get(device_id=device_id)
        
        battery_level = payload.get('battery_level', 0)
        
        device.battery_level = battery_level
        device.save(update_fields=['battery_level', 'updated_at'])
        
        DeviceLog.objects.create(
            device=device,
            event_type='BATTERY_LOW',
            description=f'Low battery alert: {battery_level}%',
            success=True
        )
        
        logger.warning(f"Low battery: {device_id} - {battery_level}%")
        
        # TODO: Send notification to owner
        
    except Device.DoesNotExist:
        logger.error(f"Device not found: {device_id}")
    except Exception as e:
        logger.error(f"Error handling battery low: {str(e)}")


def handle_tamper_detected(device_id, payload):
    """
    Handle tamper detection
    """
    try:
        device = Device.objects.get(device_id=device_id)
        
        DeviceLog.objects.create(
            device=device,
            event_type='TAMPER_DETECTED',
            description='Tamper detected on device!',
            success=True
        )
        
        logger.critical(f"TAMPER DETECTED: {device_id}")
        
        # TODO: Send urgent notification to owner
        
    except Device.DoesNotExist:
        logger.error(f"Device not found: {device_id}")
    except Exception as e:
        logger.error(f"Error handling tamper detection: {str(e)}")


# Message router
MESSAGE_HANDLERS = {
    'status': handle_device_status,
    'unlock_response': handle_unlock_response,
    'lock_response': handle_lock_response,
    'battery_low': handle_battery_low,
    'tamper_detected': handle_tamper_detected,
}


def route_message(device_id, message_type, payload):
    """
    Route MQTT message to appropriate handler
    """
    handler = MESSAGE_HANDLERS.get(message_type)
    
    if handler:
        handler(device_id, payload)
    else:
        logger.warning(f"Unknown message type: {message_type}")