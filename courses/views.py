# courses/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils import timezone

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
    enrollments = Enrollment.objects.filter(user=request.user).select_related("course")
    # compute progress dynamically
    for enr in enrollments:
        enr.progress = calculate_progress(enr)

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
    modules = enrollment.course.modules.all()
    total = modules.count()
    if total == 0:
        return 0
    completed = 0
    for m in modules:
        total_challenges = m.challenges.count()
        if total_challenges == 0:
            # treat empty modules as not counting towards completion
            continue
        solved = UserChallengeAttempt.objects.filter(
            user=enrollment.user, challenge__module=m, is_correct=True
        ).values("challenge").distinct().count()
        if solved >= total_challenges:
            completed += 1
    return int((completed / total) * 100)


@login_required
def learning_center(request, slug):
    """Return next active module + next challenge for the user."""
    course = get_object_or_404(Course, slug=slug)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    modules = course.modules.all().order_by("order")
    if not modules.exists():
        messages.warning(request, "This course has no modules yet.")
        return redirect("courses:dashboard")

    # find first module with incomplete challenges
    active_module = None
    for m in modules:
        total_challenges = m.challenges.count()
        if total_challenges == 0:
            continue
        solved_count = UserChallengeAttempt.objects.filter(
            user=request.user, challenge__module=m, is_correct=True
        ).values("challenge").distinct().count()
        if solved_count < total_challenges:
            active_module = m
            break

    if active_module is None:
        messages.success(request, "You have completed the course!")
        return redirect("courses:dashboard")

    # Use IRT to recommend next challenge
    from gamification.irt_engine import IRTEngine
    
    solved_ids = UserChallengeAttempt.objects.filter(
        user=request.user, is_correct=True, challenge__module=active_module
    ).values_list("challenge_id", flat=True)
    available_challenges = active_module.challenges.exclude(id__in=solved_ids).order_by('order')
    
    # Get skill tag from module if available
    skill_tag = None
    if active_module.skill_tags and isinstance(active_module.skill_tags, dict):
        skill_tags_list = list(active_module.skill_tags.keys())
        if skill_tags_list:
            skill_tag = skill_tags_list[0]  # Use first skill tag
    
    # Use IRT recommendation if available
    next_challenge = IRTEngine.recommend_next_challenge(
        user=request.user,
        available_challenges=available_challenges,
        skill_tag=skill_tag
    )
    
    # Fallback to first available if IRT didn't recommend
    if not next_challenge:
        next_challenge = available_challenges.first()

    return render(request, "courses/learning_center.html", {
        "course": course,
        "active_module": active_module,
        "challenge": next_challenge,
        "enrollment": enrollment,
    })


@login_required
def attempt_challenge(request, challenge_id):
    """Accept POST with 'answer' and optional 'time_seconds' then evaluate and update enrollment XP/streak."""
    from sandbox.evaluator import OutputEvaluator
    from gamification.irt_engine import IRTEngine
    from accounts.models import Profile
    
    challenge = get_object_or_404(Challenge, id=challenge_id)
    course = challenge.module.course
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)

    if request.method != "POST":
        return redirect("courses:learning_center", slug=course.slug)

    user_answer = request.POST.get("answer", "").strip()
    # time posted by front-end in seconds (optional)
    try:
        time_seconds = int(request.POST.get("time_seconds", 0))
    except (ValueError, TypeError):
        time_seconds = 0

    # Use evaluator to check correctness
    evaluator = OutputEvaluator()
    is_correct, feedback = evaluator.evaluate_challenge(user_answer, challenge)

    prev_attempts = UserChallengeAttempt.objects.filter(user=request.user, challenge=challenge).count()
    attempt = UserChallengeAttempt.objects.create(
        user=request.user,
        challenge=challenge,
        is_correct=is_correct,
        attempt_no=prev_attempts + 1,
        time_seconds=time_seconds,
    )

    # Update IRT skill mastery if skill tags exist
    if challenge.module.skill_tags and isinstance(challenge.module.skill_tags, dict):
        difficulty_map = {'easy': -1.0, 'medium': 0.0, 'hard': 1.0, 'expert': 2.0}
        challenge_difficulty = difficulty_map.get(challenge.difficulty.lower(), 0.0)
        
        for skill_tag in challenge.module.skill_tags.keys():
            IRTEngine.update_skill_mastery(
                user=request.user,
                skill_tag=skill_tag,
                is_correct=is_correct,
                challenge_difficulty=challenge_difficulty,
                challenge_discrimination=1.0
            )

    # XP and streak rules
    if is_correct:
        earned_xp = challenge.module.points
        enrollment.xp = (enrollment.xp or 0) + earned_xp
        enrollment.streak = (enrollment.streak or 0) + 1
        
        # Update profile
        profile = request.user.profile
        profile.xp = (profile.xp or 0) + earned_xp
        profile.current_streak = max(profile.current_streak, enrollment.streak)
        if not UserChallengeAttempt.objects.filter(user=request.user, challenge=challenge, is_correct=True).exclude(id=attempt.id).exists():
            profile.completed_challenges += 1
        profile.save()
        
        messages.success(request, f"Correct! {feedback} +{earned_xp} XP. Streak +1.")
    else:
        enrollment.streak = 0
        messages.error(request, f"Incorrect — {feedback}")

    enrollment.progress = calculate_progress(enrollment)
    enrollment.save()

    return redirect("courses:learning_center", slug=course.slug)
