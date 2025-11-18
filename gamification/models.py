# gamification/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone


class Achievement(models.Model):
    """Represents a badge or achievement that can be earned"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default="🏆")  # Emoji or icon name
    xp_reward = models.PositiveIntegerField(default=0)
    skill_tag = models.CharField(max_length=50, blank=True, null=True)  # Optional skill association
    criteria = models.JSONField(default=dict, blank=True)  # Conditions to unlock

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    """Tracks which users have earned which achievements"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="achievements_earned")
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name="users_earned")
    earned_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "achievement")
        ordering = ("-earned_at",)

    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"


class SkillMastery(models.Model):
    """Tracks IRT-based skill mastery for each user"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="skill_masteries")
    skill_tag = models.CharField(max_length=50, db_index=True)  # e.g., "git-clone", "ls-a"
    theta = models.FloatField(default=0.0)  # IRT ability parameter
    attempts = models.PositiveIntegerField(default=0)
    correct_attempts = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "skill_tag")
        ordering = ("-theta",)

    def __str__(self):
        return f"{self.user.username} - {self.skill_tag} (θ={self.theta:.2f})"

    @property
    def mastery_percentage(self):
        """Convert theta to a 0-100 mastery percentage"""
        # IRT theta typically ranges from -3 to +3
        # Normalize to 0-100
        normalized = (self.theta + 3) / 6
        return max(0, min(100, int(normalized * 100)))
