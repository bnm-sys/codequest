# sandbox/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone


class SandboxSession(models.Model):
    """Tracks active Docker container sessions for users"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sandbox_sessions")
    container_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    challenge = models.ForeignKey('courses.Challenge', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ("-created_at",)
    
    def __str__(self):
        return f"{self.user.username} - {self.container_id or 'No Container'}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
