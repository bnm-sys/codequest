# courses/models.py
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.postgres.fields import JSONField  # if using Postgres; fallback below

# If you use sqlite in dev and don't have Postgres, use models.JSONField (Django 3.1+)
try:
    from django.contrib.postgres.fields import JSONField as PGJSONField
except Exception:
    PGJSONField = models.JSONField


class Course(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # convenience admin reporting
    def __str__(self):
        return self.title

    @property
    def total_enrolled(self):
        return self.enrollments.count()

    @property
    def total_xp_awarded(self):
        return self.enrollments.aggregate(total=models.Sum("xp"))["total"] or 0


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=150)
    order = models.PositiveIntegerField(default=1)
    content = models.TextField(blank=True)        # markdown stored as text
    points = models.PositiveIntegerField(default=10)
    skill_tags = PGJSONField(default=dict, blank=True)  # e.g. {"filesystem": 1}
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} — {self.title}"


class Challenge(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="challenges")
    title = models.CharField(max_length=200, blank=True)
    prompt = models.TextField()
    expected_output = models.TextField()
    difficulty = models.CharField(max_length=20, default="easy")  # easy|medium|hard
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (self.title or f"Challenge for {self.module.title}")[:80]

    @property
    def total_attempts(self):
        return self.userchallengeattempt_set.count()

    @property
    def correct_attempts(self):
        return self.userchallengeattempt_set.filter(is_correct=True).count()


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)

    # Gamification & progress tracking
    progress = models.PositiveIntegerField(default=0)   # percent
    streak = models.PositiveIntegerField(default=0)
    xp = models.PositiveIntegerField(default=0)

    # per-skill mastery scores for adaptive algorithm
    mastery = PGJSONField(default=dict, blank=True)  # e.g. {"filesystem": 45, "git": 10}

    class Meta:
        unique_together = ("user", "course")
        ordering = ("-enrolled_at",)

    def __str__(self):
        return f"{self.user} → {self.course.title}"

    @property
    def total_attempts(self):
        return UserChallengeAttempt.objects.filter(
            user=self.user, challenge__module__course=self.course
        ).count()

    @property
    def total_minutes_spent(self):
        # conservative default: sum up stored time_per_attempt on attempts
        total_seconds = UserChallengeAttempt.objects.filter(
            user=self.user, challenge__module__course=self.course
        ).aggregate(total=models.Sum("time_seconds"))["total"] or 0
        return int(total_seconds / 60)


class UserChallengeAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    attempt_no = models.PositiveIntegerField(default=1)

    # measured duration for this attempt (seconds). set in view when evaluating attempt.
    time_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("-submitted_at",)

    def __str__(self):
        return f"{self.user} attempt {self.attempt_no} on {self.challenge_id}"
