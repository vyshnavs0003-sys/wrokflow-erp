from django.db import models 
from django.contrib.auth.models import User 
from django.core.exceptions import ValidationError 
from django.utils import timezone 
from employees.models import Employee 
 
# Create your models here. 
 
class LeaveType(models.Model): 
    name = models.CharField(max_length=100,unique=True) 
    description = models.TextField(blank=True,null=True) 
    is_paid = models.BooleanField(default=True) 
    annual_quota = models.PositiveIntegerField(default=0) 
    requires_approval = models.BooleanField(default=True) 
    requires_document = models.BooleanField(default=False) 
    max_consecutive_days = models.PositiveIntegerField(blank=True,null=True) 
    is_active = models.BooleanField(default=True) 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 
 
    class Meta: 
        ordering = ["name"] 
        verbose_name = "Leave Type" 
        verbose_name_plural = "Leave Types" 
 
    def __str__(self): 
        return self.name 
 
class LeavePolicy(models.Model): 
    leave_type = models.OneToOneField(LeaveType,on_delete=models.PROTECT,related_name="policy") 
    carry_forward_allowed = models.BooleanField(default=False) 
    max_carry_forward_days = models.PositiveIntegerField(default=0) 
    carry_forward_expiry_months = models.PositiveIntegerField(blank=True,null=True) 
    encashment_allowed = models.BooleanField(default=False) 
    max_encashment_days = models.PositiveIntegerField(default=0) 
    is_active = models.BooleanField(default=True) 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 
 
    class Meta: 
        ordering = ["leave_type__name"] 
        verbose_name = "Leave Policy" 
        verbose_name_plural = "Leave Policies" 
 
    def __str__(self): 
        return f"{self.leave_type.name} Policy" 
 
class LeaveAllocation(models.Model): 
    employee = models.ForeignKey(Employee,on_delete=models.PROTECT,related_name="leave_allocations") 
    leave_type = models.ForeignKey(LeaveType,on_delete=models.PROTECT,related_name="allocations") 
    year = models.PositiveIntegerField() 
    allocated_days = models.PositiveIntegerField(default=0) 
    carry_forward_days = models.PositiveIntegerField(default=0) 
    adjustment_days = models.IntegerField(default=0) 
    expiry_date = models.DateField(blank=True,null=True) 
    is_active = models.BooleanField(default=True) 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 
 
    class Meta: 
        ordering = ["-year","employee__employee_id"] 
        unique_together = ("employee","leave_type","year") 
        verbose_name = "Leave Allocation" 
        verbose_name_plural = "Leave Allocations" 
 
    @property 
    def used_days(self): 
        return LeaveRequest.objects.filter( 
            employee=self.employee, 
            leave_type=self.leave_type, 
            status="Approved", 
            start_date__year=self.year 
        ).aggregate( 
            total=models.Sum("total_days") 
        )["total"] or 0 
 
    @property 
    def pending_days(self): 
        return LeaveRequest.objects.filter( 
            employee=self.employee, 
            leave_type=self.leave_type, 
            status="Pending", 
            start_date__year=self.year 
        ).aggregate( 
            total=models.Sum("total_days") 
        )["total"] or 0 
 
    @property 
    def remaining_days(self): 
        return self.allocated_days + self.carry_forward_days + self.adjustment_days - self.used_days 
 
    def __str__(self): 
        return f"{self.employee.employee_id} - {self.leave_type.name} - {self.year}" 
 
class Holiday(models.Model): 
    name = models.CharField(max_length=150) 
    date = models.DateField() 
    description = models.TextField(blank=True,null=True) 
    is_optional = models.BooleanField(default=False) 
    is_active = models.BooleanField(default=True) 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 
 
    class Meta: 
        ordering = ["date"] 
        unique_together = ("name","date") 
        verbose_name = "Holiday" 
        verbose_name_plural = "Holidays" 
 
    def __str__(self): 
        return f"{self.name} - {self.date}" 
 
class LeaveRequest(models.Model): 
    STATUS_CHOICES = [ 
    ("Pending","Pending"), 
    ("Approved","Approved"), 
    ("Rejected","Rejected"), 
    ("Cancelled","Cancelled"), 
    ] 
 
    employee = models.ForeignKey(Employee,on_delete=models.PROTECT,related_name="leave_requests") 
    leave_type = models.ForeignKey(LeaveType,on_delete=models.PROTECT,related_name="leave_requests") 
    start_date = models.DateField() 
    end_date = models.DateField() 
    total_days = models.PositiveIntegerField(default=0) 
    reason = models.TextField() 
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="Pending") 
    reviewed_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name="reviewed_leave_requests") 
    reviewed_at = models.DateTimeField(blank=True,null=True) 
    reviewed_comments = models.TextField(blank=True,null=True) 
    cancelled_at = models.DateTimeField(blank=True,null=True) 
    cancellation_reason = models.TextField(blank=True,null=True) 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 
 
    class Meta: 
        ordering = ["-created_at"] 
        verbose_name = "Leave Request" 
        verbose_name_plural = "Leave Requests" 
 
    def clean(self): 
        if self.end_date < self.start_date: 
            raise ValidationError({ 
                "end_date": "End date must be greater than or equal to start date." 
            }) 
 
        if self.employee and not self.employee.is_active: 
            raise ValidationError({ 
                "employee": "An inactive employee cannot request leave." 
            }) 
 
        if self.employee and self.employee.status == "Resigned": 
            raise ValidationError({ 
                "employee": "A resigned employee cannot request leave." 
            }) 
 
        if self.leave_type and not self.leave_type.is_active: 
            raise ValidationError({ 
                "leave_type": "The selected leave type is inactive." 
            }) 
 
        if self.employee and self.leave_type: 
            overlapping_requests = LeaveRequest.objects.filter( 
                employee=self.employee, 
                status__in=["Pending","Approved"], 
                start_date__lte=self.end_date, 
                end_date__gte=self.start_date 
            ).exclude(pk=self.pk) 
 
            if overlapping_requests.exists(): 
                raise ValidationError({ 
                    "start_date": "This leave period overlaps with an existing leave request." 
                }) 
 
    def save(self,*args,**kwargs): 
        self.total_days = self.calculate_total_days() 
        self.full_clean() 
        super().save(*args,**kwargs) 
 
    def calculate_total_days(self): 
        if not self.start_date or not self.end_date: 
            return 0 
 
        total_days = 0 
        current_date = self.start_date 
 
        holidays = set( 
            Holiday.objects.filter( 
                date__range=[self.start_date,self.end_date], 
                is_optional=False, 
                is_active=True 
            ).values_list("date",flat=True) 
        ) 
 
        while current_date <= self.end_date: 
            if current_date.weekday() < 5 and current_date not in holidays: 
                total_days += 1 
 
            current_date += timezone.timedelta(days=1) 
 
        return total_days 
 
    def __str__(self): 
        return f"{self.employee.employee_id} - {self.leave_type.name} - {self.status}"


class LeaveAttachment(models.Model):
    leave_request = models.ForeignKey(LeaveRequest,on_delete=models.CASCADE,related_name="attachments")
    file = models.FileField(upload_to="leave_attachments/")
    uploaded_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name="uploaded_leave_attachments")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Leave Attachment"
        verbose_name_plural = "Leave Attachments"

    def __str__(self):
        return f"{self.leave_request.employee.employee_id} - {self.file.name}"