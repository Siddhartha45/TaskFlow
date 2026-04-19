from datetime import date, timedelta
from django.core.mail import send_mail
from celery import shared_task
from collections import defaultdict
from django.contrib.auth import get_user_model

from .models import Task


User = get_user_model()


@shared_task
def task_reminder():
    tomorrow = date.today() + timedelta(days=1)
    tasks = Task.objects.filter(due_date=tomorrow).exclude(status="done").select_related("project__owner")
    
    d = defaultdict(list)
    
    for task in tasks:
        d[task.project.owner].append(task)
    
    for user, user_tasks in d.items():
        task_lines = []
        
        for user_task in user_tasks:
            line = f"- {user_task.title} (Project: {user_task.project.name}, Priority: {user_task.priority or 'Not set'})"
            task_lines.append(line)
        
        task_list = "\n".join(task_lines)
        
        message = f"Hi {user.username},\n\nYou have {len(user_tasks)} task(s) due tomorrow:\n\n{task_list}\n\nGood luck!"
        
        send_mail(
        f'Task Reminder: {len(user_tasks)} task(s) due tomorrow',
        message,
        'sid@example.com',
        [user.email],
        fail_silently=False,
    )
    
    