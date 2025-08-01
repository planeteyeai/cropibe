from rest_framework.permissions import BasePermission


class HasRolePermission(BasePermission):
    """
    Generic permission that checks if the user has any of the given roles.
    Set `roles` in subclasses.
    """
    roles = []

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (
            user.is_superuser or user.has_any_role(self.roles)
        )


class IsSuperAdmin(HasRolePermission):
    roles = ['admin']


class IsAdmin(HasRolePermission):
    roles = ['admin']


class IsManager(HasRolePermission):
    roles = ['manager']


class IsAgronomist(HasRolePermission):
    roles = ['agronomist']


class IsQualityControl(HasRolePermission):
    roles = ['qualitycontrol']


class IsFieldOfficer(HasRolePermission):
    roles = ['fieldofficer']


class IsFarmer(HasRolePermission):
    roles = ['farmer']


class IsOwner(BasePermission):
    """
    Grants permission only if the authenticated user is the object owner.
    """
    def has_object_permission(self, request, view, obj):
        return bool(request.user.is_authenticated and obj.id == request.user.id)
