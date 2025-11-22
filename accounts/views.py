# Create your views here.
# accounts/views.py
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views import View

from courses.models import Course, Enrollment

from .forms import CustomUserCreationForm


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

            display_name = form.cleaned_data.get("display_name") or user.username
            preferred_language = form.cleaned_data.get("preferred_language") or "en"
            # ensure profile exists then update preferences
            profile = user.profile
            profile.display_name = display_name
            profile.preferred_language = preferred_language
            profile.save()

            # Send welcome email
            if user.email:
                try:
                    send_mail(
                        subject=_("Welcome to CodeQuest!"),
                        message=_(
                            "Hi %(user)s,\n\nWelcome to CodeQuest! We are excited to have you on board.\n\nBest,\nThe CodeQuest Team"
                        )
                        % {"user": user.username},
                        from_email=(
                            settings.DEFAULT_FROM_EMAIL
                            if hasattr(settings, "DEFAULT_FROM_EMAIL")
                            else "noreply@codequest.com"
                        ),
                        recipient_list=[user.email],
                        fail_silently=True,
                    )
                except Exception as e:
                    # Log error but don't stop registration
                    print(f"Failed to send email: {e}")

            login(request, user)
            messages.success(
                request,
                _("Welcome! Your account has been created."),
            )
            return redirect("dashboard")
        return render(request, self.template_name, {"form": form})


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"


class CustomLogoutView(LogoutView):
    next_page = "login"


class DashboardView(LoginRequiredMixin, View):
    template_name = "courses/dashboard.html"

    def get(self, request):
        # Courses block - list all courses for selection
        courses = Course.objects.all()
        # user's enrollments
        enrollments = request.user.enrollments.select_related("course").all()
        return render(
            request,
            self.template_name,
            {"courses": courses, "enrollments": enrollments},
        )


class EnrollView(LoginRequiredMixin, View):
    def post(self, request, slug):
        course = Course.objects.filter(slug=slug).first()
        if not course:
            messages.error(request, _("Course not found."))
            return redirect("dashboard")
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user, course=course
        )
        if created:
            messages.success(
                request, _("Enrolled in %(course)s") % {"course": course.title}
            )
        else:
            messages.info(
                request, _("Already enrolled in %(course)s") % {"course": course.title}
            )
        return redirect("learning_center", slug=course.slug)


class LearningCenterView(LoginRequiredMixin, View):
    template_name = "courses/learning_center.html"

    def get(self, request, slug):
        course = Course.objects.filter(slug=slug).first()
        if not course:
            messages.error(request, _("Course not found."))
            return redirect("dashboard")
        enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
        return render(
            request, self.template_name, {"course": course, "enrollment": enrollment}
        )


class ProfileView(LoginRequiredMixin, View):
    template_name = "accounts/profile.html"

    def get(self, request):
        # Get user's enrollments with course info and calculate total XP
        enrollments = (
            Enrollment.objects.filter(user=request.user)
            .select_related("course")
            .order_by("-xp")
        )

        total_xp = sum(e.xp or 0 for e in enrollments)
        max_streak = max((e.streak or 0 for e in enrollments), default=0)

        # Calculate total challenges completed
        from courses.models import UserChallengeAttempt

        total_challenges = UserChallengeAttempt.objects.filter(
            user=request.user, is_correct=True
        ).count()

        return render(
            request,
            self.template_name,
            {
                "enrollments": enrollments,
                "total_xp": total_xp,
                "max_streak": max_streak,
                "total_challenges": total_challenges,
            },
        )
