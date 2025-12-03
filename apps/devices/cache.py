"""
Device caching utilities
"""

from django.core.cache import cache
from django.conf import settings
import json


class DeviceCache:
    """
    Device cache manager
    """
    CACHE_PREFIX = 'device'
    DEFAULT_TIMEOUT = 300  # 5 minutes

    @classmethod
    def get_status_key(cls, device_id):
        """Get cache key for device status"""
        return f"{cls.CACHE_PREFIX}:status:{device_id}"

    @classmethod
    def get_device_key(cls, device_id):
        """Get cache key for device data"""
        return f"{cls.CACHE_PREFIX}:data:{device_id}"

    @classmethod
    def cache_device_status(cls, device_id, status_data, timeout=None):
        """
        Cache device status
        """
        if timeout is None:
            timeout = cls.DEFAULT_TIMEOUT
        
        key = cls.get_status_key(device_id)
        cache.set(key, json.dumps(status_data), timeout)

    @classmethod
    def get_device_status(cls, device_id):
        """
        Get cached device status
        """
        key = cls.get_status_key(device_id)
        data = cache.get(key)
        
        if data:
            return json.loads(data)
        return None

    @classmethod
    def invalidate_device_cache(cls, device_id):
        """
        Invalidate device cache
        """
        status_key = cls.get_status_key(device_id)
        data_key = cls.get_device_key(device_id)
        
        cache.delete_many([status_key, data_key])

    @classmethod
    def cache_device_data(cls, device_id, device_data, timeout=3600):
        """
        Cache device data (1 hour default)
        """
        key = cls.get_device_key(device_id)
        cache.set(key, json.dumps(device_data), timeout)

    @classmethod
    def get_device_data(cls, device_id):
        """
        Get cached device data
        """
        key = cls.get_device_key(device_id)
        data = cache.get(key)
        
        if data:
            return json.loads(data)
        return None