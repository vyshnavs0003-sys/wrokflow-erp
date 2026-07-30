from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Project
from .serializers import ProjectSerializer
# Create your views here.

class ProjectListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        projects = Project.objects.all()
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