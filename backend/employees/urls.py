from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.EmployeeCreateView.as_view(), name="employee-create"),
    path("",views.EmployeeListView.as_view(),name="employee-list"),
    path("<int:employee_id>/",views.EmployeeDetailUpdateView.as_view(),name="employee-detail-update"),
]