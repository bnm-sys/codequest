# Create your views here.
# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.views import View
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from courses.models import Course, Enrollment
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.conf import settings

class RegisterView(View):
    template_name = "accounts/register.html"

    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # normalize phone: ensure no spaces
            phone = form.cleaned_data.get("phone_number")
            if phone:
                user.phone_number = phone.strip()
            # if email provided, set
            email = form.cleaned_data.get("email")
            if email:
                user.email = email.strip().lower()
            user.save()
            
            # Send welcome email
            if user.email:
                try:
                    send_mail(
                        subject="Welcome to CodeQuest!",
                        message=f"Hi {user.username},\n\nWelcome to CodeQuest! We are excited to have you on board.\n\nBest,\nThe CodeQuest Team",
                        from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@codequest.com',
                        recipient_list=[user.email],
                        fail_silently=True,
                    )
                except Exception as e:
                    # Log error but don't stop registration
                    print(f"Failed to send email: {e}")

            login(request, user)
            messages.success(request, "Welcome! Your account has been created.")
            return redirect("dashboard")
        return render(request, self.template_name, {"form": form})

class CustomLoginView(LoginView):
    template_name = "accounts/login.html"

class CustomLogoutView(LogoutView):
    next_page = "login"

class DashboardView(LoginRequiredMixin, View):
    template_name = "accounts/dashboard.html"

    def get(self, request):
        # Courses block - list all courses for selection
        courses = Course.objects.all()
        # user's enrollments
        enrollments = request.user.enrollments.select_related('course').all()
        return render(request, self.template_name, {"courses": courses, "enrollments": enrollments})

class EnrollView(LoginRequiredMixin, View):
    def post(self, request, slug):
        course = Course.objects.filter(slug=slug).first()
        if not course:
            messages.error(request, "Course not found.")
            return redirect("dashboard")
        enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
        if created:
            messages.success(request, f"Enrolled in {course.title}")
        else:
            messages.info(request, f"Already enrolled in {course.title}")
        return redirect("learning_center", slug=course.slug)

class LearningCenterView(LoginRequiredMixin, View):
    template_name = "courses/learning_center.html"
    def get(self, request, slug):
        course = Course.objects.filter(slug=slug).first()
        if not course:
            messages.error(request, "Course not found.")
            return redirect("dashboard")
        enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
        return render(request, self.template_name, {"course": course, "enrollment": enrollment})
