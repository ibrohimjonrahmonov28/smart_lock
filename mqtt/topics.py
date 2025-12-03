"""
MQTT topic definitions
"""


class MQTTTopics:
    """
    MQTT topic structure for SmartLock system
    """
    
    # Command topics (Backend -> Device)
    DEVICE_COMMAND = "device/{device_id}/command"
    
    # Status topics (Device -> Backend)
    DEVICE_STATUS = "device/{device_id}/status"
    
    # Response topics (Device -> Backend)
    DEVICE_RESPONSE = "device/{device_id}/response"
    
    # Alert topics (Device -> Backend)
    DEVICE_ALERT = "device/{device_id}/alert"
    
    @classmethod
    def get_command_topic(cls, device_id):
        """Get command topic for device"""
        return cls.DEVICE_COMMAND.format(device_id=device_id)
    
    @classmethod
    def get_status_topic(cls, device_id):
        """Get status topic for device"""
        return cls.DEVICE_STATUS.format(device_id=device_id)
    
    @classmethod
    def get_response_topic(cls, device_id):
        """Get response topic for device"""
        return cls.DEVICE_RESPONSE.format(device_id=device_id)
    
    @classmethod
    def get_alert_topic(cls, device_id):
        """Get alert topic for device"""
        return cls.DEVICE_ALERT.format(device_id=device_id)
    
    @classmethod
    def get_all_device_topics(cls):
        """Get all device subscription topics (with wildcards)"""
        return [
            "device/+/status",
            "device/+/response",
            "device/+/alert",
        ]