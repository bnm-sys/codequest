import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Seed demo users (learner and coach) with predictable credentials."

    def handle(self, *args, **options):
        password = os.getenv("DEMO_USER_PASSWORD", "DemoPass123!")
        users = [
            {
                "username": "demo-learner",
                "email": "learner@example.com",
                "role": "student",
                "display_name": "Demo Learner",
                "preferred_language": "en",
            },
            {
                "username": "demo-ai-coach",
                "email": "ai-coach@example.com",
                "role": "instructor",
                "display_name": "AI Coach",
                "preferred_language": "en",
            },
        ]

        for user_data in users:
            user, created = User.objects.update_or_create(
                username=user_data["username"],
                defaults={
                    "email": user_data["email"],
                    "role": user_data["role"],
                },
            )
            user.set_password(password)
            user.save()

            # Ensure profile fields are synced
            profile = user.profile
            profile.display_name = user_data["display_name"]
            profile.preferred_language = user_data["preferred_language"]
            profile.save()

            status = "created" if created else "updated"
            self.stdout.write(
                self.style.SUCCESS(
                    f"{status}: {user.username} ({user.role}) password='{password}'"
                )
            )

        self.stdout.write(self.style.SUCCESS("Demo users ready."))
