from django.contrib import admin
from .models import Company, Department, Designation, OfficeTiming, Team

# Register your models here.

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
    "name",
    "email",
    "phone",
    "is_active",
    )

    search_fields = (
        "name",
        "email",
    )

    list_filter = (
        "is_active",
    )

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
    "name",
    "company",
    "department_head",
    "is_active",
    )

    search_fields = (
        "name",
        "department_head__employee_id",
        "department_head__user__username",
    )

    list_filter = (
        "company",
        "is_active",
    )

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = (
    "name",
    "department",
    "is_active",
    )

    search_fields = (
        "name",
        "department__name",
    )

    list_filter = (
        "department",
        "is_active",
    )

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
    "name",
    "department",
    "is_active",
    )

    search_fields = (
        "name",
        "department__name",
    )

    list_filter = (
        "department",
        "is_active",
    )

@admin.register(OfficeTiming)
class OfficeTimingAdmin(admin.ModelAdmin):
    list_display = (
    "shift_name",
    "company",
    "start_time",
    "end_time",
    "grace_minutes",
    "is_active",
    )

    search_fields = (
        "shift_name",
        "company__name",
    )

    list_filter = (
        "company",
        "is_active",
    )

    ordering = (
        "company",
        "start_time",
    )