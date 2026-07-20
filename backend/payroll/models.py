from django.db import models
from employees.models import Employee
# Create your models here.

class SalaryStructure(models.Model):

    employee = models.ForeignKey(Employee,on_delete=models.PROTECT,related_name="salary_structures")
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    hra = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    allowance = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    bonus = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    deduction = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    effective_from = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-effective_from"]

    def __str__(self):
        return f"{self.employee} - {self.effective_from}"
    

class Payroll(models.Model):

    STATUS_CHOICES = [
        ("Draft", "Draft"),
        ("Processed", "Processed"),
        ("Paid", "Paid"),
    ]

    employee = models.ForeignKey(Employee,on_delete=models.PROTECT,related_name="payrolls")
    salary_structure = models.ForeignKey(SalaryStructure,on_delete=models.PROTECT,related_name="payrolls")
    month = models.PositiveSmallIntegerField()
    year = models.PositiveSmallIntegerField()
    gross_salary = models.DecimalField(max_digits=10,decimal_places=2)
    total_deduction = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    net_salary = models.DecimalField(max_digits=10,decimal_places=2)
    payment_date = models.DateField(blank=True,null=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="Draft")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-year", "-month"]

    def __str__(self):
        return f"{self.employee} - {self.month}/{self.year}"
    

class PayrollItem(models.Model):

    TYPE_CHOICES = [
        ("Earning", "Earning"),
        ("Deduction", "Deduction"),
    ]

    payroll = models.ForeignKey(
        Payroll,
        on_delete=models.CASCADE,
        related_name="payroll_items"
    )

    component_name = models.CharField(max_length=100)
    component_type = models.CharField(max_length=20,choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.component_name} - {self.amount}"
    
class Payslip(models.Model):

    payroll = models.OneToOneField(Payroll,on_delete=models.CASCADE,related_name="payslip")
    generated_date = models.DateField(auto_now_add=True)
    pdf_file = models.FileField(upload_to="payslips/",blank=True,null=True)
    remarks = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payslip - {self.payroll}"