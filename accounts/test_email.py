from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse

import pytest

User = get_user_model()


@pytest.mark.django_db
class TestEmailFunctionality:

    def test_welcome_email_sent_on_registration(self, client):
        """Test that a welcome email is sent when a user registers."""
        url = reverse("register")
        data = {
            "username": "emailuser",
            "email": "emailuser@example.com",
            "phone_number": "+9779800000001",
            "password1": "StrongPassword123!",
            "password2": "StrongPassword123!",
        }

        # Clear any existing emails
        mail.outbox = []

        response = client.post(url, data)

        # Verify registration succeeded
        assert response.status_code == 302
        assert User.objects.filter(username="emailuser").exists()

        # Verify email was sent
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.subject == "Welcome to CodeQuest!"
        assert email.to == ["emailuser@example.com"]
        assert "emailuser" in email.body
        assert "Welcome to CodeQuest" in email.body

    def test_no_email_sent_without_email_address(self, client):
        """Test that no email is sent when user registers without email."""
        url = reverse("register")
        data = {
            "username": "noemailuser",
            "email": "",
            "phone_number": "+9779800000002",
            "password1": "StrongPassword123!",
            "password2": "StrongPassword123!",
        }

        # Clear any existing emails
        mail.outbox = []

        response = client.post(url, data)

        # Verify registration succeeded
        assert response.status_code == 302
        assert User.objects.filter(username="noemailuser").exists()

        # Verify no email was sent
        assert len(mail.outbox) == 0

    def test_email_failure_does_not_block_registration(self, client, settings):
        """Test that email sending failure doesn't prevent registration."""
        # Set invalid email backend to simulate failure
        settings.EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"

        url = reverse("register")
        data = {
            "username": "failemailuser",
            "email": "failemailuser@example.com",
            "phone_number": "+9779800000003",
            "password1": "StrongPassword123!",
            "password2": "StrongPassword123!",
        }

        response = client.post(url, data)

        # Verify registration succeeded despite email failure
        assert response.status_code == 302
        assert User.objects.filter(username="failemailuser").exists()
