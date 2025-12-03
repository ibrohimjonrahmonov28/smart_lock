"""
Access serializers
"""

from rest_framework import serializers
from django.utils import timezone
from .models import NFCCard, PINCode, GuestAccess
from apps.core.utils.encryption import hash_pin_code, verify_pin_code


class NFCCardSerializer(serializers.ModelSerializer):
    """
    NFC Card serializer
    """
    is_valid = serializers.BooleanField(read_only=True)
    device_name = serializers.CharField(source='device.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True, allow_null=True)

    class Meta:
        model = NFCCard
        fields = [
            'id',
            'device',
            'device_name',
            'user',
            'user_email',
            'uid',
            'name',
            'valid_from',
            'valid_until',
            'usage_count',
            'max_usage',
            'allowed_days',
            'allowed_hours',
            'is_active',
            'is_valid',
            'created_at',
        ]
        read_only_fields = ['id', 'usage_count', 'created_at']


class NFCCardCreateSerializer(serializers.ModelSerializer):
    """
    Create NFC Card
    """
    class Meta:
        model = NFCCard
        fields = [
            'uid',
            'name',
            'user',
            'valid_from',
            'valid_until',
            'max_usage',
            'allowed_days',
            'allowed_hours',
        ]

    def validate_uid(self, value):
        """Validate UID is unique"""
        if NFCCard.objects.filter(uid=value).exists():
            raise serializers.ValidationError('NFC card with this UID already exists')
        return value


class PINCodeSerializer(serializers.ModelSerializer):
    """
    PIN Code serializer
    """
    is_valid = serializers.BooleanField(read_only=True)
    device_name = serializers.CharField(source='device.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True, allow_null=True)

    class Meta:
        model = PINCode
        fields = [
            'id',
            'device',
            'device_name',
            'user',
            'user_email',
            'name',
            'valid_from',
            'valid_until',
            'usage_count',
            'max_usage',
            'allowed_days',
            'allowed_hours',
            'is_active',
            'is_valid',
            'created_at',
        ]
        read_only_fields = ['id', 'usage_count', 'created_at']


class PINCodeCreateSerializer(serializers.Serializer):
    """
    Create PIN Code
    """
    pin_code = serializers.CharField(min_length=4, max_length=8, write_only=True)
    name = serializers.CharField(max_length=100)
    user = serializers.IntegerField(required=False, allow_null=True)
    valid_from = serializers.DateTimeField(default=timezone.now)
    valid_until = serializers.DateTimeField(required=False, allow_null=True)
    max_usage = serializers.IntegerField(required=False, allow_null=True)
    allowed_days = serializers.ListField(required=False, default=list)
    allowed_hours = serializers.DictField(required=False, default=dict)

    def validate_user(self, value):
        """Validate user exists if provided"""
        if value is not None:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if not User.objects.filter(pk=value).exists():
                raise serializers.ValidationError('User does not exist')
        return value


class GuestAccessSerializer(serializers.ModelSerializer):
    """
    Guest Access serializer
    """
    is_valid = serializers.BooleanField(read_only=True)
    device_name = serializers.CharField(source='device.name', read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)

    class Meta:
        model = GuestAccess
        fields = [
            'id',
            'device',
            'device_name',
            'created_by',
            'created_by_email',
            'guest_name',
            'guest_email',
            'guest_phone',
            'access_type',
            'valid_from',
            'valid_until',
            'is_active',
            'is_valid',
            'created_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at']


class GuestAccessCreateSerializer(serializers.Serializer):
    """
    Create guest access
    """
    guest_name = serializers.CharField(max_length=100)
    guest_email = serializers.EmailField(required=False, allow_blank=True)
    guest_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    access_type = serializers.ChoiceField(choices=['NFC', 'PIN'])
    valid_from = serializers.DateTimeField()
    valid_until = serializers.DateTimeField()
    
    # For NFC
    nfc_uid = serializers.CharField(required=False, allow_blank=True)
    
    # For PIN
    pin_code = serializers.CharField(required=False, allow_blank=True, min_length=4, max_length=8)

    def validate(self, attrs):
        """Validate based on access type"""
        access_type = attrs.get('access_type')
        
        if access_type == 'NFC' and not attrs.get('nfc_uid'):
            raise serializers.ValidationError({'nfc_uid': 'NFC UID is required for NFC access'})
        
        if access_type == 'PIN' and not attrs.get('pin_code'):
            raise serializers.ValidationError({'pin_code': 'PIN code is required for PIN access'})
        
        # Validate dates
        if attrs['valid_from'] >= attrs['valid_until']:
            raise serializers.ValidationError('valid_until must be after valid_from')
        
        return attrs