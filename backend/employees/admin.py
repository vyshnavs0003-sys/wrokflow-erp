from django.contrib import admin
from .models import Employee

# Register your models here.

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
    "employee_id",
    "user",
    "department",
    "team",
    "designation",
    "reporting_manager",
    "office_timing",
    "phone",
    "status",
    )

    search_fields = (
        "employee_id",
        "user__first_name",
        "user__last_name",
        "user__username",
        "reporting_manager__employee_id",
        "reporting_manager__user__username",
    )

    list_filter = (
        "department",
        "team",
        "designation",
        "office_timing",
        "status",
    )