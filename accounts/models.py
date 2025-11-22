# accounts/models.py
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=16, blank=True, null=True)
    preferred_course = models.CharField(max_length=50, blank=True, null=True)
    # role if needed
    ROLE_CHOICES = [
        ("student", "Student"),
        ("instructor", "Instructor"),
        ("admin", "Admin"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=80, blank=True)
    preferred_language = models.CharField(
        max_length=5, choices=[("en", "English"), ("ne", "Nepali")], default="en"
    )
    xp = models.PositiveIntegerField(default=0)
    completed_challenges = models.PositiveIntegerField(default=0)
    current_streak = models.PositiveIntegerField(default=0)
    last_active = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, display_name=instance.username)
    else:
        instance.profile.save()
