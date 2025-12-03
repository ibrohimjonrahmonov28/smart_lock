"""
Device permissions
"""

from rest_framework import permissions
from .models import DeviceSharing


class IsDeviceOwner(permissions.BasePermission):
    """
    Permission to check if user is device owner
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsDeviceOwnerOrShared(permissions.BasePermission):
    """
    Permission to check if user is owner or device is shared with them
    """
    def has_object_permission(self, request, view, obj):
        # Owner has full access
        if obj.owner == request.user:
            return True
        
        # Check if device is shared
        try:
            sharing = DeviceSharing.objects.get(
                device=obj,
                shared_with=request.user,
                is_active=True
            )
            
            # Check specific permissions
            if request.method == 'DELETE':
                return False  # Only owner can delete
            
            if request.method in ['PUT', 'PATCH']:
                return sharing.role in ['ADMIN']
            
            return True  # Read access
        except DeviceSharing.DoesNotExist:
            return False


class CanUnlockDevice(permissions.BasePermission):
    """
    Permission to check if user can unlock device
    """
    def has_object_permission(self, request, view, obj):
        # Owner can always unlock
        if obj.owner == request.user:
            return True
        
        # Check sharing permissions
        try:
            sharing = DeviceSharing.objects.get(
                device=obj,
                shared_with=request.user,
                is_active=True
            )
            return sharing.can_unlock
        except DeviceSharing.DoesNotExist:
            return False