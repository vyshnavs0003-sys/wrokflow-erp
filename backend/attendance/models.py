from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from employees.models import Employee


class Shift(models.Model):
    name = models.CharField(max_length=100,unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    grace_time_minutes = models.PositiveIntegerField(default=10)
    minimum_half_day_hours = models.DecimalField(max_digits=4,decimal_places=2,default=4.00)
    minimum_full_day_hours = models.DecimalField(max_digits=4,decimal_places=2,default=8.00)
    is_night_shift = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Shift"
        verbose_name_plural = "Shifts"

    def clean(self):
        if (not self.is_night_shift and self.end_time <= self.start_time):
            raise ValidationError({
                "end_time":
                "End time must be greater than start time."
            })

    def __str__(self):
        return self.name

class EmployeeShiftAssignment(models.Model):

    employee = models.ForeignKey(Employee,on_delete=models.PROTECT,related_name="shift_assignments")
    shift = models.ForeignKey(Shift,on_delete=models.PROTECT,related_name="employee_assignments")
    effective_from = models.DateField()
    effective_to = models.DateField(blank=True,null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-effective_from"]
        verbose_name = ("Employee Shift Assignment")
        verbose_name_plural = ("Employee Shift Assignments")

    def clean(self):

        if (
            self.effective_to
            and self.effective_to
            < self.effective_from
        ):
            raise ValidationError({
                "effective_to":
                "Effective to date cannot be before effective from date."
            })

        overlapping = (
            EmployeeShiftAssignment.objects.filter(
                employee=self.employee,
                is_active=True
            )
            .exclude(pk=self.pk)
        )

        if self.effective_to:
            overlapping = overlapping.filter(
                effective_from__lte=self.effective_to
            )

        if overlapping.exists():
            raise ValidationError({
                "employee":
                "An active shift assignment already exists for this employee."
            })

    def save(
        self,
        *args,
        **kwargs
    ):
        self.full_clean()
        super().save(
            *args,
            **kwargs
        )

    def __str__(self):
        return (
            f"{self.employee.employee_id}"
            f" - {self.shift.name}"
        )
class Attendance(models.Model):

    STATUS_CHOICES = [
        ("Present", "Present"),
        ("Absent", "Absent"),
        ("Half Day", "Half Day"),
        ("Late", "Late"),
        ("Work From Home", "Work From Home"),
        ("On Leave", "On Leave"),
        ("Holiday", "Holiday"),
        ("Weekend", "Weekend"),
        ("Missed Punch", "Missed Punch"),
    ]

    employee = models.ForeignKey(Employee,on_delete=models.PROTECT,related_name="attendance_records")
    shift = models.ForeignKey(Shift,on_delete=models.PROTECT,null=True,blank=True,related_name="attendance_records")
    attendance_date = models.DateField()
    check_in = models.DateTimeField(blank=True,null=True)
    check_out = models.DateTimeField(blank=True,null=True)
    worked_hours = models.DecimalField(max_digits=5,decimal_places=2,default=0)
    late_minutes = models.PositiveIntegerField(default=0)
    early_exit_minutes = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="Present")
    remarks = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            "-attendance_date"
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "employee",
                    "attendance_date"
                ],
                name="unique_employee_attendance_date"
            )
        ]
        verbose_name = "Attendance"
        verbose_name_plural = "Attendance"

    def clean(self):
        if self.employee and not self.employee.is_active:
            raise ValidationError({
                "employee": (
                    "Attendance cannot be recorded "
                    "for an inactive employee."
                )
            })

        if (
            self.employee
            and self.employee.status == "Resigned"
        ):
            raise ValidationError({
                "employee": (
                    "Attendance cannot be recorded "
                    "for a resigned employee."
                )
            })

        if self.shift and not self.shift.is_active:
            raise ValidationError({
                "shift": (
                    "Attendance cannot use an inactive shift."
                )
            })

        if (self.check_in and self.check_out and self.check_out < self.check_in):
            raise ValidationError({
                "check_out": (
                    "Check-out cannot be earlier "
                    "than check-in."
                )
            })

    def get_shift_start_datetime(self):
        """
        Returns the actual shift start datetime
        for this attendance date.
        """
        return timezone.make_aware(
            timezone.datetime.combine(
                self.attendance_date,
                self.shift.start_time
            )
        )

    def get_shift_end_datetime(self):
        """
        Returns the actual shift end datetime.

        For a night shift, the end datetime belongs
        to the following day.
        """
        shift_end = timezone.make_aware(
            timezone.datetime.combine(
                self.attendance_date,
                self.shift.end_time
            )
        )
        if self.shift.is_night_shift:
            shift_end += timezone.timedelta(days=1)
        return shift_end

    def calculate_worked_hours(self):
        if not self.check_in or not self.check_out:
            return 0
        seconds = (self.check_out - self.check_in).total_seconds()
        if seconds <= 0:
            return 0
        return round(seconds / 3600,2)

    def calculate_late_minutes(self):
        if not self.check_in:
            return 0
        shift_start = self.get_shift_start_datetime()
        grace_period = timezone.timedelta(minutes=self.shift.grace_time_minutes)
        allowed_check_in = (shift_start + grace_period)
        if self.check_in <= allowed_check_in:
            return 0
        late_seconds = (self.check_in - allowed_check_in).total_seconds()
        return max(0,int(late_seconds // 60))

    def calculate_early_exit_minutes(self):
        if not self.check_out:
            return 0
        shift_end = self.get_shift_end_datetime()
        if self.check_out >= shift_end:
            return 0
        early_seconds = (shift_end - self.check_out).total_seconds()
        return max(0,int(early_seconds // 60))

    def calculate_status(self):
        if self.status in [
            "Work From Home",
            "On Leave",
            "Holiday",
            "Weekend",
        ]:
            return self.status
        if not self.check_in and not self.check_out:
            return "Absent"
        if self.check_in and not self.check_out:
            return "Missed Punch"
        if not self.check_in and self.check_out:
            return "Missed Punch"
        worked_hours = self.calculate_worked_hours()
        if worked_hours <= 0:
            return "Absent"
        if (
            worked_hours
            < float(self.shift.minimum_half_day_hours)
        ):
            return "Absent"
        if (
            worked_hours
            < float(self.shift.minimum_full_day_hours)
        ):
            return "Half Day"
        if self.calculate_late_minutes() > 0:
            return "Late"
        return "Present"

    def save(self, *args, **kwargs):
        self.full_clean()
        self.worked_hours = (self.calculate_worked_hours())
        self.late_minutes = (self.calculate_late_minutes())
        self.early_exit_minutes = (self.calculate_early_exit_minutes())
        self.status = (self.calculate_status())
        super().save(
            *args,
            **kwargs
        )

    def __str__(self):
        return (
            f"{self.employee.employee_id}"
            f" - {self.attendance_date}"
        )

class AttendanceRegularization(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    attendance = models.OneToOneField(Attendance,on_delete=models.CASCADE,related_name="regularization")
    requested_check_in = models.DateTimeField(blank=True,null=True)
    requested_check_out = models.DateTimeField(blank=True,null=True)
    reason = models.TextField()
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="Pending")
    reviewed_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name="attendance_regularizations_reviewed")
    reviewed_at = models.DateTimeField(blank=True,null=True)
    reviewed_comments = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Attendance Regularization"
        verbose_name_plural = "Attendance Regularizations"

    def __str__(self):
        return (
            f"{self.attendance.employee.employee_id} - "
            f"{self.attendance.attendance_date}"
        )


class AttendanceAdjustment(models.Model):
    ADJUSTMENT_CHOICES = [
        ("Add", "Add"),
        ("Deduct", "Deduct"),
    ]

    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name="adjustments")
    adjustment_type = models.CharField(max_length=10,choices=ADJUSTMENT_CHOICES)
    minutes = models.PositiveIntegerField()
    reason = models.TextField()
    adjusted_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="attendance_adjustments")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Attendance Adjustment"
        verbose_name_plural = "Attendance Adjustments"

    def __str__(self):
        return (
            f"{self.attendance.employee.employee_id} "
            f"- {self.adjustment_type} "
            f"{self.minutes} mins"
        )


class AttendanceLog(models.Model):
    ACTION_CHOICES = [
        ("Created", "Created"),
        ("Updated", "Updated"),
        ("Regularized", "Regularized"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    attendance = models.ForeignKey(Attendance,on_delete=models.CASCADE,related_name="logs")
    action = models.CharField(max_length=20,choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="attendance_logs")
    remarks = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Attendance Log"
        verbose_name_plural = "Attendance Logs"

    def __str__(self):
        return (
            f"{self.attendance.employee.employee_id} - "
            f"{self.action}"
        )


class AttendanceAttachment(models.Model):
    attendance = models.ForeignKey(Attendance,on_delete=models.CASCADE,related_name="attachments")
    file = models.FileField(upload_to="attendance_attachments/")
    uploaded_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name="uploaded_attendance_attachments")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Attendance Attachment"
        verbose_name_plural = "Attendance Attachments"

    def __str__(self):
        return (
            f"{self.attendance.employee.employee_id} - "
            f"{self.file.name}"
        )

class Overtime(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    attendance = models.OneToOneField(Attendance,on_delete=models.CASCADE,related_name="overtime")
    overtime_minutes = models.PositiveIntegerField()
    reason = models.TextField(blank=True,null=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="Pending")
    approved_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name="approved_overtimes")
    approved_at = models.DateTimeField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Overtime"
        verbose_name_plural = "Overtime"

    def __str__(self):
        return (
            f"{self.attendance.employee.employee_id} - "
            f"{self.overtime_minutes} mins"
        )