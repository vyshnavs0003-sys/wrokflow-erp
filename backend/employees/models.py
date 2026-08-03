from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from organization.models import Department, Designation, OfficeTiming, Team

# Create your models here.

class Employee(models.Model):
    GENDER_CHOICES = [
    ("Male", "Male"),
    ("Female", "Female"),
    ("Other", "Other"),
    ]

    EMPLOYMENT_TYPE_CHOICES = [
        ("Full Time", "Full Time"),
        ("Intern", "Intern"),
        ("Contract", "Contract"),
    ]

    STATUS_CHOICES = [
        ("Active", "Active"),
        ("On Leave", "On Leave"),
        ("Resigned", "Resigned"),
    ]

    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="employee_profile")
    employee_id = models.CharField(max_length=20,unique=True)
    department = models.ForeignKey(Department,on_delete=models.PROTECT,related_name="employees")
    team = models.ForeignKey(Team,on_delete=models.PROTECT,related_name="employees",blank=True,null=True)
    designation = models.ForeignKey(Designation,on_delete=models.PROTECT,related_name="employees")
    reporting_manager = models.ForeignKey("self",on_delete=models.SET_NULL,related_name="direct_reports",blank=True,null=True)
    office_timing = models.ForeignKey(OfficeTiming,on_delete=models.PROTECT,related_name="employees",blank=True,null=True)
    phone = models.CharField(max_length=15)
    profile_photo = models.ImageField(upload_to="employees/profile_photos/",blank=True,null=True)
    gender = models.CharField(max_length=10,choices=GENDER_CHOICES)
    joining_date = models.DateField()
    employment_type = models.CharField(max_length=20,choices=EMPLOYMENT_TYPE_CHOICES)
    address = models.TextField()
    emergency_contact = models.CharField(max_length=15)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="Active")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["employee_id"]
        verbose_name = "Employee"
        verbose_name_plural = "Employees"

    def clean(self):
        if self.team and self.team.department_id != self.department_id:
            raise ValidationError({
                "team": "The selected team must belong to the selected department."
            })

        if self.designation and self.designation.department_id != self.department_id:
            raise ValidationError({
                "designation": "The selected designation must belong to the selected department."
            })

        if self.reporting_manager:
            if self.reporting_manager_id == self.pk:
                raise ValidationError({
                    "reporting_manager": "An employee cannot be their own reporting manager."
                })

            if not self.reporting_manager.is_active or self.reporting_manager.status == "Resigned":
                raise ValidationError({
                    "reporting_manager": "The selected reporting manager must be an active employee."
                })

            if self.department and self.reporting_manager.department.company_id != self.department.company_id:
                raise ValidationError({
                    "reporting_manager": "The reporting manager must belong to the same company."
                })

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"