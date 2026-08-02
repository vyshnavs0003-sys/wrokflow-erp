from django.urls import path
from .views import ProjectListCreateView, ProjectDetailView, ProjectTeamListCreateView,ProjectTeamDetailView, ProjectTaskListCreateView


urlpatterns = [
    path("", ProjectListCreateView.as_view(), name="project-list-create"),
    path("<int:pk>/", ProjectDetailView.as_view(), name="project-detail"),
    path("<int:project_id>/team/",ProjectTeamListCreateView.as_view(),name="project-team-list-create"),
    path("<int:project_id>/team/<int:team_id>/",ProjectTeamDetailView.as_view(),name="project-team-detail"),
    path("<int:project_id>/tasks/",ProjectTaskListCreateView.as_view(),name="project-task-list-create"),
]