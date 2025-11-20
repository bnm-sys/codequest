# codequest/urls.py
from django.contrib import admin
from django.urls import path, include
from courses.views import home
from accounts.views import CustomLoginView, CustomLogoutView

urlpatterns = [
    path("", home, name="home"),  # front page served by courses.home
    path("admin/", admin.site.urls),

    # authentication
    path("accounts/login/", CustomLoginView.as_view(), name="login"),
    path("accounts/logout/", CustomLogoutView.as_view(), name="logout"),

    path("accounts/", include("accounts.urls")),  # registration, profile
    path("courses/", include("courses.urls")),
    path("sandbox/", include("sandbox.urls")),  # sandbox API
    path("gamification/", include("gamification.urls")),  # achievements, leaderboard
]
