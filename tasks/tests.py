import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Project, Task

User = get_user_model()


@pytest.mark.django_db
class TestProject:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="james", email="jrodriguez@gmail.com", password="james@123"
        )
        response = self.client.post(
            reverse("login"), {"username": "james", "password": "james@123"}
        )
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.another_user = User.objects.create_user(
            username="messi", email="messi@gmail.com", password="lionel@123"
        )

        self.p1 = Project.objects.create(
            name="project1", description="desc1", owner=self.user
        )
        self.p2 = Project.objects.create(
            name="project2", description="desc2", owner=self.user
        )
        self.p3 = Project.objects.create(
            name="project3", description="desc3", owner=self.user
        )
        self.p4 = Project.objects.create(
            name="project4", description="desc4", owner=self.another_user
        )
        self.p5 = Project.objects.create(
            name="project5", description="desc5", owner=self.another_user
        )

    def test_create_project_success(self):
        payload = {"name": "testproject", "description": "testdesc"}
        response = self.client.post(reverse("projects"), payload)
        assert response.status_code == 201
        assert response.data["name"] == "testproject"
        assert response.data["owner"] == self.user.id

    def test_create_project_missing_name(self):
        payload = {"description": "desc1"}
        response = self.client.post(reverse("projects"), payload)
        assert response.status_code == 400

    def test_list_projects_shows_only_own(self):
        response = self.client.get(reverse("projects"))
        assert len(response.data) == 3

    def test_retrieve_own_project(self):
        response = self.client.get(reverse("single_project", kwargs={"pk": self.p1.id}))
        assert response.status_code == 200
        assert response.data["name"] == "project1"
        assert response.data["description"] == "desc1"
        assert response.data["owner"] == self.user.id

    def test_retrieve_others_project_returns_404(self):
        response = self.client.get(reverse("single_project", kwargs={"pk": self.p5.id}))
        assert response.status_code == 404

    def test_update_own_project(self):
        payload = {"name": "newname", "description": "desc3"}
        response = self.client.put(
            reverse("single_project", kwargs={"pk": self.p3.id}), payload
        )
        assert response.status_code == 200
        assert response.data["name"] == "newname"

    def test_update_others_project_returns_404(self):
        payload = {"name": "newname", "description": "newdesc"}
        response = self.client.put(
            reverse("single_project", kwargs={"pk": self.p4.id}), payload
        )
        assert response.status_code == 404

    def test_delete_own_project(self):
        response = self.client.delete(
            reverse("single_project", kwargs={"pk": self.p2.id})
        )
        assert response.status_code == 204
        assert not Project.objects.filter(id=self.p2.id).exists()

    def test_delete_others_project_returns_404(self):
        response = self.client.delete(
            reverse("single_project", kwargs={"pk": self.p4.id})
        )
        assert response.status_code == 404


