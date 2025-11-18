# gamification/signals.py
"""
Signals to automatically award achievements when criteria are met
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from courses.models import UserChallengeAttempt, Enrollment
from accounts.models import Profile
from .models import Achievement, UserAchievement


@receiver(post_save, sender=UserChallengeAttempt)
def check_achievements_on_attempt(sender, instance, created, **kwargs):
    """Check and award achievements when a challenge is completed"""
    if not created or not instance.is_correct:
        return
    
    user = instance.user
    
    # Check challenge completion achievements
    total_completed = UserChallengeAttempt.objects.filter(
        user=user,
        is_correct=True
    ).values('challenge').distinct().count()
    
    # Award milestone achievements
    milestones = [10, 25, 50, 100, 250, 500]
    for milestone in milestones:
        if total_completed == milestone:
            achievement, _ = Achievement.objects.get_or_create(
                name=f"Challenge Master {milestone}",
                defaults={
                    'description': f"Completed {milestone} challenges",
                    'xp_reward': milestone * 10,
                    'icon': '🎯'
                }
            )
            UserAchievement.objects.get_or_create(
                user=user,
                achievement=achievement
            )
    
    # Check XP milestones
    profile = Profile.objects.get(user=user)
    xp_milestones = [1000, 5000, 10000, 25000, 50000]
    for xp_milestone in xp_milestones:
        if profile.xp >= xp_milestone:
            achievement, _ = Achievement.objects.get_or_create(
                name=f"XP Master {xp_milestone//1000}K",
                defaults={
                    'description': f"Earned {xp_milestone} XP",
                    'xp_reward': 0,  # Already earned the XP
                    'icon': '⭐'
                }
            )
            UserAchievement.objects.get_or_create(
                user=user,
                achievement=achievement
            )


@receiver(post_save, sender=Enrollment)
def check_course_completion_achievement(sender, instance, created, **kwargs):
    """Award achievement when course is completed"""
    if instance.progress >= 100:
        achievement, _ = Achievement.objects.get_or_create(
            name=f"{instance.course.title} Master",
            defaults={
                'description': f"Completed {instance.course.title} course",
                'xp_reward': 500,
                'icon': '🏆'
            }
        )
        UserAchievement.objects.get_or_create(
            user=instance.user,
            achievement=achievement
        )

