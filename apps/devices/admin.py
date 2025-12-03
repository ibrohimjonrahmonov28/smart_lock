"""
Device admin
"""

from django.contrib import admin
from .models import Device, DeviceLog, DeviceSharing


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    """
    Device admin
    """
    list_display = [
        'device_id',
        'name',
        'owner',
        'device_type',
        'status',
        'is_locked',
        'is_online',
        'battery_level',
        'created_at',
    ]
    list_filter = [
        'device_type',
        'status',
        'is_online',
        'is_locked',
        'created_at',
    ]
    search_fields = ['device_id', 'name', 'owner__email', 'location']
    readonly_fields = [
        'id',
        'device_secret',
        'last_seen',
        'last_unlock',
        'last_lock',
        'created_at',
        'updated_at',
    ]
    
    fieldsets = (
        ('Device Info', {
            'fields': ('device_id', 'name', 'device_type', 'owner')
        }),
        ('Location', {
            'fields': ('location', 'latitude', 'longitude')
        }),
        ('Status', {
            'fields': ('status', 'is_locked', 'is_online')
        }),
        ('Battery', {
            'fields': ('battery_level', 'battery_low_threshold')
        }),
        ('Features', {
            'fields': ('keypad_enabled', 'nfc_enabled')
        }),
        ('Security', {
            'fields': ('device_secret',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('last_seen', 'last_unlock', 'last_lock', 'created_at', 'updated_at')
        }),
    )


@admin.register(DeviceLog)
class DeviceLogAdmin(admin.ModelAdmin):
    """
    Device log admin
    """
    list_display = [
        'device',
        'event_type',
        'user',
        'success',
        'ip_address',
        'created_at',
    ]
    list_filter = [
        'event_type',
        'success',
        'created_at',
    ]
    search_fields = ['device__device_id', 'device__name', 'user__email', 'description']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(DeviceSharing)
class DeviceSharingAdmin(admin.ModelAdmin):
    """
    Device sharing admin
    """
    list_display = [
        'device',
        'shared_with',
        'role',
        'is_active',
        'expires_at',
        'created_at',
    ]
    list_filter = [
        'role',
        'is_active',
        'created_at',
    ]
    search_fields = [
        'device__device_id',
        'device__name',
        'shared_with__email',
        'shared_by__email',
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']