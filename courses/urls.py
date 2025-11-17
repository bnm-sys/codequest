# courses/urls.py
from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    path("", views.home, name="home_redirect"),         # optional: /courses/ to view courses
    path("dashboard/", views.dashboard, name="dashboard"),
    path("<slug:slug>/", views.course_detail, name="course_detail"),
    path("<slug:slug>/enroll/", views.enroll_in_course, name="enroll"),
    path("<slug:slug>/learning-center/", views.learning_center, name="learning_center"),
    path("challenge/<int:challenge_id>/attempt/", views.attempt_challenge, name="attempt_challenge"),
]
