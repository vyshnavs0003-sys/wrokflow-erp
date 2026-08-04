from rest_framework.permissions import BasePermission


class IsHRorSuperAdmin(BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(
            name="HR"
        ).exists()


class IsEmployeeOwner(BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return hasattr(
            request.user,
            "employee_profile"
        )

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(
            name="HR"
        ).exists():
            return True
        return obj.employee == request.user.employee_profile


class IsHRorSuperAdminOrReportingManager(BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(
            name="HR"
        ).exists():
            return True
        return hasattr(
            request.user,
            "employee_profile"
        )

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(
            name="HR"
        ).exists():
            return True
        if not hasattr(
            request.user,
            "employee_profile"
        ):
            return False
        return (
            obj.employee.reporting_manager
            == request.user.employee_profile
        )