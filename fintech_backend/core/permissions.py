"""
Custom permissions for the fintech application.
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsAccountOwner(permissions.BasePermission):
    """
    Custom permission to only allow account owners to access their data.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Check if the object has a user field and if it matches the request user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        # For user objects, check if it's the same user
        if hasattr(obj, 'id') and hasattr(request.user, 'id'):
            return obj.id == request.user.id
        return False