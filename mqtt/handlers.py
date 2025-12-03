"""
MQTT message handlers
Routes incoming MQTT messages to appropriate handlers
"""

import logging
import re

logger = logging.getLogger('mqtt')


def extract_device_id_from_topic(topic):
    """
    Extract device_id from MQTT topic
    Example: device/ESP32_001/status -> ESP32_001
    """
    match = re.search(r'device/([^/]+)/', topic)
    if match:
        return match.group(1)
    return None


def handle_mqtt_message(topic, payload):
    """
    Route MQTT message to appropriate handler based on topic
    """
    try:
        device_id = extract_device_id_from_topic(topic)
        
        if not device_id:
            logger.error(f"Could not extract device_id from topic: {topic}")
            return
        
        # Route based on topic suffix
        if topic.endswith('/status'):
            handle_status_message(device_id, payload)
        
        elif topic.endswith('/response'):
            handle_response_message(device_id, payload)
        
        elif topic.endswith('/alert'):
            handle_alert_message(device_id, payload)
        
        else:
            logger.warning(f"Unknown topic pattern: {topic}")
            
    except Exception as e:
        logger.error(f"Error handling MQTT message: {str(e)}")


def handle_status_message(device_id, payload):
    """
    Handle device status updates
    Topic: device/{device_id}/status
    """
    from apps.devices.mqtt_handlers import handle_device_status
    
    logger.info(f"Status update from {device_id}")
    handle_device_status(device_id, payload)


def handle_response_message(device_id, payload):
    """
    Handle device responses to commands
    Topic: device/{device_id}/response
    """
    from apps.devices.mqtt_handlers import (
        handle_unlock_response,
        handle_lock_response
    )
    
    response_type = payload.get('type', 'unknown')
    
    logger.info(f"Response from {device_id}: {response_type}")
    
    if response_type == 'unlock':
        handle_unlock_response(device_id, payload)
    
    elif response_type == 'lock':
        handle_lock_response(device_id, payload)
    
    else:
        logger.warning(f"Unknown response type: {response_type}")


def handle_alert_message(device_id, payload):
    """
    Handle device alerts (battery low, tamper, etc.)
    Topic: device/{device_id}/alert
    """
    from apps.devices.mqtt_handlers import (
        handle_battery_low,
        handle_tamper_detected
    )
    
    alert_type = payload.get('type', 'unknown')
    
    logger.warning(f"⚠️  Alert from {device_id}: {alert_type}")
    
    if alert_type == 'battery_low':
        handle_battery_low(device_id, payload)
    
    elif alert_type == 'tamper':
        handle_tamper_detected(device_id, payload)
    
    else:
        logger.warning(f"Unknown alert type: {alert_type}")