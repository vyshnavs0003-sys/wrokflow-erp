from django.contrib import admin
from .models import Client, Project, ProjectTeam, Task, TaskAssignment

# Register your models here.

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        "name", 
        "contact_person", 
        "email", 
        "phone", 
        "is_active",
        )
    search_fields = (
        "name", 
        "contact_person", 
        "email",
        )
    list_filter = (
        "is_active",
        )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name", 
        "client", 
        "project_manager", 
        "status", 
        "start_date", 
        "end_date",
        )
    search_fields = (
        "name", 
        "client__name",
        )
    list_filter = (
        "status", 
        "is_active",
        )
    ordering = (
        "name",
        )


@admin.register(ProjectTeam)
class ProjectTeamAdmin(admin.ModelAdmin):
    list_display = (
        "project", 
        "employee", 
        "role", 
        "assigned_date", 
        "is_active",
        )
    search_fields = (
        "project__name", 
        "employee__employee_id",
        )
    list_filter = (
        "role", 
        "is_active",
        )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title", 
        "project", 
        "priority", 
        "status", 
        "due_date",
        )
    search_fields = (
        "title", 
        "project__name",
        )
    list_filter = (
        "priority", 
        "status",
        )
    ordering = (
        "due_date",
        )


@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "task",
        "employee",
        "assigned_by",
        "assignment_status",
        "assigned_date",
    )
    search_fields = (
        "task__title",
        "employee__employee_id",
    )
    list_filter = (
        "assignment_status",
    )