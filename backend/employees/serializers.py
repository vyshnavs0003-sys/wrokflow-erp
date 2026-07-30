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
            "designation",
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
            "designation",
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
            "employee_id",
            "username",
            "full_name",
            "department",
            "designation",
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
            "designation",
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
            "designation",
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
            "designation",
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