from django.contrib import admin
from .models import SalaryStructure, Payroll, PayrollItem, Payslip

# Register your models here.

@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "basic_salary",
        "effective_from",
        "is_active",
    )
    search_fields = (
        "employee__employee_id",
    )
    list_filter = (
        "is_active",
        "effective_from",
    )


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "month",
        "year",
        "gross_salary",
        "net_salary",
        "status",
    )
    search_fields = (
        "employee__employee_id",
    )
    list_filter = (
        "status",
        "month",
        "year",
    )


@admin.register(PayrollItem)
class PayrollItemAdmin(admin.ModelAdmin):
    list_display = (
        "payroll",
        "component_name",
        "component_type",
        "amount",
    )
    search_fields = (
        "component_name",
    )
    list_filter = (
        "component_type",
    )


@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = (
        "payroll",
        "generated_date",
    )
    search_fields = (
        "payroll__employee__employee_id",
    )