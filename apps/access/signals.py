"""
Access signals
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import NFCCard, PINCode
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=NFCCard)
def nfc_card_post_save(sender, instance, created, **kwargs):
    """
    Post-save signal for NFC Card
    """
    if created:
        logger.info(f"NFC card created: {instance.uid} for device {instance.device.device_id}")


@receiver(post_save, sender=PINCode)
def pin_code_post_save(sender, instance, created, **kwargs):
    """
    Post-save signal for PIN Code
    """
    if created:
        logger.info(f"PIN code created for device {instance.device.device_id}")