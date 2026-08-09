from django.urls import path

from .views import (
    ShiftListCreateView,
    ShiftDetailView,
    EmployeeShiftAssignmentListCreateView,
    EmployeeShiftAssignmentDetailView,
    AttendanceListCreateView,
    AttendanceDetailView,
    AttendanceRegularizationListCreateView,
    AttendanceRegularizationDetailView,
    AttendanceRegularizationReviewView,
    AttendanceAdjustmentListCreateView,
    AttendanceLogListView,
    AttendanceAttachmentListCreateView,
    AttendanceAttachmentDeleteView,
    OvertimeListCreateView,
    OvertimeDetailView,
    OvertimeReviewView,
)


urlpatterns = [
    path("shifts/",ShiftListCreateView.as_view(),name="shift-list-create"),
    path("shifts/<int:pk>/",ShiftDetailView.as_view(),name="shift-detail"),
    path("shift-assignments/",EmployeeShiftAssignmentListCreateView.as_view(),name="shift-assignment-list-create"),
    path("shift-assignments/<int:pk>/",EmployeeShiftAssignmentDetailView.as_view(),name="shift-assignment-detail"),
    path("records/",AttendanceListCreateView.as_view(),name="attendance-list-create"),
    path("records/<int:pk>/",AttendanceDetailView.as_view(),name="attendance-detail"),
    path("regularizations/",AttendanceRegularizationListCreateView.as_view(),name="attendance-regularization-list-create"),
    path("regularizations/<int:pk>/",AttendanceRegularizationDetailView.as_view(),name="attendance-regularization-detail"),
    path("regularizations/<int:pk>/review/",AttendanceRegularizationReviewView.as_view(),name="attendance-regularization-review"),
    path("records/<int:attendance_id>/adjustments/",AttendanceAdjustmentListCreateView.as_view(),name="attendance-adjustment-list-create"),
    path("records/<int:attendance_id>/logs/",AttendanceLogListView.as_view(),name="attendance-log-list"),
    path("records/<int:pk>/attachments/",AttendanceAttachmentListCreateView.as_view(),name="attendance-attachment-list-create"),
    path("attachments/<int:pk>/",AttendanceAttachmentDeleteView.as_view(),name="attendance-attachment-delete"),
    path("overtime/",OvertimeListCreateView.as_view(),name="overtime-list-create"),
    path("overtime/<int:pk>/",OvertimeDetailView.as_view(),name="overtime-detail"),
    path("overtime/<int:pk>/review/",OvertimeReviewView.as_view(),name="overtime-review"),
]