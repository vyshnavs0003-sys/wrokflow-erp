from django.contrib import admin
from .models import (
LeaveType,
LeavePolicy,
LeaveAllocation,
Holiday,
LeaveRequest,
LeaveAttachment,
)

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = (
    "name",
    "is_paid",
    "annual_quota",
    "requires_approval",
    "requires_document",
    "max_consecutive_days",
    "is_active",
    )

    search_fields = ( 
        "name", 
    ) 

    list_filter = ( 
        "is_paid", 
        "requires_approval", 
        "requires_document", 
        "is_active", 
    ) 

@admin.register(LeavePolicy)
class LeavePolicyAdmin(admin.ModelAdmin):
    list_display = (
    "leave_type",
    "carry_forward_allowed",
    "max_carry_forward_days",
    "carry_forward_expiry_months",
    "encashment_allowed",
    "max_encashment_days",
    "is_active",
    )

    search_fields = ( 
        "leave_type__name", 
    ) 

    list_filter = ( 
        "carry_forward_allowed", 
        "encashment_allowed", 
        "is_active", 
    ) 

@admin.register(LeaveAllocation)
class LeaveAllocationAdmin(admin.ModelAdmin):
    list_display = (
    "employee",
    "leave_type",
    "year",
    "allocated_days",
    "carry_forward_days",
    "adjustment_days",
    )

    search_fields = ( 
        "employee__employee_id", 
        "employee__user__first_name", 
        "employee__user__last_name", 
        "leave_type__name", 
    ) 

    list_filter = ( 
        "year", 
        "leave_type", 
    ) 

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = (
    "name",
    "date",
    "is_optional",
    "is_active",
    )

    search_fields = ( 
        "name", 
    ) 

    list_filter = ( 
        "is_optional", 
        "is_active", 
        "date", 
    ) 

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
    "employee",
    "leave_type",
    "start_date",
    "end_date",
    "total_days",
    "status",
    "reviewed_by",
    "cancelled_at",
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

@admin.register(LeaveAttachment)
class LeaveAttachmentAdmin(admin.ModelAdmin):
    list_display = (
        "leave_request",
        "uploaded_by",
        "uploaded_at",
    )

    search_fields = (
        "leave_request__employee__employee_id",
        "leave_request__employee__user__first_name",
        "leave_request__employee__user__last_name",
        "leave_request__leave_type__name",
        "uploaded_by__username",
    )

    list_filter = (
        "uploaded_at",
    )

    ordering = (
        "-uploaded_at",
    )