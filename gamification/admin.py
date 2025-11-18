# gamification/admin.py
from django.contrib import admin
from .models import Achievement, UserAchievement, SkillMastery


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'xp_reward', 'skill_tag', 'icon')
    search_fields = ('name', 'description', 'skill_tag')
    list_filter = ('skill_tag',)


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'earned_at', 'notified')
    list_filter = ('achievement', 'earned_at', 'notified')
    search_fields = ('user__username', 'achievement__name')
    readonly_fields = ('earned_at',)


@admin.register(SkillMastery)
class SkillMasteryAdmin(admin.ModelAdmin):
    list_display = ('user', 'skill_tag', 'theta', 'mastery_percentage', 'attempts', 'correct_attempts', 'last_updated')
    list_filter = ('skill_tag', 'last_updated')
    search_fields = ('user__username', 'skill_tag')
    readonly_fields = ('last_updated', 'mastery_percentage')
    ordering = ('-theta',)
