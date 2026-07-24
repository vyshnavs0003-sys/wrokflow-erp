from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Set up permissions for ERP roles"

    def handle(self, *args, **kwargs):

        role_permissions = {
            "Employee": [
                # Employee
                ("employees", "employee", ["view"]),

                # Attendance
                ("attendance", "attendance", ["view"]),

                # Leave Management
                ("leave_management", "leaverequest", ["add", "view"]),
                ("leave_management", "leavetype", ["view"]),

                # Payroll
                ("payroll", "payslip", ["view"]),

                # Projects
                ("projects", "project", ["view"]),
                ("projects", "projectteam", ["view"]),
                ("projects", "task", ["view"]),
                ("projects", "taskassignment", ["view"]),

                # Communication
                ("communication", "announcement", ["view"]),
                ("communication", "notification", ["view"]),
            ],

            "HR": [
                # Employee Management
                ("employees", "employee", ["add", "change", "view"]),

                # Attendance
                ("attendance", "attendance", ["add", "change", "view"]),

                # Leave Management
                ("leave_management", "leaverequest", ["change", "view"]),
                ("leave_management", "leavetype", ["add", "change", "view"]),

                # Payroll
                ("payroll", "salarystructure", ["add", "change", "view"]),
                ("payroll", "payroll", ["add", "change", "view"]),
                ("payroll", "payrollitem", ["add", "change", "view"]),
                ("payroll", "payslip", ["add", "change", "view"]),

                # Communication
                ("communication", "announcement", ["add", "change", "view"]),
                ("communication", "notification", ["add", "change", "view"]),
            ],

            "Project Manager": [
                # Projects
                ("projects", "project", ["add", "change", "view"]),
                ("projects", "client", ["add", "change", "view"]),
                ("projects", "projectteam", ["add", "change", "view"]),
                ("projects", "task", ["add", "change", "view"]),
                ("projects", "taskassignment", ["add", "change", "view"]),

                # Communication
                ("communication", "announcement", ["view"]),
                ("communication", "notification", ["view"]),
            ],
        }

        for role, permissions in role_permissions.items():

            group, created = Group.objects.get_or_create(name=role)

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created group: {role}"
                    )
                )

            for app_label, model_name, actions in permissions:

                for action in actions:

                    codename = f"{action}_{model_name}"

                    try:
                        permission = Permission.objects.get(
                            content_type__app_label=app_label,
                            codename=codename
                        )

                        group.permissions.add(permission)

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Added {codename} → {role}"
                            )
                        )

                    except Permission.DoesNotExist:

                        self.stdout.write(
                            self.style.WARNING(
                                f"Permission not found: "
                                f"{app_label} | {codename}"
                            )
                        )

        self.stdout.write(
            self.style.SUCCESS(
                "Role permissions setup completed successfully."
            )
        )