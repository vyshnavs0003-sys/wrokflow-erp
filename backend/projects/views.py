from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Project
from .serializers import ProjectSerializer
from .permissions import CanManageProjects


class ProjectListCreateView(APIView):
    permission_classes = [CanManageProjects]
    def get(self, request):
        user = request.user
        if user.is_superuser:
            projects = Project.objects.all()
        elif user.groups.filter(name="HR").exists():
            projects = Project.objects.all()
        elif user.groups.filter(name="Employee").exists():
            projects = Project.objects.filter(
                project_manager__user=user
            ) | Project.objects.filter(
                team_members__employee__user=user
            )
            projects = projects.distinct()
        else:
            projects = Project.objects.none()
        serializer = ProjectSerializer(
            projects,
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
    def post(self, request):
        serializer = ProjectSerializer(
            data=request.data
        )
        if serializer.is_valid():
            project = serializer.save()
            return Response(
                {
                    "message": "Project created successfully",
                    "project_id": project.id,
                    "project_name": project.name,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ProjectDetailView(APIView):
    permission_classes = [CanManageProjects]
    def get(self, request, pk):
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response(
                {
                    "detail": "Project not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(
            request,
            project
        )
        serializer = ProjectSerializer(project)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request, pk):
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response(
                {
                    "detail": "Project not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(
            request,
            project
        )
        serializer = ProjectSerializer(
            project,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Project updated successfully",
                    "project": serializer.data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )