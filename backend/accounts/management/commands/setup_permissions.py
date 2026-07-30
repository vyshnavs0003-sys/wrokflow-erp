from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Set up permissions for ERP roles"

    def handle(self, *args, **kwargs):

        role_permissions = {
            "Employee": [
                ("employees", "employee", ["view"]),

                ("attendance", "attendance", ["view"]),

                ("leave_management", "leaverequest", ["add", "view"]),
                ("leave_management", "leavetype", ["view"]),

                ("payroll", "payslip", ["view"]),

                ("projects", "project", ["view"]),
                ("projects", "projectteam", ["view"]),
                ("projects", "task", ["view"]),
                ("projects", "taskassignment", ["view"]),

                ("communication", "announcement", ["view"]),
                ("communication", "notification", ["view"]),
            ],

            "HR": [
                ("employees", "employee", ["add", "change", "view"]),

                ("attendance", "attendance", ["add", "change", "view"]),

                ("leave_management", "leaverequest", ["change", "view"]),
                ("leave_management", "leavetype", ["add", "change", "view"]),

                ("payroll", "salarystructure", ["add", "change", "view"]),
                ("payroll", "payroll", ["add", "change", "view"]),
                ("payroll", "payrollitem", ["add", "change", "view"]),
                ("payroll", "payslip", ["add", "change", "view"]),

                ("communication", "announcement", ["add", "change", "view"]),
                ("communication", "notification", ["add", "change", "view"]),
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