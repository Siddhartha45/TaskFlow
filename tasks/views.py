from django.shortcuts import render, get_object_or_404
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from .serializers import ProjectSerializer, TaskSerializer
from .models import Project, Task


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
        project = get_object_or_404(Project, id=self.kwargs['project_id'], owner=self.request.user)
        serializer.save(project=project)
    
    def get_queryset(self):
        return Task.objects.filter(project__id=self.kwargs['project_id'], project__owner=self.request.user)
    

class TaskDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Task.objects.filter(project__id=self.kwargs['project_id'], project__owner=self.request.user)