@pytest.mark.django_db
class TestTasks:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="zoro", email="zoro@gmail.com", password="roronoa@123"
        )
        response = self.client.post(
            reverse("login"), {"username": "zoro", "password": "roronoa@123"}
        )
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.p1 = Project.objects.create(
            name="project1", description="desc1", owner=self.user
        )
        self.p2 = Project.objects.create(
            name="project2", description="desc2", owner=self.user
        )

        self.t1 = Task.objects.create(
            title="clean room",
            status="todo",
            priority="low",
            due_date="2026-05-21",
            project=self.p1,
        )
        self.t2 = Task.objects.create(
            title="buy groceries",
            status="todo",
            priority="medium",
            due_date="2026-05-15",
            project=self.p1,
        )
        self.t3 = Task.objects.create(
            title="read", status="todo", priority="high", project=self.p1
        )
        self.t4 = Task.objects.create(
            title="meet geralt",
            status="in_progress",
            priority="medium",
            project=self.p2,
        )
        self.t5 = Task.objects.create(
            title="meet arthur", status="done", priority="medium", project=self.p2
        )

    # Task Creation Tests
    def test_create_task_success(self):
        payload = {
            "title": "test title",
            "description": "test desc",
            "priority": "high",
            "due_date": "2026-05-21",
        }
        response = self.client.post(
            reverse("tasks", kwargs={"project_id": self.p1.id}), payload
        )
        assert response.status_code == 201
        assert response.data["title"] == "test title"
        assert response.data["status"] == "todo"

    def test_create_task_missing_title(self):
        payload = {
            "description": "task1_desc",
            "priority": "high",
            "due_date": "2026-05-21",
        }
        response = self.client.post(
            reverse("tasks", kwargs={"project_id": self.p1.id}), payload
        )
        assert response.status_code == 400

    # Task List Tests
    def test_list_tasks_under_project(self):
        response = self.client.get(reverse("tasks", kwargs={"project_id": self.p1.id}))
        assert len(response.data) == 3

    # Task Filtering Tests
    def test_filter_tasks_by_status(self):
        Task.objects.create(title="meet jin", status="done", project=self.p2)
        response = self.client.get(
            reverse("tasks", kwargs={"project_id": self.p2.id}), {"status": "done"}
        )
        assert len(response.data) == 2

    def test_filter_tasks_by_priority(self):
        Task.objects.create(title="change sheets", priority="medium", project=self.p1)
        response = self.client.get(
            reverse("tasks", kwargs={"project_id": self.p1.id}), {"priority": "medium"}
        )
        assert len(response.data) == 2

    def test_filter_tasks_by_due_date(self):
        Task.objects.create(
            title="change sheets", due_date="2026-05-15", project=self.p1
        )
        response = self.client.get(
            reverse("tasks", kwargs={"project_id": self.p1.id}),
            {"due_date": "2026-05-15"},
        )
        assert len(response.data) == 2

    def test_multiple_filters_together(self):
        Task.objects.create(
            title="change sheets", status="todo", priority="low", project=self.p1
        )
        response = self.client.get(
            reverse("tasks", kwargs={"project_id": self.p1.id}),
            {"status": "todo", "priority": "low"},
        )
        assert len(response.data) == 2

    # Task Detail Tests
    def test_retrieve_own_task(self):
        response = self.client.get(
            reverse("single_task", kwargs={"project_id": self.p1.id, "pk": self.t1.id})
        )
        assert response.status_code == 200
        assert response.data["title"] == "clean room"
        assert response.data["due_date"] == "2026-05-21"

    def test_retrieve_task_from_other_project_returns_404(self):
        response = self.client.get(
            reverse("single_task", kwargs={"project_id": self.p1.id, "pk": self.t5.id})
        )
        assert response.status_code == 404

    def test_retrieve_task_from_other_user_project_returns_404(self):
        user = User.objects.create_user(
            username="testuser", email="testuser@gmail.com", password="testuser@123"
        )
        project = Project.objects.create(
            name="test project", description="test desc", owner=user
        )
        task = Task.objects.create(title="test title", project=project)
        response = self.client.get(
            reverse("single_task", kwargs={"project_id": project.id, "pk": task.id})
        )
        assert response.status_code == 404

    # Task Update Tests
    def test_update_own_task(self):
        payload = {
            "title": "updated title",
            "status": "todo",
            "priority": "low",
            "due_date": "2026-05-21",
        }
        response = self.client.put(
            reverse("single_task", kwargs={"project_id": self.p1.id, "pk": self.t1.id}),
            payload,
        )
        assert response.status_code == 200
        assert response.data["title"] == "updated title"
        assert response.data["id"] == self.t1.id

    def test_update_task_from_other_user_project_returns_404(self):
        user = User.objects.create_user(
            username="testuser", email="testuser@gmail.com", password="testuser@123"
        )
        project = Project.objects.create(
            name="test project", description="test desc", owner=user
        )
        task = Task.objects.create(title="test title", project=project)
        payload = {
            "title": "updated test title",
        }
        response = self.client.put(
            reverse("single_task", kwargs={"project_id": project.id, "pk": task.id}),
            payload,
        )
        assert response.status_code == 404

    # Task Delete Tests
    def test_delete_own_task(self):
        task = Task.objects.create(title="del title", project=self.p1)
        response = self.client.delete(
            reverse("single_task", kwargs={"project_id": self.p1.id, "pk": task.id})
        )
        assert response.status_code == 204
        assert not Task.objects.filter(id=task.id).exists()

    def test_delete_task_from_other_project_returns_404(self):
        user = User.objects.create_user(
            username="testuser", email="testuser@gmail.com", password="testuser@123"
        )
        project = Project.objects.create(
            name="test project", description="test desc", owner=user
        )
        task = Task.objects.create(title="test title", project=project)
        response = self.client.delete(
            reverse("single_task", kwargs={"project_id": project.id, "pk": task.id})
        )
        assert response.status_code == 404
