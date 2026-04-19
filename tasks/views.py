from io import BytesIO

import pandas as pd
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer


class ProjectListCreateView(ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        return user.projects.all()


class ProjectDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return user.projects.all()


class TaskListCreateView(ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        project = get_object_or_404(
            Project, id=self.kwargs["project_id"], owner=self.request.user
        )
        serializer.save(project=project)

    def get_queryset(self):
        queryset = Task.objects.filter(
            project__id=self.kwargs["project_id"], project__owner=self.request.user
        )

        status = self.request.query_params.get("status")
        priority = self.request.query_params.get("priority")
        due_date = self.request.query_params.get("due_date")

        if status:
            queryset = queryset.filter(status=status)

        if priority:
            queryset = queryset.filter(priority=priority)

        if due_date:
            queryset = queryset.filter(due_date=due_date)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        project = get_object_or_404(Project, id=self.kwargs["project_id"])

        if not queryset and project.owner == self.request.user:
            return Response(
                {"detail": "This project do not have any tasks."},
                status=status.HTTP_200_OK,
            )

        if not queryset and project.owner != self.request.user:
            return Response(
                {"detail": "No Project matches the given query."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TaskSerializer(queryset, many=True)
        return Response(serializer.data)


class TaskDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(
            project__id=self.kwargs["project_id"], project__owner=self.request.user
        )


class TaskExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id, format=None):
        project = get_object_or_404(Project, id=project_id, owner=self.request.user)

        tasks = Task.objects.filter(project=project)
        serializer = TaskSerializer(tasks, many=True)

        columns = [
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "created_at",
        ]

        df = pd.DataFrame(serializer.data).reindex(columns=columns)

        df = df.rename(
            columns={
                "title": "Title",
                "description": "Description",
                "status": "Status",
                "priority": "Priority",
                "due_date": "Due Date",
                "created_at": "Created At",
            }
        )

        buffer = BytesIO()

        df.to_excel(buffer, index=False)
        buffer.seek(0)

        response = FileResponse(
            buffer,
            as_attachment=True,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"{project.name}.xlsx",
        )

        return response
