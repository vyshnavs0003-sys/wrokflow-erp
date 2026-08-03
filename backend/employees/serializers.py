from rest_framework import serializers
from .models import Employee

class EmployeeCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(
    choices=["Employee", "HR"],
    write_only=True
    )

    class Meta:
        model = Employee
        fields = [
            "username",
            "password",
            "role",
            "employee_id",
            "department",
            "team",
            "designation",
            "reporting_manager",
            "office_timing",
            "phone",
            "profile_photo",
            "gender",
            "joining_date",
            "employment_type",
            "address",
            "emergency_contact",
            "status",
            "is_active",
        ]

    def validate(self, attrs):
        department = attrs.get("department")
        team = attrs.get("team")
        designation = attrs.get("designation")
        reporting_manager = attrs.get("reporting_manager")

        if not department:
            raise serializers.ValidationError({
                "department": "Department is required."
            })

        if team and team.department_id != department.id:
            raise serializers.ValidationError({
                "team": "The selected team must belong to the selected department."
            })

        if designation and designation.department_id != department.id:
            raise serializers.ValidationError({
                "designation": "The selected designation must belong to the selected department."
            })

        if reporting_manager:
            if not reporting_manager.is_active or reporting_manager.status == "Resigned":
                raise serializers.ValidationError({
                    "reporting_manager": "The selected reporting manager must be an active employee."
                })

            if reporting_manager.department.company_id != department.company_id:
                raise serializers.ValidationError({
                    "reporting_manager": "The reporting manager must belong to the same company."
                })

        return attrs

    def create(self, validated_data):
        validated_data.pop("username")
        validated_data.pop("password")
        validated_data.pop("role")

        return Employee.objects.create(**validated_data)

class EmployeeListSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source="user.username")
    full_name = serializers.CharField(source="user.get_full_name")

    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "username",
            "full_name",
            "department",
            "team",
            "designation",
            "reporting_manager",
            "phone",
            "gender",
            "joining_date",
            "employment_type",
            "status",
        ]

class EmployeeAdminSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source="user.username")
    full_name = serializers.CharField(source="user.get_full_name")

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_id",
            "username",
            "full_name",
            "department",
            "team",
            "designation",
            "reporting_manager",
            "office_timing",
            "phone",
            "profile_photo",
            "gender",
            "joining_date",
            "employment_type",
            "address",
            "emergency_contact",
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

class EmployeeHRSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source="user.username")
    full_name = serializers.CharField(source="user.get_full_name")

    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "username",
            "full_name",
            "department",
            "team",
            "designation",
            "reporting_manager",
            "office_timing",
            "phone",
            "profile_photo",
            "gender",
            "joining_date",
            "employment_type",
            "address",
            "emergency_contact",
            "status",
            "is_active",
        ]

class EmployeeProjectManagerSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source="user.username")
    full_name = serializers.CharField(source="user.get_full_name")

    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "username",
            "full_name",
            "department",
            "team",
            "designation",
            "reporting_manager",
            "profile_photo",
            "phone",
            "status",
        ]

class EmployeeSelfSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source="user.username")
    full_name = serializers.CharField(source="user.get_full_name")

    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "username",
            "full_name",
            "department",
            "team",
            "designation",
            "reporting_manager",
            "office_timing",
            "phone",
            "profile_photo",
            "gender",
            "joining_date",
            "employment_type",
            "address",
            "emergency_contact",
            "status",
        ]

class EmployeeUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = [
            "department",
            "team",
            "designation",
            "reporting_manager",
            "office_timing",
            "phone",
            "profile_photo",
            "gender",
            "joining_date",
            "employment_type",
            "address",
            "emergency_contact",
            "status",
            "is_active",
        ]

    def validate(self, attrs):
        employee = self.instance

        department = attrs.get("department", employee.department)
        team = attrs.get("team", employee.team)
        designation = attrs.get("designation", employee.designation)
        reporting_manager = attrs.get(
            "reporting_manager",
            employee.reporting_manager
        )

        if team and team.department_id != department.id:
            raise serializers.ValidationError({
                "team": "The selected team must belong to the selected department."
            })

        if designation and designation.department_id != department.id:
            raise serializers.ValidationError({
                "designation": "The selected designation must belong to the selected department."
            })

        if reporting_manager:
            if reporting_manager == employee:
                raise serializers.ValidationError({
                    "reporting_manager": "An employee cannot be their own reporting manager."
                })

            if not reporting_manager.is_active or reporting_manager.status == "Resigned":
                raise serializers.ValidationError({
                    "reporting_manager": "The selected reporting manager must be an active employee."
                })

            if reporting_manager.department.company_id != department.company_id:
                raise serializers.ValidationError({
                    "reporting_manager": "The reporting manager must belong to the same company."
                })

        return attrs