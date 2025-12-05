"""
Device serializers
"""

from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from .models import Device, DeviceLog, DeviceSharing
from apps.access.models import PINCode, NFCCard, GuestAccess
from apps.users.serializers import UserSerializer

User = get_user_model()


class DeviceListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for device list (optimized for list view)
    Does not include owner details since user is already authenticated
    """
    is_battery_low = serializers.BooleanField(read_only=True)
    is_shared = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = [
            'id',
            'device_id',
            'name',
            'device_type',
            'location',
            'status',
            'is_locked',
            'is_online',
            'battery_level',
            'is_battery_low',
            'keypad_enabled',
            'nfc_enabled',
            'last_seen',
            'last_unlock',
            'is_shared',  # Indicates if this is a shared device
        ]

    def get_is_shared(self, obj):
        """
        Check if this device is shared with the current user (not owned by them)
        """
        request = self.context.get('request')
        if request and request.user:
            return obj.owner != request.user
        return False


class DeviceSerializer(serializers.ModelSerializer):
    """
    Device serializer with detailed information
    Includes active PINs, NFCs, guests, and access statistics
    Perfect for landlords/property managers
    """
    is_battery_low = serializers.BooleanField(read_only=True)
    active_pins = serializers.SerializerMethodField()
    active_nfcs = serializers.SerializerMethodField()
    active_guests = serializers.SerializerMethodField()
    shared_with_count = serializers.SerializerMethodField()
    access_stats = serializers.SerializerMethodField()

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
            'created_at',
            'updated_at',
            # New fields
            'active_pins',
            'active_nfcs',
            'active_guests',
            'shared_with_count',
            'access_stats',
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
            'created_at',
            'updated_at',
        ]

    def get_active_pins(self, obj):
        """
        Get all active PIN codes for this device
        """
        pins = PINCode.objects.filter(
            device=obj,
            is_active=True
        ).select_related('user')

        return [{
            'id': pin.id,
            'name': pin.name,
            'user': pin.user.full_name if pin.user else 'Unknown',
            'valid_from': pin.valid_from,
            'valid_until': pin.valid_until,
            'usage_count': pin.usage_count,
            'max_usage': pin.max_usage,
            'is_valid': pin.is_valid,
        } for pin in pins]

    def get_active_nfcs(self, obj):
        """
        Get all active NFC cards for this device
        """
        nfcs = NFCCard.objects.filter(
            device=obj,
            is_active=True
        ).select_related('user')

        return [{
            'id': nfc.id,
            'name': nfc.name,
            'user': nfc.user.full_name if nfc.user else 'Unknown',
            'uid': nfc.uid[:6] + '...',  # Only show first 6 chars for security
            'valid_from': nfc.valid_from,
            'valid_until': nfc.valid_until,
            'usage_count': nfc.usage_count,
            'max_usage': nfc.max_usage,
            'is_valid': nfc.is_valid,
        } for nfc in nfcs]

    def get_active_guests(self, obj):
        """
        Get all active guest access for this device
        """
        guests = GuestAccess.objects.filter(
            device=obj,
            is_active=True
        )

        return [{
            'id': guest.id,
            'guest_name': guest.guest_name,
            'guest_email': guest.guest_email,
            'guest_phone': guest.guest_phone,
            'access_type': guest.access_type,
            'valid_from': guest.valid_from,
            'valid_until': guest.valid_until,
            'is_valid': guest.is_valid,
        } for guest in guests]

    def get_shared_with_count(self, obj):
        """
        Count how many users this device is shared with
        """
        return obj.shared_with.filter(is_active=True).count()

    def get_access_stats(self, obj):
        """
        Get access statistics for this device
        """
        # Get logs from last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_logs = DeviceLog.objects.filter(
            device=obj,
            created_at__gte=thirty_days_ago
        )

        # Count successful unlocks
        successful_unlocks = recent_logs.filter(
            event_type__in=['UNLOCK_NFC', 'UNLOCK_PIN', 'UNLOCK_REMOTE'],
            success=True
        ).count()

        # Count failed attempts
        failed_attempts = recent_logs.filter(success=False).count()

        # Get most recent activity
        last_activity = recent_logs.order_by('-created_at').first()

        return {
            'total_unlocks_30d': successful_unlocks,
            'failed_attempts_30d': failed_attempts,
            'last_activity': {
                'event_type': last_activity.event_type if last_activity else None,
                'description': last_activity.description if last_activity else None,
                'created_at': last_activity.created_at if last_activity else None,
            } if last_activity else None,
        }


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