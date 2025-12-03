"""
Access models - NFC cards and PIN codes
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.core.models import TimeStampedModel, UUIDModel
from apps.core.utils.validators import validate_pin_code, validate_nfc_uid
from apps.core.utils.encryption import hash_pin_code

User = get_user_model()


class NFCCard(TimeStampedModel, UUIDModel):
    """
    NFC Card for device access
    """
    device = models.ForeignKey(
        'devices.Device',
        on_delete=models.CASCADE,
        related_name='nfc_cards'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='nfc_cards',
        null=True,
        blank=True
    )
    
    # NFC Info
    uid = models.CharField(
        max_length=23,
        unique=True,
        validators=[validate_nfc_uid],
        help_text='NFC UID (e.g., 04:A3:2F:B2)'
    )
    name = models.CharField(max_length=100, help_text='Card name/label')
    
    # Validity
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)
    
    # Usage limits
    usage_count = models.IntegerField(default=0)
    max_usage = models.IntegerField(
        null=True,
        blank=True,
        help_text='Maximum usage count (null = unlimited)'
    )
    
    # Time restrictions
    allowed_days = models.JSONField(
        default=list,
        blank=True,
        help_text='Allowed days: ["mon","tue","wed","thu","fri","sat","sun"]'
    )
    allowed_hours = models.JSONField(
        default=dict,
        blank=True,
        help_text='Allowed hours: {"start":"08:00","end":"18:00"}'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Created by
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='nfc_cards_created'
    )

    class Meta:
        db_table = 'nfc_cards'
        verbose_name = 'NFC Card'
        verbose_name_plural = 'NFC Cards'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['device', 'is_active']),
            models.Index(fields=['uid']),
        ]

    def __str__(self):
        return f"{self.name} ({self.uid})"

    @property
    def is_valid(self):
        """Check if card is currently valid"""
        now = timezone.now()
        
        # Check active status
        if not self.is_active:
            return False
        
        # Check time validity
        if self.valid_from and now < self.valid_from:
            return False
        
        if self.valid_until and now > self.valid_until:
            return False
        
        # Check usage limit
        if self.max_usage and self.usage_count >= self.max_usage:
            return False
        
        return True

    def increment_usage(self):
        """Increment usage count"""
        self.usage_count += 1
        self.save(update_fields=['usage_count', 'updated_at'])


class PINCode(TimeStampedModel, UUIDModel):
    """
    PIN Code for device access
    """
    device = models.ForeignKey(
        'devices.Device',
        on_delete=models.CASCADE,
        related_name='pin_codes'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pin_codes',
        null=True,
        blank=True
    )
    
    # PIN Info
    pin_hash = models.CharField(max_length=64)
    name = models.CharField(max_length=100, help_text='PIN name/label')
    
    # Validity
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)
    
    # Usage limits
    usage_count = models.IntegerField(default=0)
    max_usage = models.IntegerField(
        null=True,
        blank=True,
        help_text='Maximum usage count (null = unlimited)'
    )
    
    # Time restrictions
    allowed_days = models.JSONField(default=list, blank=True)
    allowed_hours = models.JSONField(default=dict, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Created by
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='pin_codes_created'
    )

    class Meta:
        db_table = 'pin_codes'
        verbose_name = 'PIN Code'
        verbose_name_plural = 'PIN Codes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['device', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} (PIN)"

    def set_pin(self, pin_code):
        """Set PIN code (hashed)"""
        validate_pin_code(pin_code)
        self.pin_hash = hash_pin_code(pin_code)

    @property
    def is_valid(self):
        """Check if PIN is currently valid"""
        now = timezone.now()
        
        if not self.is_active:
            return False
        
        if self.valid_from and now < self.valid_from:
            return False
        
        if self.valid_until and now > self.valid_until:
            return False
        
        if self.max_usage and self.usage_count >= self.max_usage:
            return False
        
        return True

    def increment_usage(self):
        """Increment usage count"""
        self.usage_count += 1
        self.save(update_fields=['usage_count', 'updated_at'])


class GuestAccess(TimeStampedModel, UUIDModel):
    """
    Temporary guest access (NFC or PIN)
    """
    ACCESS_TYPE_CHOICES = [
        ('NFC', 'NFC Card'),
        ('PIN', 'PIN Code'),
    ]
    
    device = models.ForeignKey(
        'devices.Device',
        on_delete=models.CASCADE,
        related_name='guest_access'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='guest_access_created'
    )
    
    # Guest Info
    guest_name = models.CharField(max_length=100)
    guest_email = models.EmailField(blank=True)
    guest_phone = models.CharField(max_length=20, blank=True)
    
    # Access type
    access_type = models.CharField(max_length=10, choices=ACCESS_TYPE_CHOICES)
    
    # Link to NFC or PIN
    nfc_card = models.ForeignKey(
        NFCCard,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='guest_access'
    )
    pin_code = models.ForeignKey(
        PINCode,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='guest_access'
    )
    
    # Validity
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    
    # Status
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'guest_access'
        verbose_name = 'Guest Access'
        verbose_name_plural = 'Guest Access'
        ordering = ['-created_at']

    def __str__(self):
        return f"Guest: {self.guest_name} ({self.access_type})"

    @property
    def is_valid(self):
        """Check if guest access is valid"""
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_until
        )