from django.urls import path
from .views import ProjectListCreateView, ProjectDetailView


urlpatterns = [
    path('projects/', ProjectListCreateView.as_view()),
    path('projects/<int:pk>/', ProjectDetailView.as_view()),
]
