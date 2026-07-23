from rest_framework import serializers
from .models import Employee


class EmployeeCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(write_only=True)

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