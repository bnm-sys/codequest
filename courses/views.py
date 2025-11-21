from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils import timezone
from django.db.models import Prefetch

from .models import Course, Module, Challenge, Enrollment, UserChallengeAttempt
from django.db.models import Sum


def home(request):
    """Homepage listing active courses. Not authenticated by default."""
    courses = Course.objects.filter(is_active=True).order_by("-created_at")
    return render(request, "home.html", {"courses": courses})


def course_detail(request, slug):
    """Show course details and modules; provide enroll button if not enrolled."""
    course = get_object_or_404(Course, slug=slug)
    modules = course.modules.all().order_by("order")
    user_enrollment = None
    if request.user.is_authenticated:
        user_enrollment = Enrollment.objects.filter(user=request.user, course=course).first()

    return render(request, "courses/course_detail.html", {
        "course": course,
        "modules": modules,
        "enrollment": user_enrollment,
    })


@login_required
def enroll_in_course(request, slug):
    """Create or get enrollment and redirect to dashboard."""
    course = get_object_or_404(Course, slug=slug)
    enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
    if created:
        messages.success(request, f"Enrolled in {course.title}.")
    else:
        messages.info(request, f"You are already enrolled in {course.title}.")
    return redirect("courses:dashboard")


@login_required
def dashboard(request):
    """User-facing dashboard with enrollments, xp, streaks, and leaderboard snippets."""
    # Optimized: select_related to avoid N+1
    enrollments = Enrollment.objects.filter(user=request.user).select_related("course")
    
    # REMOVED: Dynamic calculate_progress loop. Rely on stored 'progress' field for read efficiency.

    # simple leaderboard example for each course (top 5)
    course_ids = [e.course_id for e in enrollments]
    leaderboards = {}
    if course_ids:
        for cid in course_ids:
            top = Enrollment.objects.filter(course_id=cid).order_by("-xp")[:5]
            leaderboards[cid] = top

    return render(request, "courses/dashboard.html", {
        "enrollments": enrollments,
        "leaderboards": leaderboards,
    })


def calculate_progress(enrollment):
    """Calculate percent of modules fully solved."""
    # Optimized: prefetch challenges to avoid N+1
    modules = enrollment.course.modules.prefetch_related('challenges')
    total = modules.count()
    if total == 0:
        return 0
    completed = 0
    
    # Get all solved challenge IDs for this user and course in one query
    solved_challenge_ids = set(UserChallengeAttempt.objects.filter(
        user=enrollment.user, 
        challenge__module__course=enrollment.course, 
        is_correct=True
    ).values_list("challenge_id", flat=True))

    for m in modules:
        challenge_ids = [c.id for c in m.challenges.all()]
        if not challenge_ids:
            continue
        
        if all(cid in solved_challenge_ids for cid in challenge_ids):
            completed += 1
            
    return int((completed / total) * 100)


@login_required
def learning_center(request, slug):
    """Return next active module + next challenge for the user."""
    course = get_object_or_404(Course, slug=slug)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    
    # Optimized: Prefetch modules and challenges
    modules = course.modules.prefetch_related('challenges').order_by("order")
    
    if not modules.exists():
        messages.warning(request, "This course has no modules yet.")
        return redirect("courses:dashboard")

    # Optimized: Fetch all solved challenges for this course once
    solved_challenge_ids = set(UserChallengeAttempt.objects.filter(
        user=request.user, 
        challenge__module__course=course, 
        is_correct=True
    ).values_list("challenge_id", flat=True))

    active_module = None
    next_challenge = None

    for m in modules:
        challenges = m.challenges.all()
        if not challenges:
            continue
            
        module_challenge_ids = [c.id for c in challenges]
        is_complete = all(cid in solved_challenge_ids for cid in module_challenge_ids)
        
        if not is_complete:
            active_module = m
            for c in challenges:
                if c.id not in solved_challenge_ids:
                    next_challenge = c
                    break
            break

    if active_module is None:
        messages.success(request, "You have completed the course!")
        return redirect("courses:dashboard")

    return render(request, "courses/learning_center.html", {
        "course": course,
        "active_module": active_module,
        "challenge": next_challenge,
        "enrollment": enrollment,
    })


@login_required
def attempt_challenge(request, challenge_id):
    """Accept POST with 'answer' and optional 'time_seconds' then evaluate and update enrollment XP/streak."""
    challenge = get_object_or_404(Challenge, id=challenge_id)
    course = challenge.module.course
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)

    if request.method != "POST":
        return redirect("courses:learning_center", slug=course.slug)

    user_answer = request.POST.get("answer", "").strip()
    try:
        time_seconds = int(request.POST.get("time_seconds", 0))
    except (ValueError, TypeError):
        time_seconds = 0

    is_correct = (user_answer == challenge.expected_output.strip())

    prev_attempts = UserChallengeAttempt.objects.filter(user=request.user, challenge=challenge).count()
    UserChallengeAttempt.objects.create(
        user=request.user,
        challenge=challenge,
        is_correct=is_correct,
        attempt_no=prev_attempts + 1,
        time_seconds=time_seconds,
    )

    if is_correct:
        earned_xp = challenge.module.points
        enrollment.xp = (enrollment.xp or 0) + earned_xp
        enrollment.streak = (enrollment.streak or 0) + 1
        messages.success(request, f"Correct — +{earned_xp} XP. Streak +1.")
    else:
        enrollment.streak = 0
        messages.error(request, "Incorrect — try again!")

    enrollment.progress = calculate_progress(enrollment)
    enrollment.save()

    return redirect("courses:learning_center", slug=course.slug)
