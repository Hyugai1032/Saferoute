# auth_app/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsProvincialAdmin(BasePermission):
    """Only Provincial Admin - full access"""
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'PROVINCIAL_ADMIN'
        )


class IsMunicipalAdminOrHigher(BasePermission):
    """Municipal Admin or Provincial Admin"""
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['PROVINCIAL_ADMIN', 'MUNICIPAL_ADMIN']
        )


class IsStaffOrHigher(BasePermission):
    """Response Team, Evac Center Staff, or any Admin"""
    def has_permission(self, request, view):
        allowed_roles = [
            'PROVINCIAL_ADMIN', 
            'MUNICIPAL_ADMIN', 
            'RESPONSE_TEAM', 
            'EVAC_CENTER_STAFF'
        ]
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in allowed_roles
        )


class IsOwnerOrAdmin(BasePermission):
    """User can access their own data, or Admin can access anyone's"""
    def has_object_permission(self, request, view, obj):
        # Admin can access anyone
        if request.user.role in ['PROVINCIAL_ADMIN', 'MUNICIPAL_ADMIN']:
            return True
        # Users can only access themselves
        return obj.id == request.user.id
    
class GisLayerAdminWriteElseReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_staff