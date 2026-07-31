from django.db import transaction
from rest_framework import serializers
from .models import Project, ProjectTeam


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