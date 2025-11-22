# codequest/views.py
from django.shortcuts import render

from courses.models import Course


def home_view(request):
    courses = Course.objects.all()

    return render(request, "home.html", {"courses": courses})
