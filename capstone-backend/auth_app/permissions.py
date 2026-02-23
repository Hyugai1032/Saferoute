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
    
class GisLayerRolePermission(BasePermission):
    """
    Read: authenticated Municipal/Provincial admins (or adjust to allow public)
    Write:
      - Provincial admin: can write any municipality
      - Municipal admin: only their own municipality
    """

    def has_permission(self, request, view):
        user = request.user

        # --- READ ---
        if request.method in SAFE_METHODS:
            return user and user.is_authenticated and user.role in ["PROVINCIAL_ADMIN", "MUNICIPAL_ADMIN"]

        # --- WRITE ---
        if not user or not user.is_authenticated:
            return False

        if user.role == "PROVINCIAL_ADMIN":
            return True

        if user.role == "MUNICIPAL_ADMIN":
            # For POST, enforce municipality in request.data matches user's municipality
            if request.method == "POST":
                user_mun_id = getattr(getattr(user, "municipality", None), "id", None)
                req_mun_id = request.data.get("municipality")

                if not user_mun_id:
                    return False

                try:
                    req_mun_id = int(req_mun_id)
                except (TypeError, ValueError):
                    return False

                return req_mun_id == user_mun_id

            # For PATCH/PUT/DELETE we validate per-object in has_object_permission
            return True

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in SAFE_METHODS:
            return user and user.is_authenticated and user.role in ["PROVINCIAL_ADMIN", "MUNICIPAL_ADMIN"]

        if user.role == "PROVINCIAL_ADMIN":
            return True

        if user.role == "MUNICIPAL_ADMIN":
            user_mun_id = getattr(getattr(user, "municipality", None), "id", None)
            return user_mun_id is not None and obj.municipality_id == user_mun_id

        return False