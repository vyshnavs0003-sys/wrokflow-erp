from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.EmployeeCreateView.as_view(), name="employee-create"),
    path("",views.EmployeeListView.as_view(),name="employee-list"),
]