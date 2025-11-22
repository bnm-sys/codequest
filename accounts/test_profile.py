from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.urls import reverse

import pytest

User = get_user_model()


@pytest.mark.django_db
class TestProfileFeatures:

    def test_profile_created_on_user_registration(self, client):
        """Test that a profile is automatically created when a user registers."""
        url = reverse("register")
        data = {
            "username": "profileuser",
            "email": "profileuser@example.com",
            "phone_number": "+9779800000010",
            "display_name": "Profile User",
            "preferred_language": "en",
            "password1": "StrongPassword123!",
            "password2": "StrongPassword123!",
        }

        response = client.post(url, data)

        # Check if registration succeeded
        if response.status_code != 302:
            print(
                f"Form errors: {response.context.get('form').errors if 'form' in response.context else 'No form in context'}"
            )

        assert response.status_code == 302
        user = User.objects.get(username="profileuser")
        assert hasattr(user, "profile")
        assert user.profile.display_name == "Profile User"
        assert user.profile.preferred_language == "en"

    def test_profile_display_name_defaults_to_username(self, client):
        """Test that display_name defaults to username if not provided."""
        url = reverse("register")
        data = {
            "username": "defaultnameuser",
            "email": "defaultname@example.com",
            "phone_number": "+9779800000011",
            "display_name": "",  # Empty display name
            "preferred_language": "ne",
            "password1": "StrongPassword123!",
            "password2": "StrongPassword123!",
        }

        response = client.post(url, data)

        assert response.status_code == 302
        user = User.objects.get(username="defaultnameuser")
        assert user.profile.display_name == "defaultnameuser"
        assert user.profile.preferred_language == "ne"

    def test_profile_preferred_language_choices(self, client):
        """Test that preferred_language accepts valid choices."""
        url = reverse("register")

        # Test English
        data_en = {
            "username": "englishuser",
            "email": "english@example.com",
            "phone_number": "+9779800000012",
            "preferred_language": "en",
            "password1": "StrongPassword123!",
            "password2": "StrongPassword123!",
        }
        response = client.post(url, data_en)
        assert response.status_code == 302
        user_en = User.objects.get(username="englishuser")
        assert user_en.profile.preferred_language == "en"

        # Test Nepali
        data_ne = {
            "username": "nepaliuser",
            "email": "nepali@example.com",
            "phone_number": "+9779800000013",
            "preferred_language": "ne",
            "password1": "StrongPassword123!",
            "password2": "StrongPassword123!",
        }
        response = client.post(url, data_ne)
        assert response.status_code == 302
        user_ne = User.objects.get(username="nepaliuser")
        assert user_ne.profile.preferred_language == "ne"


@pytest.mark.django_db
class TestSeedDemoUsers:

    def test_seed_demo_users_command(self):
        """Test that seed_demo_users command creates demo users."""
        out = StringIO()
        call_command("seed_demo_users", stdout=out)

        # Check output
        output = out.getvalue()
        assert "demo-learner" in output
        assert "demo-ai-coach" in output
        assert "Demo users ready" in output

        # Verify users created
        learner = User.objects.get(username="demo-learner")
        ai_coach = User.objects.get(username="demo-ai-coach")

        assert learner.role == "student"
        assert ai_coach.role == "instructor"
        assert learner.email == "learner@example.com"
        assert ai_coach.email == "ai-coach@example.com"

        # Verify profiles
        assert learner.profile.display_name == "Demo Learner"
        assert learner.profile.preferred_language == "en"
        assert ai_coach.profile.display_name == "AI Coach"
        assert ai_coach.profile.preferred_language == "en"

        # Verify password
        assert learner.check_password("DemoPass123!")
        assert ai_coach.check_password("DemoPass123!")

    def test_seed_demo_users_idempotent(self):
        """Test that running seed_demo_users multiple times is safe."""
        # Run first time
        call_command("seed_demo_users", stdout=StringIO())
        first_learner = User.objects.get(username="demo-learner")
        first_id = first_learner.id

        # Run second time
        out = StringIO()
        call_command("seed_demo_users", stdout=out)

        # Should update, not create
        assert "updated" in out.getvalue()

        second_learner = User.objects.get(username="demo-learner")
        assert second_learner.id == first_id  # Same user
        assert User.objects.filter(username="demo-learner").count() == 1


@pytest.mark.django_db
class TestUserRoles:

    def test_user_role_default_is_student(self):
        """Test that default role is student."""
        user = User.objects.create_user(username="defaultrole", password="pass123")
        assert user.role == "student"

    def test_user_role_choices(self):
        """Test that role choices work correctly."""
        student = User.objects.create_user(
            username="student1", password="pass123", role="student"
        )
        instructor = User.objects.create_user(
            username="instructor1", password="pass123", role="instructor"
        )
        admin = User.objects.create_user(
            username="admin1", password="pass123", role="admin"
        )

        assert student.role == "student"
        assert instructor.role == "instructor"
        assert admin.role == "admin"
