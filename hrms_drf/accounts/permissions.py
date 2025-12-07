from rest_framework.permissions import BasePermission


class IsHRUser(BasePermission):
    """
    Allows access only to users with role 'HR'.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and
                    getattr(request.user, 'role', None) == 'HR')
