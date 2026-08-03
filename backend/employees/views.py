from django.contrib.auth.models import User, Group
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .permissions import CanCreateEmployee
from .models import Employee
from .serializers import EmployeeCreateSerializer, EmployeeAdminSerializer, EmployeeHRSerializer, EmployeeSelfSerializer,EmployeeUpdateSerializer

class EmployeeCreateView(APIView):
    permission_classes = [IsAuthenticated, CanCreateEmployee]

    def post(self, request):
        serializer = EmployeeCreateSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]
            role = serializer.validated_data["role"]

            try:
                group = Group.objects.get(name=role)
            except Group.DoesNotExist:
                return Response(
                    {
                        "detail": f"The {role} group does not exist."
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    password=password
                )

                employee = serializer.save(user=user)

                user.groups.add(group)

            return Response(
                {
                    "message": "Employee and User created successfully",
                    "employee_id": employee.employee_id,
                    "username": user.username,
                    "role": role,
                    "department": employee.department.id,
                    "team": employee.team.id if employee.team else None,
                    "designation": employee.designation.id,
                    "reporting_manager": employee.reporting_manager.id if employee.reporting_manager else None,
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


class EmployeeDetailUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, employee_id):
        try:
            return Employee.objects.get(pk=employee_id)
        except Employee.DoesNotExist:
            return None

    def get(self, request, employee_id):
        employee = self.get_object(employee_id)

        if not employee:
            return Response(
                {
                    "detail": "Employee not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if request.user.is_superuser:
            serializer = EmployeeAdminSerializer(employee)

        elif request.user.groups.filter(name="HR").exists():
            serializer = EmployeeHRSerializer(employee)

        else:
            if request.user.employee_profile != employee:
                return Response(
                    {
                        "detail": "You do not have permission to view this employee."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = EmployeeSelfSerializer(employee)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request, employee_id):
        employee = self.get_object(employee_id)

        if not employee:
            return Response(
                {
                    "detail": "Employee not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if not request.user.is_superuser and not request.user.groups.filter(name="HR").exists():
            return Response(
                {
                    "detail": "You do not have permission to update this employee."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = EmployeeUpdateSerializer(
            employee,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            employee = serializer.save()

            return Response(
                {
                    "message": "Employee updated successfully.",
                    "employee_id": employee.employee_id,
                    "department": employee.department.id,
                    "team": employee.team.id if employee.team else None,
                    "designation": employee.designation.id,
                    "reporting_manager": employee.reporting_manager.id if employee.reporting_manager else None,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )