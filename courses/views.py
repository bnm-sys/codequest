from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from .models import Challenge, Course, Enrollment, UserChallengeAttempt

# Minimal bilingual support for course/module titles & descriptions
COURSE_TRANSLATIONS = {
    "linux-foundation": {
        "ne": {
            "title": "लिनक्स फाउन्डेशन",
            "description": (
                "लिनक्स प्रणाली प्रशासनमा बलियो आधार बनाउनुहोस्। "
                "फाइलसिस्टम नेभिगेट गर्नुहोस्, प्रोसेसहरू व्यवस्थापन गर्नुहोस्, "
                "अनुमतिहरू कन्फिगर गर्नुहोस्, र शेल स्क्रिप्टिङबाट स्वचालन गर्नुहोस्।"
            ),
        }
    },
    "practical-git": {
        "ne": {
            "title": "प्र्याक्टिकल गिट",
            "description": (
                "गिटसँग संस्करण नियन्त्रणमा महारत हासिल गर्नुहोस्। "
                "ब्रान्चिङ, मर्जिङ, रिबेसिङ, र सहयोगी वर्कफ्लोहरू "
                "व्यावहारिक चुनौतीहरू मार्फत सिक्नुहोस्।"
            ),
        }
    },
}

MODULE_TRANSLATIONS = {
    "linux-foundation": {
        1: {
            "title": "नेभिगेसन र फाइल व्यवस्थापन",
            "content": "लिनक्स फाइलसिस्टम संरचना र अत्यावश्यक नेभिगेसन कमाण्डहरूमा महारत हासिल गर्नुहोस्।",
        },
        2: {
            "title": "अनुमति र स्वामित्व",
            "content": "फाइल अनुमतिहरू, स्वामित्व, र सुरक्षा आधारभूत कुराहरू बुझ्नुहोस्।",
        },
        3: {
            "title": "प्रोसेस व्यवस्थापन",
            "content": "सिस्टम प्रोसेसहरू प्रभावकारी रूपमा निगरानी र नियन्त्रण गर्न सिक्नुहोस्।",
        },
    },
    "practical-git": {
        1: {
            "title": "गिट आधारभूत",
            "content": "इनिशियलाइज, स्टेज, र कमिटजस्ता आधारभूत गिट कमाण्डहरू सिक्नुहोस्।",
        },
        2: {
            "title": "ब्रान्चिङ र मर्जिङ",
            "content": "ब्रान्चिङ रणनीतिहरू र मर्जिङ प्रविधिहरूमा अभ्यास गर्नुहोस्।",
        },
        3: {
            "title": "रिमोट रेपोजिटरी",
            "content": "पुस, पुल, फेचमार्फत सहयोगी वर्कफ्लोमा महारत हासिल गर्नुहोस्।",
        },
    },
}


def _localize_course(course, lang_code):
    """Override course title/description for the requested language if available."""
    if not lang_code or not lang_code.startswith("ne"):
        return course
    trans = COURSE_TRANSLATIONS.get(course.slug, {}).get("ne")
    if trans:
        course.title = trans.get("title", course.title)
        course.description = trans.get("description", course.description)
    return course


def _localize_modules(course, modules, lang_code):
    """Override module title/content for the requested language if available."""
    if not lang_code or not lang_code.startswith("ne"):
        return modules
    per_course = MODULE_TRANSLATIONS.get(course.slug, {})
    for m in modules:
        mt = per_course.get(getattr(m, "order", None), {})
        m.title = mt.get("title", m.title)
        m.content = mt.get("content", m.content)
    return modules


def home(request):
    """Homepage listing active courses. Not authenticated by default."""
    courses = (
        Course.objects.filter(is_active=True)
        .filter(
            Q(title__icontains="practical git") | Q(title__icontains="linux foundation")
        )
        .order_by("title")
    )
    lang = getattr(request, "LANGUAGE_CODE", None)
    courses = [_localize_course(course, lang) for course in courses]
    active_enrollment = None
    if request.user.is_authenticated:
        active_enrollment = (
            Enrollment.objects.filter(user=request.user)
            .select_related("course")
            .first()
        )
    return render(
        request,
        "home.html",
        {"courses": courses, "active_enrollment": active_enrollment},
    )


