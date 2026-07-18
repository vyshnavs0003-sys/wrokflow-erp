from django.contrib import admin
from .models import LeaveType, LeaveRequest
# Register your models here.

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_paid",
        "is_active",
    )

    search_fields = (
        "name",
    )

    list_filter = (
        "is_paid",
        "is_active",
    )

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "leave_type",
        "start_date",
        "end_date",
        "status",
        "reviewed_by",
    )

    search_fields = (
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
        "leave_type__name",
    )

    list_filter = (
        "status",
        "leave_type",
        "start_date",
    )

    ordering = (
        "-created_at",
    )    