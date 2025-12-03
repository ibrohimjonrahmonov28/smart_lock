"""
User permissions
"""

from rest_framework import permissions


class IsSelfOrAdmin(permissions.BasePermission):
    """
    Permission to only allow users to access their own profile
    or admins to access any profile
    """
    def has_object_permission(self, request, view, obj):
        # Admin can access any profile
        if request.user.is_staff:
            return True
        
        # User can only access their own profile
        return obj == request.user