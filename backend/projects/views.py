from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Project, ProjectTeam, Task, TaskAssignment
from .serializers import ProjectSerializer, ProjectTeamSerializer, TaskSerializer, TaskAssignmentSerializer
from .permissions import CanManageProjects, CanManageProjectTeam, CanManageProjectTasks, CanManageTaskAssignments


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


class ProjectTeamListCreateView(APIView):
    permission_classes = [CanManageProjectTeam]
    def get(self, request, project_id):
        try:
            project = Project.objects.get(
                pk=project_id
            )
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
        team_members = ProjectTeam.objects.filter(
            project=project
        )
        serializer = ProjectTeamSerializer(
            team_members,
            many=True,
            context={"project": project}
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request, project_id):
        try:
            project = Project.objects.get(
                pk=project_id
            )
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
        serializer = ProjectTeamSerializer(
            data=request.data,
            context={"project": project}
        )
        if serializer.is_valid():
            serializer.save(
                project=project
            )
            return Response(
                {
                    "message": "Team member added successfully",
                    "team_member": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ProjectTeamDetailView(APIView):
    permission_classes = [CanManageProjectTeam]

    def get_object(self, project_id, team_id):
        try:
            return ProjectTeam.objects.get(
                pk=team_id,
                project_id=project_id
            )
        except ProjectTeam.DoesNotExist:
            return None

    def get(self, request, project_id, team_id):
        team_member = self.get_object(
            project_id,
            team_id
        )
        if not team_member:
            return Response(
                {
                    "detail": "Team member not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(
            request,
            team_member.project
        )
        serializer = ProjectTeamSerializer(
            team_member,
            context={"project": team_member.project}
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request, project_id, team_id):
        team_member = self.get_object(
            project_id,
            team_id
        )
        if not team_member:
            return Response(
                {
                    "detail": "Team member not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(
            request,
            team_member.project
        )
        serializer = ProjectTeamSerializer(
            team_member,
            data=request.data,
            partial=True,
            context={"project": team_member.project}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Team member updated successfully",
                    "team_member": serializer.data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, project_id, team_id):
        team_member = self.get_object(
            project_id,
            team_id
        )
        if not team_member:
            return Response(
                {
                    "detail": "Team member not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(
            request,
            team_member.project
        )
        team_member.delete()
        return Response(
            {
                "message": "Team member removed successfully."
            },
            status=status.HTTP_204_NO_CONTENT
        )


class ProjectTaskListCreateView(APIView):
    permission_classes = [CanManageProjectTasks]

    def get(self, request, project_id):
        try:
            project = Project.objects.get(
                pk=project_id
            )
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
        tasks = Task.objects.filter(
            project=project
        )
        serializer = TaskSerializer(
            tasks,
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request, project_id):
        try:
            project = Project.objects.get(
                pk=project_id
            )
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
        serializer = TaskSerializer(
            data=request.data
        )
        if serializer.is_valid():
            serializer.save(
                project=project
            )
            return Response(
                {
                    "message": "Task created successfully",
                    "task": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class TaskAssignmentListCreateView(APIView):
    permission_classes = [CanManageTaskAssignments]

    def get(self, request, project_id, task_id):
        try:
            task = Task.objects.get(
                pk=task_id,
                project_id=project_id
            )
        except Task.DoesNotExist:
            return Response(
                {
                    "detail": "Task not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        assignments = TaskAssignment.objects.filter(
            task=task
        )

        if request.user.groups.filter(name="Employee").exists():
            if task.project.project_manager.user != request.user:
                assignments = assignments.filter(
                    employee__user=request.user
                )

        serializer = TaskAssignmentSerializer(
            assignments,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request, project_id, task_id):
        try:
            task = Task.objects.get(
                pk=task_id,
                project_id=project_id
            )
        except Task.DoesNotExist:
            return Response(
                {
                    "detail": "Task not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if (
            request.user.groups.filter(name="Employee").exists()
            and task.project.project_manager.user != request.user
        ):
            return Response(
                {
                    "detail": (
                        "Only the project manager "
                        "can assign tasks."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TaskAssignmentSerializer(
            data=request.data,
            context={"task": task}
        )

        if serializer.is_valid():
            serializer.save(
                    task=task,
                    assigned_by=request.user.employee_profile
            ) 
            return Response(
                {
                    "message": "Task assigned successfully",
                    "assignment": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class TaskAssignmentDetailView(APIView):
    permission_classes = [CanManageTaskAssignments]

    def get_object(self, project_id, task_id, assignment_id):
        try:
            return TaskAssignment.objects.get(
                pk=assignment_id,
                task_id=task_id,
                task__project_id=project_id
            )
        except TaskAssignment.DoesNotExist:
            return None

    def get(self, request, project_id, task_id, assignment_id):
        assignment = self.get_object(
            project_id,
            task_id,
            assignment_id
        )

        if not assignment:
            return Response(
                {
                    "detail": "Task assignment not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(
            request,
            assignment
        )

        serializer = TaskAssignmentSerializer(
            assignment
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request, project_id, task_id, assignment_id):
        assignment = self.get_object(
            project_id,
            task_id,
            assignment_id
        )

        if not assignment:
            return Response(
                {
                    "detail": "Task assignment not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(
            request,
            assignment
        )

        serializer = TaskAssignmentSerializer(
            assignment,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "Task assignment updated successfully",
                    "assignment": serializer.data
                },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, project_id, task_id, assignment_id):
        assignment = self.get_object(
            project_id,
            task_id,
            assignment_id
        )

        if not assignment:
            return Response(
                {
                    "detail": "Task assignment not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(
            request,
            assignment
        )

        assignment.delete()

        return Response(
            {
                "message": "Task assignment removed successfully."
            },
            status=status.HTTP_204_NO_CONTENT
        )