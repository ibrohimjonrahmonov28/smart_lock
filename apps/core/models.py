"""
Abstract base models for all apps
"""

from django.db import models
import uuid


class TimeStampedModel(models.Model):
    """
    Abstract base class with created_at and updated_at fields
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class UUIDModel(models.Model):
    """
    Abstract base class with UUID primary key
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True