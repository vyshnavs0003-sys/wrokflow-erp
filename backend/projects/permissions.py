from rest_framework.permissions import BasePermission

class CanManageProjects(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_superuser:
            return True
        if user.groups.filter(name="HR").exists():
            return request.method == "GET"
        if user.groups.filter(name="Employee").exists():
            return request.method == "GET"
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True
        if user.groups.filter(name="HR").exists():
            return request.method == "GET"
        if user.groups.filter(name="Employee").exists():
            if obj.project_manager.user == user:
                return True
            if request.method == "GET":
                return True
        return False