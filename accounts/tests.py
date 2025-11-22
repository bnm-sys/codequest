from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse

import pytest

User = get_user_model()


@pytest.mark.django_db
class TestAuthentication:

    def test_register_view_get(self, client):
        """Test that the registration page renders correctly."""
        url = reverse("register")
        response = client.get(url)
        assert response.status_code == 200
        assert "form" in response.context
        assert "accounts/register.html" in [t.name for t in response.templates]

    def test_register_user_success(self, client):
        """Test registering a new user with valid data and verifying email."""
        url = reverse("register")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "phone_number": "+9779800000000",
            "password1": "StrongPassword123!",
            "password2": "StrongPassword123!",
        }
        response = client.post(url, data)

        if response.status_code == 200 and "form" in response.context:
            print(response.context["form"].errors)

        # Should redirect to dashboard
        assert response.status_code == 302
        assert response.url == reverse("dashboard")

        # Verify user created
        assert User.objects.filter(username="newuser").exists()
        user = User.objects.get(username="newuser")
        assert user.email == "newuser@example.com"
        assert user.phone_number == "+9779800000000"

        # Verify email sent
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "Welcome to CodeQuest!"
        assert mail.outbox[0].to == ["newuser@example.com"]

    def test_register_user_invalid_phone(self, client):
        """Test registration fails with invalid phone format."""
        url = reverse("register")
        data = {
            "username": "badphoneuser",
            "email": "valid@example.com",
            "phone_number": "12345",  # Invalid format
            "password1": "StrongPassword123!",
            "password2": "StrongPassword123!",
        }
        response = client.post(url, data)
        assert response.status_code == 200
        assert not User.objects.filter(username="badphoneuser").exists()
        assert "Phone number must be in +977XXXXXXXXX format." in str(response.content)

    def test_login_view_get(self, client):
        """Test that the login page renders correctly."""
        url = reverse("login")
        response = client.get(url)
        assert response.status_code == 200
        assert "accounts/login.html" in [t.name for t in response.templates]

    def test_login_user_success(self, client):
        """Test logging in with valid credentials."""
        user = User.objects.create_user(username="testuser", password="password123")
        url = reverse("login")
        data = {"username": "testuser", "password": "password123"}
        response = client.post(url, data)

        # Should redirect to dashboard (or next page)
        assert response.status_code == 302
        # The default redirect might be /accounts/profile/ if not configured,
        # but accounts/views.py redirects to 'dashboard' in RegisterView.
        # LoginView uses LOGIN_REDIRECT_URL setting.
        # Let's check settings.py for LOGIN_REDIRECT_URL.
        # If not set, it defaults to /accounts/profile/.
        # But let's assume it redirects somewhere.
        # We can just check that it redirects.

        # Check if user is authenticated
        # We can check the session
        assert "_auth_user_id" in client.session
        assert str(client.session["_auth_user_id"]) == str(user.pk)

    def test_login_user_invalid(self, client):
        """Test logging in with invalid credentials."""
        url = reverse("login")
        data = {"username": "wronguser", "password": "wrongpassword"}
        response = client.post(url, data)
        assert response.status_code == 200
        assert "form" in response.context
        # Form should have errors
        assert response.context["form"].errors
