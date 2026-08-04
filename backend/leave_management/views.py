from django.db import transaction
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    LeaveType,
    LeavePolicy,
    LeaveAllocation,
    Holiday,
    LeaveRequest,
    LeaveAttachment,
)

from .serializers import (
    LeaveTypeSerializer,
    LeavePolicySerializer,
    LeaveAllocationSerializer,
    HolidaySerializer,
    LeaveRequestSerializer,
    LeaveAttachmentSerializer,
)


class LeaveTypeListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        leave_types = LeaveType.objects.filter(
            is_active=True
        )

        serializer = LeaveTypeSerializer(
            leave_types,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        if not request.user.is_superuser and not request.user.groups.filter(
            name="HR"
        ).exists():
            return Response(
                {
                    "detail": "You do not have permission to create a leave type."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = LeaveTypeSerializer(
            data=request.data
        )

        if serializer.is_valid():
            leave_type = serializer.save()

            return Response(
                {
                    "message": "Leave type created successfully.",
                    "id": leave_type.id,
                    "name": leave_type.name,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LeaveTypeDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return LeaveType.objects.get(pk=pk)
        except LeaveType.DoesNotExist:
            return None

    def get(self, request, pk):
        leave_type = self.get_object(pk)

        if not leave_type:
            return Response(
                {
                    "detail": "Leave type not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = LeaveTypeSerializer(
            leave_type
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request, pk):
        if not request.user.is_superuser and not request.user.groups.filter(
            name="HR"
        ).exists():
            return Response(
                {
                    "detail": "You do not have permission to update a leave type."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        leave_type = self.get_object(pk)

        if not leave_type:
            return Response(
                {
                    "detail": "Leave type not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = LeaveTypeSerializer(
            leave_type,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "Leave type updated successfully."
                },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        if not request.user.is_superuser and not request.user.groups.filter(
            name="HR"
        ).exists():
            return Response(
                {
                    "detail": "You do not have permission to delete a leave type."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        leave_type = self.get_object(pk)

        if not leave_type:
            return Response(
                {
                    "detail": "Leave type not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        leave_type.is_active = False
        leave_type.save(
            update_fields=["is_active", "updated_at"]
        )

        return Response(
            {
                "message": "Leave type deactivated successfully."
            },
            status=status.HTTP_200_OK
        )


class LeavePolicyListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        policies = LeavePolicy.objects.filter(
            is_active=True
        )

        serializer = LeavePolicySerializer(
            policies,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        if not request.user.is_superuser and not request.user.groups.filter(
            name="HR"
        ).exists():
            return Response(
                {
                    "detail": "You do not have permission to create a leave policy."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = LeavePolicySerializer(
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "Leave policy created successfully.",
                    "id": serializer.instance.id,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LeavePolicyDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return LeavePolicy.objects.get(pk=pk)
        except LeavePolicy.DoesNotExist:
            return None

    def get(self, request, pk):
        policy = self.get_object(pk)

        if not policy:
            return Response(
                {
                    "detail": "Leave policy not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = LeavePolicySerializer(
            policy
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request, pk):
        if not request.user.is_superuser and not request.user.groups.filter(
            name="HR"
        ).exists():
            return Response(
                {
                    "detail": "You do not have permission to update a leave policy."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        policy = self.get_object(pk)

        if not policy:
            return Response(
                {
                    "detail": "Leave policy not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = LeavePolicySerializer(
            policy,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "Leave policy updated successfully."
                },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LeaveAllocationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_superuser or request.user.groups.filter(
            name="HR"
        ).exists():
            allocations = LeaveAllocation.objects.all()

        elif hasattr(
            request.user,
            "employee_profile"
        ):
            allocations = LeaveAllocation.objects.filter(
                employee=request.user.employee_profile
            )

        else:
            return Response(
                {
                    "detail": "Employee profile not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = LeaveAllocationSerializer(
            allocations,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        if not request.user.is_superuser and not request.user.groups.filter(
            name="HR"
        ).exists():
            return Response(
                {
                    "detail": "You do not have permission to create a leave allocation."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = LeaveAllocationSerializer(
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "Leave allocation created successfully.",
                    "id": serializer.instance.id,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class HolidayListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        holidays = Holiday.objects.filter(
            is_active=True
        )

        serializer = HolidaySerializer(
            holidays,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        if not request.user.is_superuser and not request.user.groups.filter(
            name="HR"
        ).exists():
            return Response(
                {
                    "detail": "You do not have permission to create a holiday."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = HolidaySerializer(
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "Holiday created successfully.",
                    "id": serializer.instance.id,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LeaveRequestListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_superuser or request.user.groups.filter(
            name="HR"
        ).exists():
            leave_requests = LeaveRequest.objects.all()

        elif hasattr(
            request.user,
            "employee_profile"
        ):
            employee = request.user.employee_profile

            leave_requests = LeaveRequest.objects.filter(
                employee=employee
            )

        else:
            return Response(
                {
                    "detail": "Employee profile not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = LeaveRequestSerializer(
            leave_requests,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        if not hasattr(
            request.user,
            "employee_profile"
        ):
            return Response(
                {
                    "detail": "Employee profile not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = LeaveRequestSerializer(
            data=request.data,
            context={
                "request": request
            }
        )

        if serializer.is_valid():
            leave_request = serializer.save()

            return Response(
                {
                    "message": "Leave request created successfully.",
                    "id": leave_request.id,
                    "total_days": leave_request.total_days,
                    "status": leave_request.status,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LeaveRequestDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return LeaveRequest.objects.get(pk=pk)
        except LeaveRequest.DoesNotExist:
            return None

    def get(self, request, pk):
        leave_request = self.get_object(pk)

        if not leave_request:
            return Response(
                {
                    "detail": "Leave request not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if (
            not request.user.is_superuser
            and not request.user.groups.filter(
                name="HR"
            ).exists()
            and leave_request.employee != request.user.employee_profile
        ):
            if (
                not hasattr(
                    request.user,
                    "employee_profile"
                )
                or leave_request.employee.reporting_manager
                != request.user.employee_profile
            ):
                return Response(
                    {
                        "detail": "You do not have permission to view this leave request."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

        serializer = LeaveRequestSerializer(
            leave_request
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class LeaveRequestCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            leave_request = LeaveRequest.objects.get(
                pk=pk
            )
        except LeaveRequest.DoesNotExist:
            return Response(
                {
                    "detail": "Leave request not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if not hasattr(
            request.user,
            "employee_profile"
        ):
            return Response(
                {
                    "detail": "Employee profile not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if leave_request.employee != request.user.employee_profile:
            return Response(
                {
                    "detail": "You can only cancel your own leave request."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        if leave_request.status != "Pending":
            return Response(
                {
                    "detail": "Only pending leave requests can be cancelled."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        cancellation_reason = request.data.get(
            "cancellation_reason"
        )

        if not cancellation_reason:
            return Response(
                {
                    "cancellation_reason": "Cancellation reason is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        leave_request.status = "Cancelled"
        leave_request.cancelled_at = timezone.now()
        leave_request.cancellation_reason = cancellation_reason
        leave_request.save(
            update_fields=[
                "status",
                "cancelled_at",
                "cancellation_reason",
                "updated_at",
            ]
        )

        return Response(
            {
                "message": "Leave request cancelled successfully."
            },
            status=status.HTTP_200_OK
        )
    
class LeaveRequestApprovalView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            leave_request = LeaveRequest.objects.get(
                pk=pk
            )
        except LeaveRequest.DoesNotExist:
            return Response(
                {
                    "detail": "Leave request not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if leave_request.status != "Pending":
            return Response(
                {
                    "detail": "Only pending leave requests can be approved or rejected."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        is_super_admin = request.user.is_superuser

        is_hr = request.user.groups.filter(
            name="HR"
        ).exists()

        is_reporting_manager = (
            hasattr(
                request.user,
                "employee_profile"
            )
            and leave_request.employee.reporting_manager
            == request.user.employee_profile
        )

        if not (
            is_super_admin
            or is_hr
            or is_reporting_manager
        ):
            return Response(
                {
                    "detail": "You do not have permission to review this leave request."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        action = request.data.get(
            "action"
        )

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

        if action == "Approved":
            allocation = LeaveAllocation.objects.filter(
                employee=leave_request.employee,
                leave_type=leave_request.leave_type,
                year=leave_request.start_date.year,
                is_active=True
            ).first()

            if not allocation:
                return Response(
                    {
                        "detail": (
                            "No active leave allocation exists "
                            "for this employee and leave type "
                            "for the selected year."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if allocation.remaining_days < leave_request.total_days:
                return Response(
                    {
                        "detail": (
                            "Insufficient leave balance "
                            "for this leave request."
                        ),
                        "remaining_days": allocation.remaining_days,
                        "requested_days": leave_request.total_days,
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        with transaction.atomic():
            leave_request.status = action
            leave_request.reviewed_by = request.user
            leave_request.reviewed_at = timezone.now()
            leave_request.reviewed_comments = comments

            leave_request.save(
                update_fields=[
                    "status",
                    "reviewed_by",
                    "reviewed_at",
                    "reviewed_comments",
                    "updated_at",
                ]
            )

        return Response(
            {
                "message": (
                    f"Leave request {action.lower()} successfully."
                ),
                "leave_request_id": leave_request.id,
                "status": leave_request.status,
                "reviewed_by": request.user.username,
            },
            status=status.HTTP_200_OK
        )


class LeaveAttachmentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_leave_request(self, pk):
        try:
            return LeaveRequest.objects.get(
                pk=pk
            )
        except LeaveRequest.DoesNotExist:
            return None

    def get(self, request, pk):
        leave_request = self.get_leave_request(pk)

        if not leave_request:
            return Response(
                {
                    "detail": "Leave request not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if not hasattr(
            request.user,
            "employee_profile"
        ):
            return Response(
                {
                    "detail": "Employee profile not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        is_owner = (
            leave_request.employee
            == request.user.employee_profile
        )

        is_hr = request.user.groups.filter(
            name="HR"
        ).exists()

        is_super_admin = request.user.is_superuser

        is_reporting_manager = (
            leave_request.employee.reporting_manager
            == request.user.employee_profile
        )

        if not (
            is_owner
            or is_hr
            or is_super_admin
            or is_reporting_manager
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

        attachments = LeaveAttachment.objects.filter(
            leave_request=leave_request
        )

        serializer = LeaveAttachmentSerializer(
            attachments,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request, pk):
        leave_request = self.get_leave_request(pk)

        if not leave_request:
            return Response(
                {
                    "detail": "Leave request not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if not hasattr(
            request.user,
            "employee_profile"
        ):
            return Response(
                {
                    "detail": "Employee profile not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if (
            leave_request.employee
            != request.user.employee_profile
        ):
            return Response(
                {
                    "detail": (
                        "You can only upload attachments "
                        "to your own leave request."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = LeaveAttachmentSerializer(
            data={
                "leave_request": leave_request.id,
                "file": request.FILES.get(
                    "file"
                ),
            }
        )

        if serializer.is_valid():
            attachment = serializer.save(
                uploaded_by=request.user
            )

            return Response(
                {
                    "message": (
                        "Leave attachment uploaded successfully."
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


class LeaveAttachmentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            attachment = LeaveAttachment.objects.get(
                pk=pk
            )
        except LeaveAttachment.DoesNotExist:
            return Response(
                {
                    "detail": "Leave attachment not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if not hasattr(
            request.user,
            "employee_profile"
        ):
            return Response(
                {
                    "detail": "Employee profile not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        is_owner = (
            attachment.leave_request.employee
            == request.user.employee_profile
        )

        is_hr = request.user.groups.filter(
            name="HR"
        ).exists()

        is_super_admin = request.user.is_superuser

        if not (
            is_owner
            or is_hr
            or is_super_admin
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
                    "Leave attachment deleted successfully."
                )
            },
            status=status.HTTP_200_OK
        )