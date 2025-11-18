#!/usr/bin/env python
"""
Management script to create sample courses, modules, and challenges
Run with: python create_sample_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'codequest.settings')
django.setup()

from courses.models import Course, Module, Challenge
from accounts.models import CustomUser
from gamification.models import Achievement

def create_sample_data():
    print("Creating sample data...")
    
    # Create sample course: Linux Basics
    linux_course, created = Course.objects.get_or_create(
        slug='linux-basics',
        defaults={
            'title': 'Linux Basics',
            'description': 'Learn the fundamentals of Linux command line and system administration.',
            'is_active': True
        }
    )
    print(f"✓ Created course: {linux_course.title}")
    
    # Create Module 1: File System Navigation
    module1, created = Module.objects.get_or_create(
        course=linux_course,
        order=1,
        defaults={
            'title': 'File System Navigation',
            'content': 'Learn to navigate the Linux file system using basic commands like ls, cd, pwd.',
            'points': 100,
            'skill_tags': {
                'ls': 1.0,
                'cd': 1.0,
                'pwd': 0.8
            }
        }
    )
    print(f"✓ Created module: {module1.title}")
    
    # Challenge 1: List directory contents
    Challenge.objects.get_or_create(
        module=module1,
        defaults={
            'title': 'List Directory Contents',
            'prompt': 'Use the ls command to list all files in the current directory, including hidden files.',
            'expected_output': '.bashrc .profile file1.txt file2.txt',
            'difficulty': 'easy'
        }
    )
    print("  ✓ Created challenge: List Directory Contents")
    
    # Challenge 2: Navigate to home directory
    Challenge.objects.get_or_create(
        module=module1,
        defaults={
            'title': 'Navigate to Home',
            'prompt': 'Change directory to your home directory using the cd command.',
            'expected_output': '/home/user',
            'difficulty': 'easy'
        }
    )
    print("  ✓ Created challenge: Navigate to Home")
    
    # Create Module 2: Git Basics
    module2, created = Module.objects.get_or_create(
        course=linux_course,
        order=2,
        defaults={
            'title': 'Git Basics',
            'content': 'Learn to use Git for version control with commands like git clone, git add, git commit.',
            'points': 150,
            'skill_tags': {
                'git-clone': 1.0,
                'git-add': 1.0,
                'git-commit': 1.0
            }
        }
    )
    print(f"✓ Created module: {module2.title}")
    
    # Challenge 3: Clone a repository
    Challenge.objects.get_or_create(
        module=module2,
        defaults={
            'title': 'Clone Repository',
            'prompt': 'Clone the repository at https://github.com/user/repo.git using git clone.',
            'expected_output': 'Cloning into \'repo\'...',
            'difficulty': 'medium'
        }
    )
    print("  ✓ Created challenge: Clone Repository")
    
    # Create Git Course
    git_course, created = Course.objects.get_or_create(
        slug='git-fundamentals',
        defaults={
            'title': 'Git Fundamentals',
            'description': 'Master Git version control system from basics to advanced workflows.',
            'is_active': True
        }
    )
    print(f"✓ Created course: {git_course.title}")
    
    # Create Module for Git Course
    git_module1, created = Module.objects.get_or_create(
        course=git_course,
        order=1,
        defaults={
            'title': 'Git Setup and Configuration',
            'content': 'Learn to set up Git and configure your user information.',
            'points': 80,
            'skill_tags': {
                'git-config': 1.0,
                'git-init': 0.9
            }
        }
    )
    print(f"✓ Created module: {git_module1.title}")
    
    Challenge.objects.get_or_create(
        module=git_module1,
        defaults={
            'title': 'Configure Git User',
            'prompt': 'Set your Git username to "John Doe" using git config.',
            'expected_output': '',
            'difficulty': 'easy'
        }
    )
    print("  ✓ Created challenge: Configure Git User")
    
    # Create sample achievements
    Achievement.objects.get_or_create(
        name='First Steps',
        defaults={
            'description': 'Complete your first challenge',
            'xp_reward': 50,
            'icon': '🎯'
        }
    )
    print("✓ Created achievement: First Steps")
    
    Achievement.objects.get_or_create(
        name='Linux Explorer',
        defaults={
            'description': 'Complete the Linux Basics course',
            'xp_reward': 500,
            'icon': '🐧',
            'skill_tag': 'ls'
        }
    )
    print("✓ Created achievement: Linux Explorer")
    
    print("\n✓ Sample data created successfully!")
    print(f"\nCourses: {Course.objects.count()}")
    print(f"Modules: {Module.objects.count()}")
    print(f"Challenges: {Challenge.objects.count()}")
    print(f"Achievements: {Achievement.objects.count()}")

if __name__ == '__main__':
    create_sample_data()

