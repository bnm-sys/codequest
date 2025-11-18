# gamification/urls.py
from django.urls import path
from .views import leaderboard, achievements, skill_mastery

urlpatterns = [
    path('leaderboard/', leaderboard, name='leaderboard'),
    path('achievements/', achievements, name='achievements'),
    path('skill-mastery/', skill_mastery, name='skill_mastery'),
]

