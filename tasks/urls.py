from django.urls import path

from .views import (
    ProjectListCreateView,
    ProjectDetailView,
    TaskListCreateView,
    TaskDetailView,
    TaskExportView,
)

urlpatterns = [
    path("projects/", ProjectListCreateView.as_view(), name="projects"),
    path("projects/<int:pk>/", ProjectDetailView.as_view(), name="single_project"),
    path(
        "projects/<int:project_id>/tasks/", TaskListCreateView.as_view(), name="tasks"
    ),
    path(
        "projects/<int:project_id>/tasks/<int:pk>/",
        TaskDetailView.as_view(),
        name="single_task",
    ),
    path(
        "projects/<int:project_id>/tasks/export/",
        TaskExportView.as_view(),
        name="tasks_export",
    ),
]
