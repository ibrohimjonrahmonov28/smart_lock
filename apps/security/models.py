"""
Security models - Audit logs and security events
"""

from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import TimeStampedModel, UUIDModel

User = get_user_model()


class SecurityEvent(TimeStampedModel, UUIDModel):
    """
    Security events and audit logs
    """
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    EVENT_TYPE_CHOICES = [
        ('LOGIN_SUCCESS', 'Login Success'),
        ('LOGIN_FAILED', 'Login Failed'),
        ('LOGOUT', 'Logout'),
        ('PASSWORD_CHANGE', 'Password Changed'),
        ('DEVICE_ADDED', 'Device Added'),
        ('DEVICE_REMOVED', 'Device Removed'),
        ('UNLOCK_SUCCESS', 'Unlock Success'),
        ('UNLOCK_FAILED', 'Unlock Failed'),
        ('INVALID_SIGNATURE', 'Invalid Signature'),
        ('REPLAY_ATTACK', 'Replay Attack Detected'),
        ('TAMPER_DETECTED', 'Tamper Detected'),
        ('BRUTE_FORCE', 'Brute Force Attempt'),
        ('UNAUTHORIZED_ACCESS', 'Unauthorized Access Attempt'),
    ]

    # Event info
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='LOW')
    
    # User (if applicable)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='security_events'
    )
    
    # Device (if applicable)
    device = models.ForeignKey(
        'devices.Device',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='security_events'
    )
    
    # Request info
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    # Details
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    
    # Resolution
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='security_events_resolved'
    )

    class Meta:
        db_table = 'security_events'
        verbose_name = 'Security Event'
        verbose_name_plural = 'Security Events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', '-created_at']),
            models.Index(fields=['severity', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['device', '-created_at']),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.severity} - {self.created_at}"


class AuditLog(TimeStampedModel, UUIDModel):
    """
    Immutable audit logs (append-only)
    """
    # Who
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # What
    action = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=50)
    resource_id = models.CharField(max_length=50, blank=True)
    
    # When & Where
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    # Details
    details = models.JSONField(default=dict)
    
    # Result
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    # Tamper protection (hash chain)
    previous_hash = models.CharField(max_length=64, blank=True)
    current_hash = models.CharField(max_length=64)

    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-created_at']
        permissions = [
            ('view_audit_logs', 'Can view audit logs'),
        ]

    def __str__(self):
        return f"{self.action} by {self.user} at {self.created_at}"

    def save(self, *args, **kwargs):
        """Calculate hash chain on save"""
        if not self.pk:
            import hashlib
            
            # Get last log
            last_log = AuditLog.objects.order_by('-created_at').first()
            self.previous_hash = last_log.current_hash if last_log else '0' * 64
            
            # Calculate current hash
            data = f"{self.created_at}{self.action}{self.resource_type}{self.previous_hash}"
            self.current_hash = hashlib.sha256(data.encode()).hexdigest()
        
        super().save(*args, **kwargs)