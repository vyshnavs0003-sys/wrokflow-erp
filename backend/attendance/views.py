from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import (
    Shift,
    EmployeeShiftAssignment,
    Attendance,
    AttendanceRegularization,
    AttendanceAdjustment,
    AttendanceLog,
    AttendanceAttachment,
    Overtime,
)
from .serializers import (
    ShiftSerializer,
    EmployeeShiftAssignmentSerializer,
    AttendanceSerializer,
    AttendanceRegularizationSerializer,
    AttendanceAdjustmentSerializer,
    AttendanceLogSerializer,
    AttendanceAttachmentSerializer,
    OvertimeSerializer,
)


def is_super_admin(user):
    return user.is_authenticated and user.is_superuser


def is_hr(user):
    return (
        user.is_authenticated
        and user.groups.filter(name="HR").exists()
    )


def has_employee_profile(user):
    return hasattr(user, "employee_profile")


def is_hr_or_super_admin(user):
    return is_super_admin(user) or is_hr(user)



class ShiftListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        shifts = Shift.objects.filter(is_active=True)
        serializer = ShiftSerializer(shifts,many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        if not is_hr_or_super_admin(request.user):
            return Response(
                {
                    "detail": (
                        "You do not have permission "
                        "to create a shift."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = ShiftSerializer(data=request.data)
        if serializer.is_valid():
            shift = serializer.save()
            return Response(
                {
                    "message": "Shift created successfully.",
                    "id": shift.id,
                    "name": shift.name,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ShiftDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Shift.objects.get(pk=pk)
        except Shift.DoesNotExist:
            return None

    def get(self, request, pk):
        shift = self.get_object(pk)
        if not shift:
            return Response(
                {
                    "detail": "Shift not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ShiftSerializer(shift)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request, pk):
        if not is_hr_or_super_admin(request.user):
            return Response(
                {
                    "detail": (
                        "You do not have permission "
                        "to update a shift."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )
        shift = self.get_object(pk)
        if not shift:
            return Response(
                {
                    "detail": "Shift not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ShiftSerializer(
            shift,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Shift updated successfully."
                },
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        if not is_hr_or_super_admin(request.user):
            return Response(
                {
                    "detail": (
                        "You do not have permission "
                        "to deactivate a shift."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )
        shift = self.get_object(pk)
        if not shift:
            return Response(
                {
                    "detail": "Shift not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        shift.is_active = False
        shift.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )
        return Response(
            {
                "message": "Shift deactivated successfully."
            },
            status=status.HTTP_200_OK
        )


class EmployeeShiftAssignmentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if is_hr_or_super_admin(request.user):
            assignments = (
                EmployeeShiftAssignment.objects
                .select_related(
                    "employee",
                    "shift",
                )
                .all()
            )
        elif has_employee_profile(request.user):
            assignments = (
                EmployeeShiftAssignment.objects
                .select_related(
                    "employee",
                    "shift",
                )
                .filter(
                    employee=request.user.employee_profile
                )
            )
        else:
            return Response(
                {
                    "detail": "Employee profile not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = EmployeeShiftAssignmentSerializer(assignments,many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        if not is_hr_or_super_admin(request.user):
            return Response(
                {
                    "detail": (
                        "You do not have permission "
                        "to assign shifts."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = EmployeeShiftAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            assignment = serializer.save()
            return Response(
                {
                    "message": (
                        "Employee shift assigned successfully."
                    ),
                    "id": assignment.id,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class EmployeeShiftAssignmentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return EmployeeShiftAssignment.objects.select_related(
                "employee",
                "shift",
            ).get(pk=pk)
        except EmployeeShiftAssignment.DoesNotExist:
            return None

    def get(self, request, pk):
        assignment = self.get_object(pk)
        if not assignment:
            return Response(
                {
                    "detail": "Shift assignment not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        if (
            not is_hr_or_super_admin(request.user)
            and (
                not has_employee_profile(request.user)
                or assignment.employee
                != request.user.employee_profile
            )
        ):
            return Response(
                {
                    "detail": (
                        "You do not have permission "
                        "to view this shift assignment."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = EmployeeShiftAssignmentSerializer(assignment)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request, pk):
        if not is_hr_or_super_admin(request.user):
            return Response(
                {
                    "detail": (
                        "You do not have permission "
                        "to update a shift assignment."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )
        assignment = self.get_object(pk)
        if not assignment:
            return Response(
                {
                    "detail": "Shift assignment not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = EmployeeShiftAssignmentSerializer(assignment,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": (
                        "Shift assignment updated successfully."
                    )
                },
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        if not is_hr_or_super_admin(request.user):
            return Response(
                {
                    "detail": (
                        "You do not have permission "
                        "to deactivate this shift assignment."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )
        assignment = self.get_object(pk)
        if not assignment:
            return Response(
                {
                    "detail": "Shift assignment not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        assignment.is_active = False
        assignment.save(update_fields=["is_active","updated_at"])
        return Response(
            {
                "message": (
                    "Shift assignment deactivated successfully."
                )
            },
            status=status.HTTP_200_OK
        )


class AttendanceListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        queryset = Attendance.objects.select_related(
            "employee",
            "shift",
        )
        if is_hr_or_super_admin(request.user):
            attendance_records = queryset.all()

        elif has_employee_profile(request.user):
            attendance_records = queryset.filter(
                employee=request.user.employee_profile
            )
        else:
            return Response(
                {
                    "detail": "Employee profile not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = AttendanceSerializer(attendance_records,many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        if not (
            is_hr_or_super_admin(request.user)
            or has_employee_profile(request.user)
        ):
            return Response(
                {
                    "detail": "Employee profile not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = AttendanceSerializer(data=request.data)
        if serializer.is_valid():
            attendance = serializer.save()
            AttendanceLog.objects.create(
                attendance=attendance,
                action="Created",
                performed_by=request.user,
                remarks="Attendance record created.",
            )
            return Response(
                {
                    "message": (
                        "Attendance recorded successfully."
                    ),
                    "id": attendance.id,
                    "worked_hours": attendance.worked_hours,
                    "status": attendance.status,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class AttendanceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Attendance.objects.select_related(
                "employee",
                "shift",
            ).get(pk=pk)
        except Attendance.DoesNotExist:
            return None

    def has_access(self, request, attendance):
        if is_hr_or_super_admin(request.user):
            return True
        if not has_employee_profile(request.user):
            return False
        employee = request.user.employee_profile
        if attendance.employee == employee:
            return True
        if attendance.employee.reporting_manager == employee:
            return True
        return False

    def get(self, request, pk):
        attendance = self.get_object(pk)
        if not attendance:
            return Response(
                {
                    "detail": "Attendance record not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        if not self.has_access(request, attendance):
            return Response(
                {
                    "detail": (
                        "You do not have permission "
                        "to view this attendance record."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = AttendanceSerializer(attendance)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
    
    def patch(self, request, pk):
        attendance = self.get_object(pk)
        if not attendance:
            return Response(
                {
                    "detail": "Attendance record not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        if not is_hr_or_super_admin(request.user):
            return Response(
                {
                    "detail": (
                        "Only HR or Super Admin can "
                        "update attendance directly."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = AttendanceSerializer(attendance,data=request.data,partial=True)
        if serializer.is_valid():
            with transaction.atomic():
                attendance = serializer.save()
                AttendanceLog.objects.create(
                    attendance=attendance,
                    action="Updated",
                    performed_by=request.user,
                    remarks="Attendance record updated.",
                )
            return Response(
                {
                    "message": (
                        "Attendance updated successfully."
                    )
                },
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class AttendanceRegularizationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = (
            AttendanceRegularization.objects
            .select_related(
                "attendance",
                "attendance__employee",
                "reviewed_by",
            )
        )
        if is_hr_or_super_admin(request.user):
            regularizations = queryset.all()
        elif has_employee_profile(request.user):
            regularizations = queryset.filter(
                attendance__employee=
                request.user.employee_profile
            )
        else:
            return Response(
                {
                    "detail": "Employee profile not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = AttendanceRegularizationSerializer(regularizations,many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        if not has_employee_profile(request.user):
            return Response(
                {
                    "detail": "Employee profile not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = AttendanceRegularizationSerializer(data=request.data)
        if serializer.is_valid():
            attendance = serializer.validated_data[
                "attendance"
            ]
            if (
                attendance.employee
                != request.user.employee_profile
                and not is_hr_or_super_admin(request.user)
            ):
                return Response(
                    {
                        "detail": (
                            "You can only regularize "
                            "your own attendance."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            regularization = serializer.save()
            AttendanceLog.objects.create(
                attendance=attendance,
                action="Regularized",
                performed_by=request.user,
                remarks=(
                    "Attendance regularization "
                    "request submitted."
                ),
            )
            return Response(
                {
                    "message": (
                        "Attendance regularization "
                        "submitted successfully."
                    ),
                    "id": regularization.id,
                    "status": regularization.status,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
class AttendanceRegularizationDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return (
                AttendanceRegularization.objects
                .select_related(
                    "attendance",
                    "attendance__employee",
                    "reviewed_by",
                )
                .get(pk=pk)
            )
        except AttendanceRegularization.DoesNotExist:
            return None

    def get(self, request, pk):
        regularization = self.get_object(pk)
        if not regularization:
            return Response(
                {
                    "detail": (
                        "Attendance regularization "
                        "not found."
                    )
                },
                status=status.HTTP_404_NOT_FOUND
            )
        if is_hr_or_super_admin(request.user):
            has_access = True
        elif has_employee_profile(request.user):
            has_access = (
                regularization.attendance.employee
                == request.user.employee_profile
            )
        else:
            has_access = False
        if not has_access:
            return Response(
                {
                    "detail": (
                        "You do not have permission "
                        "to view this regularization request."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = AttendanceRegularizationSerializer(
            regularization
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class AttendanceRegularizationReviewView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, pk):
        try:
            regularization = (
                AttendanceRegularization.objects
                .select_related(
                    "attendance",
                    "attendance__employee",
                )
                .get(pk=pk)
            )
        except AttendanceRegularization.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Attendance regularization "
                        "not found."
                    )
                },
                status=status.HTTP_404_NOT_FOUND
            )
        if regularization.status != "Pending":
            return Response(
                {
                    "detail": (
                        "Only pending regularization "
                        "requests can be reviewed."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        employee = regularization.attendance.employee
        is_manager = (
            has_employee_profile(request.user)
            and employee.reporting_manager
            == request.user.employee_profile
        )
        if not (
            is_hr_or_super_admin(request.user)
            or is_manager
        ):
            return Response(
                {
                    "detail": (
                        "You do not have permission "
                        "to review this request."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )
        action = request.data.get("action")
        comments = request.data.get(
            "reviewed_comments"
        )
        if action not in [
            "Approved",
            "Rejected",
        ]:
            return Response(
                {
                    "action": (
                        "Action must be either "
                        "'Approved' or 'Rejected'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        with transaction.atomic():
            regularization.status = action
            regularization.reviewed_by = request.user
            regularization.reviewed_at = timezone.now()
            regularization.reviewed_comments = comments
            regularization.save(
                update_fields=[
                    "status",
                    "reviewed_by",
                    "reviewed_at",
                    "reviewed_comments",
                    "updated_at",
                ]
            )
            if action == "Approved":
                attendance = regularization.attendance
                attendance.check_in = (
                    regularization.requested_check_in
                )
                attendance.check_out = (
                    regularization.requested_check_out
                )
                attendance.save()
                AttendanceLog.objects.create(
                    attendance=attendance,
                    action="Approved",
                    performed_by=request.user,
                    remarks=(
                        "Attendance regularization approved."
                    ),
                )
            else:
                AttendanceLog.objects.create(
                    attendance=regularization.attendance,
                    action="Rejected",
                    performed_by=request.user,
                    remarks=(
                        "Attendance regularization rejected."
                    ),
                )
        return Response(
            {
                "message": (
                    f"Attendance regularization "
                    f"{action.lower()} successfully."
                ),
                "status": regularization.status,
            },
            status=status.HTTP_200_OK
        )


class AttendanceAdjustmentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, attendance_id):
        try:
            attendance = Attendance.objects.get(
                pk=attendance_id
            )
        except Attendance.DoesNotExist:
            return Response(
                {
                    "detail": "Attendance record not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        if (
            not is_hr_or_super_admin(request.user)
            and (
                not has_employee_profile(request.user)
                or attendance.employee
                != request.user.employee_profile
            )
        ):
            return Response(
                {
                    "detail": (
                        "You do not have permission "
                        "to view these adjustments."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )
        adjustments = AttendanceAdjustment.objects.filter(attendance=attendance).select_related("adjusted_by")
        serializer = AttendanceAdjustmentSerializer(adjustments,many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request, attendance_id):
        if not is_hr_or_super_admin(request.user):
            return Response(
                {
                    "detail": (
                        "Only HR or Super Admin can "
                        "create attendance adjustments."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            attendance = Attendance.objects.get(
                pk=attendance_id
            )
        except Attendance.DoesNotExist:
            return Response(
                {
                    "detail": "Attendance record not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        data = request.data.copy()
        data["attendance"] = attendance.id
        serializer = AttendanceAdjustmentSerializer(
            data=data
        )
        if serializer.is_valid():
            adjustment = serializer.save(
                adjusted_by=request.user
            )
            return Response(
                {
                    "message": (
                        "Attendance adjustment "
                        "created successfully."
                    ),
                    "id": adjustment.id,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class AttendanceLogListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, attendance_id):
        if not is_hr_or_super_admin(request.user):
            return Response(
                {
                    "detail": (
                        "Only HR or Super Admin can "
                        "view attendance audit logs."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )
        logs = (
            AttendanceLog.objects
            .filter(
                attendance_id=attendance_id
            )
            .select_related(
                "performed_by",
                "attendance",
            )
        )
        serializer = AttendanceLogSerializer(logs,many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class AttendanceAttachmentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_attendance(self, pk):
        try:
            return Attendance.objects.select_related(
                "employee"
            ).get(pk=pk)
        except Attendance.DoesNotExist:
            return None

    def get(self, request, pk):
        attendance = self.get_attendance(pk)
        if not attendance:
            return Response(
                {
                    "detail": "Attendance record not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        is_owner = (
            has_employee_profile(request.user)
            and attendance.employee
            == request.user.employee_profile
        )
        is_manager = (
            has_employee_profile(request.user)
            and attendance.employee.reporting_manager
            == request.user.employee_profile
        )
        if not (
            is_owner
            or is_manager
            or is_hr_or_super_admin(request.user)
        ):
            return Response(
                {
                    "detail": (
                        "You do not have permission "
                        "to view these attachments."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )
        attachments = (
            AttendanceAttachment.objects
            .filter(
                attendance=attendance
            )
            .select_related(
                "uploaded_by"
            )
        )
        serializer = AttendanceAttachmentSerializer(attachments,many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
    
    def post(self, request, pk):
        attendance = self.get_attendance(pk)
        if not attendance:
            return Response(
                {
                    "detail": "Attendance record not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        if not has_employee_profile(request.user):
            return Response(
                {
                    "detail": "Employee profile not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        if (
            attendance.employee
            != request.user.employee_profile
            and not is_hr_or_super_admin(request.user)
        ):
            return Response(
                {
                    "detail": (
                        "You can only upload "
                        "attachments to your own attendance."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = AttendanceAttachmentSerializer(
            data={
                "attendance": attendance.id,
                "file": request.FILES.get("file"),
            }
        )
        if serializer.is_valid():

            attachment = serializer.save(
                uploaded_by=request.user
            )
            return Response(
                {
                    "message": (
                        "Attendance attachment "
                        "uploaded successfully."
                    ),
                    "id": attachment.id,
                    "file": attachment.file.url,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class AttendanceAttachmentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            attachment = (
                AttendanceAttachment.objects
                .select_related(
                    "attendance",
                    "attendance__employee",
                )
                .get(pk=pk)
            )
        except AttendanceAttachment.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Attendance attachment not found."
                    )
                },
                status=status.HTTP_404_NOT_FOUND
            )
        is_owner = (
            has_employee_profile(request.user)
            and attachment.attendance.employee
            == request.user.employee_profile
        )
        if not (
            is_owner
            or is_hr_or_super_admin(request.user)
        ):
            return Response(
                {
                    "detail": (
                        "You do not have permission "
                        "to delete this attachment."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )
        attachment.file.delete(
            save=False
        )
        attachment.delete()
        return Response(
            {
                "message": (
                    "Attendance attachment "
                    "deleted successfully."
                )
            },
            status=status.HTTP_200_OK
        )


class OvertimeListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = (
            Overtime.objects
            .select_related(
                "attendance",
                "attendance__employee",
                "approved_by",
            )
        )
        if is_hr_or_super_admin(request.user):
            overtimes = queryset.all()
        elif has_employee_profile(request.user):
            overtimes = queryset.filter(
                attendance__employee=
                request.user.employee_profile
            )
        else:
            return Response(
                {
                    "detail": "Employee profile not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = OvertimeSerializer(
            overtimes,
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        if not has_employee_profile(request.user):
            return Response(
                {
                    "detail": "Employee profile not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = OvertimeSerializer(
            data=request.data
        )
        if serializer.is_valid():
            attendance = serializer.validated_data[
                "attendance"
            ]
            if (
                attendance.employee
                != request.user.employee_profile
                and not is_hr_or_super_admin(request.user)
            ):
                return Response(
                    {
                        "detail": (
                            "You can only create overtime "
                            "for your own attendance."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            overtime = serializer.save()
            return Response(
                {
                    "message": (
                        "Overtime request "
                        "created successfully."
                    ),
                    "id": overtime.id,
                    "status": overtime.status,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class OvertimeReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            overtime = (
                Overtime.objects
                .select_related(
                    "attendance",
                    "attendance__employee",
                )
                .get(pk=pk)
            )
        except Overtime.DoesNotExist:
            return Response(
                {
                    "detail": "Overtime request not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        if overtime.status != "Pending":
            return Response(
                {
                    "detail": (
                        "Only pending overtime "
                        "requests can be reviewed."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        employee = overtime.attendance.employee
        is_manager = (
            has_employee_profile(request.user)
            and employee.reporting_manager
            == request.user.employee_profile
        )
        if not (
            is_hr_or_super_admin(request.user)
            or is_manager
        ):
            return Response(
                {
                    "detail": (
                        "You do not have permission "
                        "to review this overtime request."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )
        action = request.data.get("action")
        if action not in [
            "Approved",
            "Rejected",
        ]:
            return Response(
                {
                    "action": (
                        "Action must be either "
                        "'Approved' or 'Rejected'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        with transaction.atomic():
            overtime.status = action
            if action == "Approved":
                overtime.approved_by = request.user
                overtime.approved_at = timezone.now()
            overtime.save(
                update_fields=[
                    "status",
                    "approved_by",
                    "approved_at",
                    "updated_at",
                ]
            )
        return Response(
            {
                "message": (
                    f"Overtime request "
                    f"{action.lower()} successfully."
                ),
                "status": overtime.status,
            },
            status=status.HTTP_200_OK
        )

class OvertimeDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return (
                Overtime.objects
                .select_related(
                    "attendance",
                    "attendance__employee",
                    "approved_by",
                )
                .get(pk=pk)
            )
        except Overtime.DoesNotExist:
            return None

    def get(self, request, pk):
        overtime = self.get_object(pk)
        if not overtime:
            return Response(
                {
                    "detail": "Overtime request not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        if is_hr_or_super_admin(request.user):
            has_access = True
        elif has_employee_profile(request.user):
            has_access = (
                overtime.attendance.employee
                == request.user.employee_profile
            )
        else:
            has_access = False
        if not has_access:
            return Response(
                {
                    "detail": (
                        "You do not have permission "
                        "to view this overtime request."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = OvertimeSerializer(overtime)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )