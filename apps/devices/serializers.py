"""
Device serializers
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Device, DeviceLog, DeviceSharing
from apps.users.serializers import UserSerializer

User = get_user_model()


class DeviceSerializer(serializers.ModelSerializer):
    """
    Device serializer
    """
    owner = UserSerializer(read_only=True)
    is_battery_low = serializers.BooleanField(read_only=True)

    class Meta:
        model = Device
        fields = [
            'id',
            'device_id',
            'name',
            'device_type',
            'location',
            'latitude',
            'longitude',
            'status',
            'is_locked',
            'is_online',
            'battery_level',
            'battery_low_threshold',
            'is_battery_low',
            'keypad_enabled',
            'nfc_enabled',
            'last_seen',
            'last_unlock',
            'last_lock',
            'owner',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'device_secret',
            'is_locked',
            'is_online',
            'battery_level',
            'last_seen',
            'last_unlock',
            'last_lock',
            'owner',
            'created_at',
            'updated_at',
        ]


class DeviceCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new device
    """
    class Meta:
        model = Device
        fields = ['device_id', 'name', 'device_type', 'location', 'latitude', 'longitude']

    def validate_device_id(self, value):
        """
        Check device_id is unique
        """
        if Device.objects.filter(device_id=value).exists():
            raise serializers.ValidationError('Device with this ID already exists')
        return value


class DeviceUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating device
    """
    class Meta:
        model = Device
        fields = ['name', 'location', 'latitude', 'longitude', 'battery_low_threshold', 'status']


class DeviceUnlockSerializer(serializers.Serializer):
    """
    Serializer for unlock/lock commands
    """
    duration = serializers.IntegerField(
        default=5,
        min_value=1,
        max_value=30,
        help_text='Duration in seconds (1-30)'
    )


class DeviceLogSerializer(serializers.ModelSerializer):
    """
    Device log serializer
    """
    user = UserSerializer(read_only=True)
    device_name = serializers.CharField(source='device.name', read_only=True)

    class Meta:
        model = DeviceLog
        fields = [
            'id',
            'device',
            'device_name',
            'user',
            'event_type',
            'description',
            'ip_address',
            'success',
            'error_message',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class DeviceSharingSerializer(serializers.ModelSerializer):
    """
    Device sharing serializer
    """
    device = DeviceSerializer(read_only=True)
    shared_with = UserSerializer(read_only=True)
    shared_by = UserSerializer(read_only=True)

    class Meta:
        model = DeviceSharing
        fields = [
            'id',
            'device',
            'shared_with',
            'shared_by',
            'role',
            'can_unlock',
            'can_lock',
            'can_view_logs',
            'can_manage_access',
            'can_share',
            'expires_at',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'shared_by', 'created_at']


class DeviceSharingCreateSerializer(serializers.Serializer):
    """
    Create device sharing
    """
    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=['ADMIN', 'MEMBER', 'VIEWER'],
        default='MEMBER'
    )
    expires_at = serializers.DateTimeField(required=False, allow_null=True)

    def validate_email(self, value):
        """
        Validate user exists
        """
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('User with this email does not exist')
        return value