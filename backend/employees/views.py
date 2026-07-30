from django.contrib.auth.models import User, Group
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .permissions import CanCreateEmployee
from .models import Employee
from .serializers import EmployeeCreateSerializer, EmployeeListSerializer, EmployeeAdminSerializer, EmployeeHRSerializer, EmployeeProjectManagerSerializer, EmployeeSelfSerializer


class EmployeeCreateView(APIView):
    permission_classes = [IsAuthenticated, CanCreateEmployee]

    def post(self, request):
        serializer = EmployeeCreateSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]
            role = serializer.validated_data["role"]
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    password=password
                )
                employee = serializer.save(user=user)
                group = Group.objects.get(name=role)
                user.groups.add(group)
            return Response(
                {
                    "message": "Employee and User created successfully",
                    "employee_id": employee.employee_id,
                    "username": user.username,
                    "role": role,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class EmployeeListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        if user.is_superuser:
            employees = Employee.objects.all()
            serializer = EmployeeAdminSerializer(
                employees,
                many=True
            )
        elif user.groups.filter(name="HR").exists():
            employees = Employee.objects.all()
            serializer = EmployeeHRSerializer(
                employees,
                many=True
            )
        else:
            employee = user.employee_profile
            serializer = EmployeeSelfSerializer(
                employee
            )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )