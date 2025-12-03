"""
MQTT Client for SmartLock Backend
Handles real-time communication with devices
"""

import paho.mqtt.client as mqtt
import json
import logging
from django.conf import settings
from threading import Thread
import time

logger = logging.getLogger('mqtt')


class MQTTClient:
    """
    MQTT Client singleton
    """
    _instance = None
    _client = None
    _connected = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MQTTClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._setup_client()

    def _setup_client(self):
        """
        Setup MQTT client with callbacks
        """
        self._client = mqtt.Client(
            client_id=settings.MQTT_CLIENT_ID,
            clean_session=True,
            protocol=mqtt.MQTTv311
        )

        # Set callbacks
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message
        self._client.on_subscribe = self._on_subscribe
        self._client.on_publish = self._on_publish

        # Set credentials if provided
        if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
            self._client.username_pw_set(
                settings.MQTT_USERNAME,
                settings.MQTT_PASSWORD
            )

        logger.info("MQTT client initialized")

    def _on_connect(self, client, userdata, flags, rc):
        """
        Callback when connected to MQTT broker
        """
        if rc == 0:
            self._connected = True
            logger.info("✅ Connected to MQTT broker")
            
            # Subscribe to all device topics
            from .topics import MQTTTopics
            topics = MQTTTopics.get_all_device_topics()
            
            for topic in topics:
                self._client.subscribe(topic, qos=1)
                logger.info(f"📡 Subscribed to: {topic}")
        else:
            self._connected = False
            error_messages = {
                1: "Connection refused - incorrect protocol version",
                2: "Connection refused - invalid client identifier",
                3: "Connection refused - server unavailable",
                4: "Connection refused - bad username or password",
                5: "Connection refused - not authorized"
            }
            logger.error(f"❌ MQTT connection failed: {error_messages.get(rc, f'Unknown error {rc}')}")

    def _on_disconnect(self, client, userdata, rc):
        """
        Callback when disconnected from MQTT broker
        """
        self._connected = False
        if rc != 0:
            logger.warning(f"⚠️  Unexpected MQTT disconnect (code: {rc}). Reconnecting...")
        else:
            logger.info("MQTT disconnected")

    def _on_message(self, client, userdata, msg):
        """
        Callback when message received
        """
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode('utf-8'))
            
            logger.info(f"📨 Message received on {topic}")
            
            # Route message to handler
            from .handlers import handle_mqtt_message
            handle_mqtt_message(topic, payload)
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON payload: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing MQTT message: {str(e)}")

    def _on_subscribe(self, client, userdata, mid, granted_qos):
        """
        Callback when subscribed to topic
        """
        logger.debug(f"Subscribed (mid: {mid}, QoS: {granted_qos})")

    def _on_publish(self, client, userdata, mid):
        """
        Callback when message published
        """
        logger.debug(f"Message published (mid: {mid})")

    def connect(self):
        """
        Connect to MQTT broker
        """
        try:
            logger.info(f"Connecting to MQTT broker: {settings.MQTT_BROKER}:{settings.MQTT_PORT}")
            
            self._client.connect(
                settings.MQTT_BROKER,
                settings.MQTT_PORT,
                settings.MQTT_KEEPALIVE
            )
            
            # Start network loop in background thread
            self._client.loop_start()
            
            # Wait for connection
            timeout = 10
            start_time = time.time()
            while not self._connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if self._connected:
                logger.info("✅ MQTT client connected and ready")
                return True
            else:
                logger.error("❌ Failed to connect to MQTT broker within timeout")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error connecting to MQTT broker: {str(e)}")
            return False

    def disconnect(self):
        """
        Disconnect from MQTT broker
        """
        if self._client:
            self._client.loop_stop()
            self._client.disconnect()
            logger.info("MQTT client disconnected")

    def publish(self, topic, payload, qos=1, retain=False):
        """
        Publish message to MQTT topic
        """
        if not self._connected:
            logger.error("Cannot publish - MQTT not connected")
            return False

        try:
            if isinstance(payload, dict):
                payload = json.dumps(payload)
            
            result = self._client.publish(topic, payload, qos=qos, retain=retain)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"📤 Published to {topic}")
                return True
            else:
                logger.error(f"Failed to publish to {topic}: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing to MQTT: {str(e)}")
            return False

    @property
    def is_connected(self):
        """Check if connected to MQTT broker"""
        return self._connected


# Global MQTT client instance
_mqtt_client_instance = None


def get_mqtt_client():
    """
    Get global MQTT client instance
    """
    global _mqtt_client_instance
    if _mqtt_client_instance is None:
        _mqtt_client_instance = MQTTClient()
    return _mqtt_client_instance


def mqtt_publish(topic, payload, qos=1, retain=False):
    """
    Helper function to publish MQTT message
    """
    client = get_mqtt_client()
    return client.publish(topic, payload, qos, retain)


def start_mqtt_client():
    """
    Start MQTT client connection
    """
    client = get_mqtt_client()
    return client.connect()


def stop_mqtt_client():
    """
    Stop MQTT client connection
    """
    client = get_mqtt_client()
    client.disconnect()