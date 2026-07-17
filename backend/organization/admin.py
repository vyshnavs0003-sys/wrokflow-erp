from django.contrib import admin
from .models import Company, Department, Designation

# Register your models here.

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "phone",
        "office_start_time",
        "office_end_time",
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
        "is_active",
    )

    search_fields = (
        "name",
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