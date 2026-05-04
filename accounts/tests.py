import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestAuth:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="peter", email="parker@gmail.com", password="peter@parker"
        )

    # Registration tests
    def test_register_success(self):
        payload = {
            "username": "copyninja",
            "email": "hatake@gmail.com",
            "password": "chiDori@123",
        }
        response = self.client.post(reverse("register"), payload)
        assert response.status_code == 201
        user = User.objects.get(username="copyninja")
        assert user.email == "hatake@gmail.com"
        assert user.password != "chiDori@123"
        assert "password" not in response.data

    def test_register_missing_username(self):
        payload = {"email": "hatake@gmail.com", "password": "chiDori@123"}
        response = self.client.post(reverse("register"), payload)
        assert response.status_code == 400

    def test_register_missing_password(self):
        payload = {
            "username": "copyninja",
            "email": "hatake@gmail.com",
        }
        response = self.client.post(reverse("register"), payload)
        assert response.status_code == 400

    def test_register_duplicate_username(self):
        payload = {
            "username": "peter",
            "email": "peter@gmail.com",
            "password": "peter@123",
        }
        response = self.client.post(reverse("register"), payload)
        assert response.status_code == 400

    def test_register_duplicate_email(self):
        payload = {
            "username": "parker",
            "email": "parker@gmail.com",
            "password": "peter@123",
        }
        response = self.client.post(reverse("register"), payload)
        assert response.status_code == 400

    def test_register_invalid_email(self):
        payload = {"username": "w0lf", "email": "sekiro", "password": "onearmedwolf"}
        response = self.client.post(reverse("register"), payload)
        assert response.status_code == 400

    # Login tests
    def test_login_success(self):
        payload = {"username": "peter", "password": "peter@parker"}
        response = self.client.post(reverse("login"), payload)
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_wrong_password(self):
        payload = {"username": "peter", "password": "peterparker"}
        response = self.client.post(reverse("login"), payload)
        assert response.status_code == 401

    def test_login_nonexistent_user(self):
        payload = {"username": "mark", "password": "mark@123"}
        response = self.client.post(reverse("login"), payload)
        assert response.status_code == 401

    # Token refresh tests
    def test_refresh_success(self):
        payload1 = {"username": "peter", "password": "peter@parker"}
        response1 = self.client.post(reverse("login"), payload1)
        payload2 = {"refresh": response1.data["refresh"]}
        response2 = self.client.post(reverse("token_refresh"), payload2)
        assert response2.status_code == 200
        assert "access" in response2.data

    def test_refresh_invalid_token(self):
        payload = {"refresh": "invalidtoken"}
        response = self.client.post(reverse("token_refresh"), payload)
        assert response.status_code == 401

    # Protected endpoint tests
    def test_projects_endpoint_requires_auth(self):
        response = self.client.get(reverse("projects"))
        assert response.status_code == 401

    def test_projects_endpoint_with_valid_token(self):
        payload = {"username": "peter", "password": "peter@parker"}
        response1 = self.client.post(reverse("login"), payload)
        token = response1.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response2 = self.client.get(reverse("projects"))
        assert response2.status_code == 200
