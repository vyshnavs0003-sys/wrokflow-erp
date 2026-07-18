from django.contrib import admin
from .models import Attendance
# Register your models here.

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "attendance_date",
        "check_in",
        "check_out",
        "status",
    )

    search_fields = (
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
    )

    list_filter = (
        "attendance_date",
        "status",
    )

    ordering = (
        "-attendance_date",
        "-check_in",
    )
