"""
Security serializers
"""

from rest_framework import serializers
from .models import SecurityEvent, AuditLog
from apps.users.serializers import UserSerializer


class SecurityEventSerializer(serializers.ModelSerializer):
    """
    Security Event serializer
    """
    user = UserSerializer(read_only=True)
    device_name = serializers.CharField(source='device.name', read_only=True, allow_null=True)

    class Meta:
        model = SecurityEvent
        fields = [
            'id',
            'event_type',
            'severity',
            'user',
            'device',
            'device_name',
            'ip_address',
            'user_agent',
            'description',
            'metadata',
            'resolved',
            'resolved_at',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Audit Log serializer
    """
    user_email = serializers.CharField(source='user.email', read_only=True, allow_null=True)

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'user',
            'user_email',
            'action',
            'resource_type',
            'resource_id',
            'ip_address',
            'details',
            'success',
            'error_message',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']