from django.contrib import admin
from .models import Project, Task


class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'owner']
    
    
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'project__id','project__owner']
    
    
admin.site.register(Project, ProjectAdmin)
admin.site.register(Task, TaskAdmin)