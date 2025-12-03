"""
Access admin
"""

from django.contrib import admin
from .models import NFCCard, PINCode, GuestAccess


@admin.register(NFCCard)
class NFCCardAdmin(admin.ModelAdmin):
    """
    NFC Card admin
    """
    list_display = [
        'name',
        'uid',
        'device',
        'user',
        'is_active',
        'is_valid',
        'usage_count',
        'created_at',
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'uid', 'device__name', 'user__email']
    readonly_fields = ['id', 'usage_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Card Info', {
            'fields': ('uid', 'name', 'device', 'user')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Usage', {
            'fields': ('usage_count', 'max_usage')
        }),
        ('Restrictions', {
            'fields': ('allowed_days', 'allowed_hours')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(PINCode)
class PINCodeAdmin(admin.ModelAdmin):
    """
    PIN Code admin
    """
    list_display = [
        'name',
        'device',
        'user',
        'is_active',
        'is_valid',
        'usage_count',
        'created_at',
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'device__name', 'user__email']
    readonly_fields = ['id', 'pin_hash', 'usage_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('PIN Info', {
            'fields': ('name', 'device', 'user', 'pin_hash')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Usage', {
            'fields': ('usage_count', 'max_usage')
        }),
        ('Restrictions', {
            'fields': ('allowed_days', 'allowed_hours')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(GuestAccess)
class GuestAccessAdmin(admin.ModelAdmin):
    """
    Guest Access admin
    """
    list_display = [
        'guest_name',
        'device',
        'access_type',
        'is_active',
        'valid_from',
        'valid_until',
        'created_at',
    ]
    list_filter = ['access_type', 'is_active', 'created_at']
    search_fields = ['guest_name', 'guest_email', 'device__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Guest Info', {
            'fields': ('guest_name', 'guest_email', 'guest_phone')
        }),
        ('Access', {
            'fields': ('device', 'access_type', 'nfc_card', 'pin_code')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_until', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )