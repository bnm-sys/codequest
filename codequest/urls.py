# codequest/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from courses.views import home

urlpatterns = [
    path("", home, name="home"),  # front page served by courses.home
    path("admin/", admin.site.urls),

    # authentication (login uses custom template)
    path("accounts/login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),

    path("accounts/", include("accounts.urls")),  # registration, profile
    path("courses/", include("courses.urls")),
]
