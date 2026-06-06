from rest_framework.permissions import SAFE_METHODS, BasePermission


class RolePermission(BasePermission):
    allowed_roles = set()

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in self.allowed_roles)


class IsAdmin(RolePermission):
    allowed_roles = {"admin"}


class IsStudentOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        student = getattr(obj, "student", None) or getattr(getattr(obj, "placement", None), "student", None)
        return student == request.user


class IsSupervisorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in {"workplace_supervisor", "academic_supervisor", "admin"}
        )
