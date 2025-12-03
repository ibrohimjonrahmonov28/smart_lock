"""
Device models
"""

from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import TimeStampedModel, UUIDModel
from apps.core.utils.validators import validate_device_id
import secrets

User = get_user_model()


class Device(TimeStampedModel, UUIDModel):
    """
    Smart Lock Device
    """
    DEVICE_TYPE_CHOICES = [
        ('LITE', 'SmartLock LITE'),
        ('PRO', 'SmartLock PRO'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('MAINTENANCE', 'Maintenance'),
    ]

    # Owner
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='devices'
    )

    # Device Info
    device_id = models.CharField(
        max_length=32,
        unique=True,
        db_index=True,
        validators=[validate_device_id]
    )
    name = models.CharField(max_length=100)
    device_type = models.CharField(
        max_length=10,
        choices=DEVICE_TYPE_CHOICES,
        default='LITE'
    )
    
    # Security
    device_secret = models.CharField(max_length=64, unique=True)
    
    # Location
    location = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    is_locked = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False)
    
    # Battery
    battery_level = models.IntegerField(default=100)
    battery_low_threshold = models.IntegerField(default=20)
    
    # Features (based on device type)
    keypad_enabled = models.BooleanField(default=False)
    nfc_enabled = models.BooleanField(default=True)
    
    # Timestamps
    last_seen = models.DateTimeField(null=True, blank=True)
    last_unlock = models.DateTimeField(null=True, blank=True)
    last_lock = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'devices'
        verbose_name = 'Device'
        verbose_name_plural = 'Devices'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['device_id']),
        ]

    def __str__(self):
        return f"{self.name} ({self.device_id})"

    def save(self, *args, **kwargs):
        """Generate device secret on creation"""
        if not self.device_secret:
            self.device_secret = secrets.token_hex(32)
        
        # Set features based on device type
        if self.device_type == 'PRO':
            self.keypad_enabled = True
            self.nfc_enabled = True
        
        super().save(*args, **kwargs)

    @property
    def is_battery_low(self):
        """Check if battery is low"""
        return self.battery_level <= self.battery_low_threshold


class DeviceLog(TimeStampedModel, UUIDModel):
    """
    Device activity logs
    """
    EVENT_TYPE_CHOICES = [
        ('UNLOCK', 'Unlock'),
        ('LOCK', 'Lock'),
        ('UNLOCK_APP', 'Unlock via App'),
        ('UNLOCK_NFC', 'Unlock via NFC'),
        ('UNLOCK_PIN', 'Unlock via PIN'),
        ('UNLOCK_PHYSICAL', 'Unlock via Physical Key'),
        ('BATTERY_LOW', 'Battery Low'),
        ('DEVICE_ONLINE', 'Device Online'),
        ('DEVICE_OFFLINE', 'Device Offline'),
        ('TAMPER_DETECTED', 'Tamper Detected'),
    ]

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='device_logs'
    )
    
    event_type = models.CharField(max_length=30, choices=EVENT_TYPE_CHOICES)
    description = models.TextField(blank=True)
    
    # Request info
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Result
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = 'device_logs'
        verbose_name = 'Device Log'
        verbose_name_plural = 'Device Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['device', '-created_at']),
            models.Index(fields=['event_type', '-created_at']),
        ]

    def __str__(self):
        return f"{self.device.name} - {self.event_type} - {self.created_at}"


class DeviceSharing(TimeStampedModel, UUIDModel):
    """
    Device sharing with other users
    """
    ROLE_CHOICES = [
        ('OWNER', 'Owner'),
        ('ADMIN', 'Admin'),
        ('MEMBER', 'Member'),
        ('VIEWER', 'Viewer'),
    ]

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='shared_with'
    )
    shared_with = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shared_devices'
    )
    shared_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='devices_shared_by_me'
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='MEMBER')
    
    # Permissions
    can_unlock = models.BooleanField(default=True)
    can_lock = models.BooleanField(default=True)
    can_view_logs = models.BooleanField(default=True)
    can_manage_access = models.BooleanField(default=False)
    can_share = models.BooleanField(default=False)
    
    # Expiry
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'device_sharing'
        verbose_name = 'Device Sharing'
        verbose_name_plural = 'Device Sharings'
        unique_together = ['device', 'shared_with']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.device.name} shared with {self.shared_with.email}"