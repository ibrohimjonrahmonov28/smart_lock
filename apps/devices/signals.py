"""
Device signals
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Device, DeviceLog
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Device)
def device_post_save(sender, instance, created, **kwargs):
    """
    Post-save signal for Device
    """
    if created:
        logger.info(f"New device created: {instance.device_id} by {instance.owner.email}")


@receiver(pre_save, sender=Device)
def device_pre_save(sender, instance, **kwargs):
    """
    Pre-save signal for Device
    """
    if instance.pk:
        try:
            old_instance = Device.objects.get(pk=instance.pk)
            
            # Detect lock state change
            if old_instance.is_locked != instance.is_locked:
                event_type = 'LOCK' if instance.is_locked else 'UNLOCK'
                logger.info(f"Device {instance.device_id} {event_type}")
            
            # Detect online/offline change
            if old_instance.is_online != instance.is_online:
                status = 'ONLINE' if instance.is_online else 'OFFLINE'
                logger.info(f"Device {instance.device_id} {status}")
                
        except Device.DoesNotExist:
            pass