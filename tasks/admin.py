from django.contrib import admin
from .models import Project, Task


class ProjectAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "owner"]


class TaskAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "status", "priority", "project__id", "project__owner", "due_date"]


admin.site.register(Project, ProjectAdmin)
admin.site.register(Task, TaskAdmin)
