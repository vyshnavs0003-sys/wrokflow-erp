from django.db import models

# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to="company/logo/",blank=True, null=True)
    is_active= models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name ="Company"
        verbose_name_plural="Companies"

    def __str__(self):
        return self.name
    
class Department(models.Model):
    company = models.ForeignKey(Company,on_delete=models.PROTECT, related_name="departments")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering =["name"]
        verbose_name = "Department"
        verbose_name_plural = "Departments"

def __str__(self):
    return self.name        

class Designation(models.Model):
    department = models.ForeignKey(Department,on_delete=models.PROTECT,related_name="designations")
    name = models.CharField(max_length=100)
    descripion = models.TextField(blank=True,null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["department","name"]
        unique_together = ("department","name")
        verbose_name = "Designation"
        verbose_name_plural = "Designations"

    def __str__(self):
        return f"{self.name} ({self.department.name})"    

class OfficeTiming(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,related_name="office_timings")
    shift_name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField
    grace_minutes = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["shift_name"]
        verbose_name = "Office Timing"
        verbose_name_plural = "Office Timings"
        unique_together = ("company", "shift_name")

    def __str__(self):
        return f"{self.company.name} - {self.shift_name}"    