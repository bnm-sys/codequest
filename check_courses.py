#!/usr/bin/env python
"""
Quick script to check courses in the database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'codequest.settings')
django.setup()

from courses.models import Course, Module

print("=" * 60)
print("COURSE DIAGNOSTICS")
print("=" * 60)

courses = Course.objects.all()
print(f"\nTotal courses in database: {courses.count()}")

active_courses = Course.objects.filter(is_active=True)
print(f"Active courses: {active_courses.count()}")

print("\nCourse Details:")
print("-" * 60)
for course in courses:
    print(f"\n✓ {course.title}")
    print(f"  - Slug: {course.slug}")
    print(f"  - Is Active: {course.is_active}")
    print(f"  - Description: {course.description[:50]}..." if len(course.description) > 50 else f"  - Description: {course.description}")
    print(f"  - Modules: {course.modules.count()}")
    print(f"  - Total Enrolled: {course.total_enrolled}")
    
    # Show modules
    modules = course.modules.all()
    if modules.exists():
        for module in modules:
            print(f"    → {module.title} ({module.challenges.count()} challenges)")

print("\n" + "=" * 60)
print("If you see courses above but not on the homepage:")
print("  1. Restart Django server: python manage.py runserver")
print("  2. Hard refresh browser: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)")
print("  3. Clear browser cache")
print("=" * 60)

