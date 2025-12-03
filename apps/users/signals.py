"""
User signals
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    Post-save signal for User model
    """
    if created:
        logger.info(f"New user created: {instance.email} (ID: {instance.id})")
        
        # TODO: Send welcome email
        # TODO: Create default settingss