"""
Custom permissions
"""

from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permission to only allow owners of an object to access it
    """
    def has_object_permission(self, request, view, obj):
        # Check if object has 'user' or 'owner' field
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission to allow owners to edit, others to read only
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False