def course_detail(request, slug):
    """Show course details and modules; provide enroll button if not enrolled."""
    course = get_object_or_404(Course, slug=slug)
    modules = list(course.modules.all().order_by("order"))
    lang = getattr(request, "LANGUAGE_CODE", None)
    _localize_course(course, lang)
    _localize_modules(course, modules, lang)
    user_enrollment = None
    if request.user.is_authenticated:
        user_enrollment = Enrollment.objects.filter(
            user=request.user, course=course
        ).first()

    return render(
        request,
        "courses/course_detail.html",
        {
            "course": course,
            "modules": modules,
            "enrollment": user_enrollment,
        },
    )


@login_required
def enroll_in_course(request, slug):
    """Create or get enrollment and redirect to dashboard."""
    course = get_object_or_404(Course, slug=slug)
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user, course=course
    )
    if created:
        messages.success(request, _("Enrolled in %(course)s.") % {"course": course.title})
    else:
        messages.info(
            request, _("You are already enrolled in %(course)s.") % {"course": course.title}
        )
    return redirect("courses:dashboard")


@login_required
def dashboard(request):
    """User-facing dashboard with enrollments, xp, streaks, and leaderboard snippets."""
    # Optimized: select_related to avoid N+1
    enrollments = Enrollment.objects.filter(user=request.user).select_related("course")
    lang = getattr(request, "LANGUAGE_CODE", None)
    for e in enrollments:
        _localize_course(e.course, lang)

    # REMOVED: Dynamic calculate_progress loop. Rely on stored 'progress' field for read efficiency.

    # simple leaderboard example for each course (top 5)
    course_ids = [e.course_id for e in enrollments]
    leaderboards = {}
    if course_ids:
        for cid in course_ids:
            top = Enrollment.objects.filter(course_id=cid).order_by("-xp")[:5]
            leaderboards[cid] = top

    return render(
        request,
        "courses/dashboard.html",
        {
            "enrollments": enrollments,
            "leaderboards": leaderboards,
        },
    )


def calculate_progress(enrollment):
    """Calculate percent of modules fully solved."""
    # Optimized: prefetch challenges to avoid N+1
    modules = enrollment.course.modules.prefetch_related("challenges")
    total = modules.count()
    if total == 0:
        return 0
    completed = 0

    # Get all solved challenge IDs for this user and course in one query
    solved_challenge_ids = set(
        UserChallengeAttempt.objects.filter(
            user=enrollment.user,
            challenge__module__course=enrollment.course,
            is_correct=True,
        ).values_list("challenge_id", flat=True)
    )

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
    modules = list(course.modules.prefetch_related("challenges").order_by("order"))
    lang = getattr(request, "LANGUAGE_CODE", None)
    _localize_course(course, lang)
    _localize_modules(course, modules, lang)

    if not modules:
        messages.warning(request, _("This course has no modules yet."))
        return redirect("courses:dashboard")

    # Optimized: Fetch all solved challenges for this course once
    solved_challenge_ids = set(
        UserChallengeAttempt.objects.filter(
            user=request.user, challenge__module__course=course, is_correct=True
        ).values_list("challenge_id", flat=True)
    )

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
        messages.success(request, _("You have completed the course!"))
        return redirect("courses:dashboard")

    return render(
        request,
        "courses/learning_center.html",
        {
            "course": course,
            "active_module": active_module,
            "challenge": next_challenge,
            "enrollment": enrollment,
        },
    )


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

    is_correct = user_answer == challenge.expected_output.strip()

    prev_attempts = UserChallengeAttempt.objects.filter(
        user=request.user, challenge=challenge
    ).count()
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
        messages.success(
            request,
            _("Correct — +%(xp)s XP. Streak +1.") % {"xp": earned_xp},
        )
    else:
        enrollment.streak = 0
        messages.error(request, _("Incorrect — try again!"))

    enrollment.progress = calculate_progress(enrollment)
    enrollment.save()

    return redirect("courses:learning_center", slug=course.slug)
