# gamification/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from .models import Achievement, UserAchievement, SkillMastery
from accounts.models import CustomUser
from courses.models import Enrollment


@login_required
def leaderboard(request):
    """Display leaderboard sorted by XP"""
    # Total XP leaderboard
    leaderboard_data = CustomUser.objects.filter(
        profile__xp__gt=0
    ).annotate(
        total_xp=Sum('enrollments__xp')
    ).order_by('-total_xp')[:100]
    
    # Skill-specific leaderboards
    skill_leaderboards = {}
    skill_tags = SkillMastery.objects.values_list('skill_tag', flat=True).distinct()
    for skill_tag in skill_tags[:5]:  # Top 5 skills
        skill_leaderboards[skill_tag] = SkillMastery.objects.filter(
            skill_tag=skill_tag
        ).order_by('-theta')[:10]
    
    # User's rank
    user_total_xp = request.user.enrollments.aggregate(total=Sum('xp'))['total'] or 0
    user_rank = CustomUser.objects.filter(
        enrollments__xp__gt=user_total_xp
    ).distinct().count() + 1
    
    return render(request, 'gamification/leaderboard.html', {
        'leaderboard': leaderboard_data,
        'skill_leaderboards': skill_leaderboards,
        'user_rank': user_rank,
        'user_xp': user_total_xp,
    })


@login_required
def achievements(request):
    """Display user's achievements and available badges"""
    user_achievements = UserAchievement.objects.filter(user=request.user).select_related('achievement')
    all_achievements = Achievement.objects.all()
    earned_ids = set(user_achievements.values_list('achievement_id', flat=True))
    
    # Categorize achievements
    earned = [ua.achievement for ua in user_achievements]
    available = [a for a in all_achievements if a.id not in earned_ids]
    
    return render(request, 'gamification/achievements.html', {
        'earned_achievements': earned,
        'available_achievements': available,
        'total_earned': len(earned),
        'total_available': len(all_achievements),
    })


@login_required
def skill_mastery(request):
    """Display user's skill mastery levels"""
    masteries = SkillMastery.objects.filter(user=request.user).order_by('-theta')
    
    return render(request, 'gamification/skill_mastery.html', {
        'masteries': masteries,
    })
