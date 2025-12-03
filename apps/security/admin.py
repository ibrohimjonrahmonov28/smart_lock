"""
Security admin
"""

from django.contrib import admin
from .models import SecurityEvent, AuditLog


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    """
    Security Event admin
    """
    list_display = [
        'event_type',
        'severity',
        'user',
        'device',
        'ip_address',
        'resolved',
        'created_at',
    ]
    list_filter = [
        'event_type',
        'severity',
        'resolved',
        'created_at',
    ]
    search_fields = [
        'description',
        'user__email',
        'device__device_id',
        'ip_address',
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Event Info', {
            'fields': ('event_type', 'severity', 'description')
        }),
        ('Related', {
            'fields': ('user', 'device')
        }),
        ('Request Info', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Resolution', {
            'fields': ('resolved', 'resolved_at', 'resolved_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Audit Log admin (Read-only)
    """
    list_display = [
        'action',
        'resource_type',
        'user',
        'success',
        'ip_address',
        'created_at',
    ]
    list_filter = [
        'action',
        'resource_type',
        'success',
        'created_at',
    ]
    search_fields = [
        'action',
        'resource_type',
        'resource_id',
        'user__email',
        'ip_address',
    ]
    readonly_fields = [
        'id',
        'user',
        'action',
        'resource_type',
        'resource_id',
        'ip_address',
        'user_agent',
        'details',
        'success',
        'error_message',
        'previous_hash',
        'current_hash',
        'created_at',
    ]
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# Custom admin site config
admin.site.site_header = 'SmartLock Security Admin'
admin.site.index_title = 'Security & Monitoring'