# courses/admin.py
from django.contrib import admin

from .models import Challenge, Course, Enrollment, Module, UserChallengeAttempt


class ChallengeInline(admin.TabularInline):
    model = Challenge
    extra = 0
    fields = ("title", "difficulty")


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 0
    show_change_link = True


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_active", "total_enrolled", "created_at")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ModuleInline]
    readonly_fields = ("created_at",)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order", "points", "created_at")
    list_filter = ("course",)
    inlines = [ChallengeInline]
    readonly_fields = ("created_at",)


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "difficulty", "created_at")
    list_filter = ("difficulty", "module")
    search_fields = ("prompt",)
    readonly_fields = ("created_at",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "xp", "streak", "progress", "enrolled_at")
    list_filter = ("course",)
    readonly_fields = ("enrolled_at",)


@admin.register(UserChallengeAttempt)
class UserChallengeAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "challenge",
        "is_correct",
        "attempt_no",
        "time_seconds",
        "submitted_at",
    )
    list_filter = ("is_correct", "challenge__module")
    search_fields = ("user__email",)
    readonly_fields = ("submitted_at",)
