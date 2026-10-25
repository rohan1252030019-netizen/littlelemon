from rest_framework.permissions import SAFE_METHODS, BasePermission


def is_manager(user) -> bool:
    """Return True for staff users and members of the Manager group."""
    return bool(
        user
        and user.is_authenticated
        and (user.is_staff or user.groups.filter(name="Manager").exists())
    )


class IsManager(BasePermission):
    """Allow access only to restaurant managers."""

    message = "Only members of the Manager group can perform this action."

    def has_permission(self, request, view):
        return is_manager(request.user)


class ReadOnlyOrManager(BasePermission):
    """Anyone may read; only managers may create, update or delete."""

    message = "Only members of the Manager group can modify the menu."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return is_manager(request.user)


class IsOwnerOrManager(BasePermission):
    """A booking may be accessed by its owner or by a manager."""

    message = "You can only access your own bookings."

    def has_object_permission(self, request, view, obj):
        return is_manager(request.user) or obj.user_id == request.user.id
