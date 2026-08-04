from django.urls import path

from .views import (
    LeaveTypeListCreateView,
    LeaveTypeDetailView,
    LeavePolicyListCreateView,
    LeavePolicyDetailView,
    LeaveAllocationListCreateView,
    HolidayListCreateView,
    LeaveRequestListCreateView,
    LeaveRequestDetailView,
    LeaveRequestCancelView,
    LeaveRequestApprovalView,
    LeaveAttachmentListCreateView,
    LeaveAttachmentDeleteView,
)


urlpatterns = [
    path("types/",LeaveTypeListCreateView.as_view(),name="leave-type-list-create"),
    path("types/<int:pk>/",LeaveTypeDetailView.as_view(),name="leave-type-detail"),
    path("policies/",LeavePolicyListCreateView.as_view(),name="leave-policy-list-create"),
    path("policies/<int:pk>/",LeavePolicyDetailView.as_view(),name="leave-policy-detail"),
    path("allocations/",LeaveAllocationListCreateView.as_view(),name="leave-allocation-list-create"),
    path("holidays/",HolidayListCreateView.as_view(),name="holiday-list-create"),
    path("requests/",LeaveRequestListCreateView.as_view(),name="leave-request-list-create"),
    path("requests/<int:pk>/",LeaveRequestDetailView.as_view(),name="leave-request-detail"),
    path("requests/<int:pk>/cancel/",LeaveRequestCancelView.as_view(),name="leave-request-cancel"),
    path("requests/<int:pk>/review/",LeaveRequestApprovalView.as_view(),name="leave-request-review"),
    path("requests/<int:pk>/attachments/",LeaveAttachmentListCreateView.as_view(),name="leave-attachment-list-create"),
    path("attachments/<int:pk>/",LeaveAttachmentDeleteView.as_view(),name="leave-attachment-delete"),
]