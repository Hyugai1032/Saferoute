from rest_framework.permissions import BasePermission


class IsProvincialAdmin(BasePermission):
    """
    Allows access only to Provincial Admins.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Adjust based on your user model
        # Option 1: role field
        if hasattr(user, "role") and user.role == "PROVINCIAL_ADMIN":
            return True

        # Option 2: no municipality = provincial
        if hasattr(user, "municipality") and user.municipality is None:
            return True

        return False