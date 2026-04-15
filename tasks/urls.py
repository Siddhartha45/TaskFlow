from django.urls import path

from .views import (
    ProjectListCreateView,
    ProjectDetailView,
    TaskListCreateView,
    TaskDetailView,
    TaskExportView,
)


urlpatterns = [
    path("projects/", ProjectListCreateView.as_view()),
    path("projects/<int:pk>/", ProjectDetailView.as_view()),
    path("projects/<int:project_id>/tasks/", TaskListCreateView.as_view()),
    path("projects/<int:project_id>/tasks/<int:pk>/", TaskDetailView.as_view()),
    path("projects/<int:project_id>/tasks/export/", TaskExportView.as_view()),
]
