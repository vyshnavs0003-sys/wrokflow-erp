from django.db import models
from employees.models import Employee

# Create your models here.
class Attendance(models.Model):
    STATUS_CHOICES = [
        ("Present", "Present"),
        ("Absent", "Absent"),
        ("Half Day", "Half Day"),
        ("Work From Home", "Work From Home"),
        ("On Leave", "On Leave"),
        ("Holiday", "Holiday"),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.PROTECT,related_name="attendance_records")
    attendance_date = models.DateField()
    check_in = models.TimeField(blank=True,null=True)
    check_out = models.TimeField(blank=True,null=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="Present")
    remarks = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-attendance_date"]
        unique_together = ("employee", "attendance_date")
        verbose_name = "Attendance"
        verbose_name_plural = "Attendance"

    def __str__(self):
        return f"{self.employee.employee_id} - {self.attendance_date}"    

