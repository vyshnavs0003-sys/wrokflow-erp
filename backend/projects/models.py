from django.db import models
from employees.models import Employee

# Create your models here.
class Client(models.Model):
    name = models.CharField(max_length=150, unique=True)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    website = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return self.name
    

class Project(models.Model):

    STATUS_CHOICES = [
        ("Planning", "Planning"),
        ("In Progress", "In Progress"),
        ("On Hold", "On Hold"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]

    name = models.CharField(max_length=200)
    client = models.ForeignKey(Client,on_delete=models.PROTECT,related_name="projects")
    project_manager = models.ForeignKey(Employee,on_delete=models.PROTECT,related_name="managed_projects")
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    budget = models.DecimalField(max_digits=12,decimal_places=2,blank=True,null=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="Planning")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name    
    

class ProjectTeam(models.Model):

    ROLE_CHOICES = [
        ("Backend Developer", "Backend Developer"),
        ("Frontend Developer", "Frontend Developer"),
        ("Full Stack Developer", "Full Stack Developer"),
        ("UI/UX Designer", "UI/UX Designer"),
        ("QA Engineer", "QA Engineer"),
        ("DevOps Engineer", "DevOps Engineer"),
    ]

    project = models.ForeignKey(Project,on_delete=models.CASCADE,related_name="team_members")
    employee = models.ForeignKey(Employee,on_delete=models.PROTECT,related_name="project_assignments")
    role = models.CharField(max_length=50,choices=ROLE_CHOICES)
    assigned_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["project", "employee"]
        constraints = [ models.UniqueConstraint(fields=["project", "employee"],name="unique_project_employee")]

    def __str__(self):
        return f"{self.employee} - {self.project}"
    

class Task(models.Model):

    PRIORITY_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
        ("Critical", "Critical"),
    ]

    STATUS_CHOICES = [
        ("To Do", "To Do"),
        ("In Progress", "In Progress"),
        ("In Review", "In Review"),
        ("Completed", "Completed"),
        ("Blocked", "Blocked"),
    ]

    project = models.ForeignKey(Project,on_delete=models.CASCADE,related_name="tasks")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=20,choices=PRIORITY_CHOICES,default="Medium")
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="To Do")
    start_date = models.DateField()
    due_date = models.DateField()
    estimated_hours = models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True)
    actual_hours = models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_date"]

    def __str__(self):
        return self.title    
    

class TaskAssignment(models.Model):

    ASSIGNMENT_STATUS_CHOICES = [
        ("Assigned", "Assigned"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),
    ]

    task = models.ForeignKey(Task,on_delete=models.CASCADE,related_name="assignments")
    employee = models.ForeignKey(Employee,on_delete=models.PROTECT,related_name="task_assignments")
    assigned_by = models.ForeignKey(Employee,on_delete=models.PROTECT,related_name="assigned_tasks")
    assigned_date = models.DateField(auto_now_add=True)
    assignment_status = models.CharField(max_length=20,choices=ASSIGNMENT_STATUS_CHOICES,default="Assigned")
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-assigned_date"]

    def __str__(self):
        return f"{self.task} - {self.employee}"