from django.contrib import admin
from .models import (
    Shift,
    EmployeeShiftAssignment,
    Attendance,
    AttendanceRegularization,
    AttendanceAdjustment,
    AttendanceLog,
    AttendanceAttachment,
    Overtime,
)


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "start_time",
        "end_time",
        "grace_time_minutes",
        "minimum_half_day_hours",
        "minimum_full_day_hours",
        "is_night_shift",
        "is_active",
    )

    search_fields = (
        "name",
    )

    list_filter = (
        "is_night_shift",
        "is_active",
    )

    ordering = (
        "name",
    )


@admin.register(EmployeeShiftAssignment)
class EmployeeShiftAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "shift",
        "effective_from",
        "effective_to",
        "is_active",
    )

    search_fields = (
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
        "shift__name",
    )

    list_filter = (
        "shift",
        "is_active",
    )

    ordering = (
        "-effective_from",
    )


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "attendance_date",
        "shift",
        "check_in",
        "check_out",
        "worked_hours",
        "late_minutes",
        "early_exit_minutes",
        "status",
    )

    search_fields = (
        "employee__employee_id",
        "employee__user__first_name",
        "employee__user__last_name",
    )

    list_filter = (
        "status",
        "shift",
        "attendance_date",
    )

    ordering = (
        "-attendance_date",
    )


@admin.register(AttendanceRegularization)
class AttendanceRegularizationAdmin(admin.ModelAdmin):
    list_display = (
        "attendance",
        "status",
        "reviewed_by",
        "reviewed_at",
        "created_at",
    )

    search_fields = (
        "attendance__employee__employee_id",
        "attendance__employee__user__first_name",
        "attendance__employee__user__last_name",
    )

    list_filter = (
        "status",
    )

    ordering = (
        "-created_at",
    )


@admin.register(AttendanceAdjustment)
class AttendanceAdjustmentAdmin(admin.ModelAdmin):
    list_display = (
        "attendance",
        "adjustment_type",
        "minutes",
        "adjusted_by",
        "created_at",
    )

    search_fields = (
        "attendance__employee__employee_id",
        "attendance__employee__user__first_name",
        "attendance__employee__user__last_name",
    )

    list_filter = (
        "adjustment_type",
    )

    ordering = (
        "-created_at",
    )


@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    list_display = (
        "attendance",
        "action",
        "performed_by",
        "created_at",
    )

    search_fields = (
        "attendance__employee__employee_id",
        "attendance__employee__user__first_name",
        "attendance__employee__user__last_name",
    )

    list_filter = (
        "action",
    )

    ordering = (
        "-created_at",
    )


@admin.register(AttendanceAttachment)
class AttendanceAttachmentAdmin(admin.ModelAdmin):
    list_display = (
        "attendance",
        "uploaded_by",
        "uploaded_at",
    )

    search_fields = (
        "attendance__employee__employee_id",
        "attendance__employee__user__first_name",
        "attendance__employee__user__last_name",
        "uploaded_by__username",
    )

    list_filter = (
        "uploaded_at",
    )

    ordering = (
        "-uploaded_at",
    )


@admin.register(Overtime)
class OvertimeAdmin(admin.ModelAdmin):
    list_display = (
        "attendance",
        "overtime_minutes",
        "status",
        "approved_by",
        "approved_at",
    )

    search_fields = (
        "attendance__employee__employee_id",
        "attendance__employee__user__first_name",
        "attendance__employee__user__last_name",
    )

    list_filter = (
        "status",
    )

    ordering = (
        "-created_at",
    )