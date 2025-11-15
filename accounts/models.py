from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    preferred_course = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.username

