from django.db import transaction
from rest_framework import serializers
from .models import Project, ProjectTeam, Task, TaskAssignment


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "client",
            "project_manager",
            "description",
            "start_date",
            "end_date",
            "budget",
            "status",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        with transaction.atomic():
            project = Project.objects.create(
                **validated_data
            )

        return project

    def update(self, instance, validated_data):
        with transaction.atomic():
            project = super().update(
                instance,
                validated_data
            )

        return project


class ProjectTeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectTeam
        fields = [
            "id",
            "project",
            "employee",
            "role",
            "assigned_date",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "project",
            "assigned_date",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):

        project = self.context.get("project")

        if not project and self.instance:
            project = self.instance.project

        employee = attrs.get(
            "employee",
            self.instance.employee if self.instance else None
        )

        role = attrs.get(
            "role",
            self.instance.role if self.instance else None
        )

        if not project:
            raise serializers.ValidationError(
                {
                    "project": "Project is required."
                }
            )

        if not employee:
            raise serializers.ValidationError(
                {
                    "employee": "Employee is required."
                }
            )

        existing_team_member = ProjectTeam.objects.filter(
            project=project,
            employee=employee
        ).exclude(
            pk=self.instance.pk
        ).first() if self.instance else ProjectTeam.objects.filter(
            project=project,
            employee=employee
        ).first()

        if existing_team_member:
            raise serializers.ValidationError(
                {
                    "employee": (
                        "This employee is already assigned "
                        "to this project."
                    )
                }
            )

        if employee == project.project_manager:
            raise serializers.ValidationError(
                {
                    "employee": (
                        "The official project manager "
                        "cannot be added as a project team member "
                        "while they are the project manager."
                    )
                }
            )

        return attrs


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = [
            "id",
            "project",
            "title",
            "description",
            "priority",
            "status",
            "start_date",
            "due_date",
            "estimated_hours",
            "actual_hours",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "project",
            "created_at",
            "updated_at",
        ]


class TaskAssignmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskAssignment
        fields = [
            "id",
            "task",
            "employee",
            "assigned_by",
            "assigned_date",
            "assignment_status",
            "remarks",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "task",
            "assigned_by",
            "assigned_date",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):

        task = self.context.get("task")

        if not task and self.instance:
            task = self.instance.task

        employee = attrs.get(
            "employee",
            self.instance.employee if self.instance else None
        )

        if not task:
            raise serializers.ValidationError(
                {
                    "task": "Task is required."
                }
            )

        if not employee:
            raise serializers.ValidationError(
                {
                    "employee": "Employee is required."
                }
            )

        project = task.project

        is_project_team_member = ProjectTeam.objects.filter(
            project=project,
            employee=employee,
            is_active=True
        ).exists()

        if not is_project_team_member:
            raise serializers.ValidationError(
                {
                    "employee": (
                        "This employee is not an active member "
                        "of the project team."
                    )
                }
            )

        existing_assignment = TaskAssignment.objects.filter(
            task=task,
            employee=employee
        ).exclude(
            pk=self.instance.pk
        ).first() if self.instance else TaskAssignment.objects.filter(
            task=task,
            employee=employee
        ).first()

        if existing_assignment:
            raise serializers.ValidationError(
                {
                    "employee": (
                        "This employee is already assigned "
                        "to this task."
                    )
                }
            )

        return attrs