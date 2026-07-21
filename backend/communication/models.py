from django.db import models
from employees.models import Employee
from organization.models import Department
# Create your models here.

class Announcement(models.Model):

    PRIORITY_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
        ("Urgent", "Urgent"),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    created_by = models.ForeignKey(Employee,on_delete=models.PROTECT,related_name="announcements")
    target_department = models.ForeignKey(Department,on_delete=models.SET_NULL, related_name="announcements",blank=True,null=True)
    publish_date = models.DateTimeField()
    expiry_date = models.DateTimeField(blank=True,null=True)
    priority = models.CharField(max_length=20,choices=PRIORITY_CHOICES,default="Medium")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-publish_date"]

    def __str__(self):
        return self.title


class Notification(models.Model):

    NOTIFICATION_TYPE_CHOICES = [
        ("Leave", "Leave"),
        ("Task", "Task"),
        ("Payroll", "Payroll"),
        ("Attendance", "Attendance"),
        ("Announcement", "Announcement"),
        ("System", "System"),
    ]

    recipient = models.ForeignKey(Employee,on_delete=models.CASCADE,related_name="notifications")
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20,choices=NOTIFICATION_TYPE_CHOICES,default="System")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recipient} - {self.title}"