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
            login(request, user)
            messages.success(request, "Welcome! Your account has been created.")
            return redirect("dashboard")
        return render(request, self.template_name, {"form": form})

class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return '/accounts/dashboard/'

class CustomLogoutView(LogoutView):
    """
    Allows GET logouts and flashes a timed confirmation before redirecting home.
    """
    next_page = "home"

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.success(self.request, "Successfully logged out. See you on your next mission!")
        return response

    def get(self, request, *args, **kwargs):
        """
        Support GET requests coming from navbar links by delegating to POST logic.
        """
        return self.post(request, *args, **kwargs)

class DashboardView(LoginRequiredMixin, View):
    template_name = "courses/dashboard.html"

    def get(self, request):
        from courses.views import calculate_progress
        
        # Courses block - list all courses for selection
        courses = Course.objects.all()
        # user's enrollments
        enrollments = request.user.enrollments.select_related('course').all()
        
        # Compute progress dynamically
        for enr in enrollments:
            enr.progress = calculate_progress(enr)
        
        # Leaderboard snippets for each course
        course_ids = [e.course_id for e in enrollments]
        leaderboards = {}
        if course_ids:
            for cid in course_ids:
                top = Enrollment.objects.filter(course_id=cid).order_by("-xp")[:5]
                leaderboards[cid] = top
        
        return render(request, self.template_name, {
            "courses": courses, 
            "enrollments": enrollments,
            "leaderboards": leaderboards,
        })

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
        return redirect("courses:learning_center", slug=course.slug)

class LearningCenterView(LoginRequiredMixin, View):
    template_name = "courses/learning_center.html"
    def get(self, request, slug):
        course = Course.objects.filter(slug=slug).first()
        if not course:
            messages.error(request, "Course not found.")
            return redirect("dashboard")
        enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
        return render(request, self.template_name, {"course": course, "enrollment": enrollment})
