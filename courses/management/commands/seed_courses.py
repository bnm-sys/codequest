"""
Management command to seed demo courses: Practical Git and Linux Foundation.
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from courses.models import Challenge, Course, Module


class Command(BaseCommand):
    help = "Seed Practical Git and Linux Foundation courses with modules and challenges"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding courses...")

        # Create Practical Git course
        git_course, created = Course.objects.get_or_create(
            slug="practical-git",
            defaults={
                "title": "Practical Git",
                "description": "Master version control with Git. Learn branching, merging, rebasing, and collaborative workflows through hands-on terminal challenges.",
                "is_active": True,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"✓ Created course: {git_course.title}"))
        else:
            self.stdout.write(f"- Course already exists: {git_course.title}")

        # Create Linux Foundation course
        linux_course, created = Course.objects.get_or_create(
            slug="linux-foundation",
            defaults={
                "title": "Linux Foundation",
                "description": "Build a rock-solid foundation in Linux system administration. Navigate filesystems, manage processes, configure permissions, and automate tasks with shell scripting.",
                "is_active": True,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"✓ Created course: {linux_course.title}"))
        else:
            self.stdout.write(f"- Course already exists: {linux_course.title}")

        # Seed Git modules and challenges
        self._seed_git_modules(git_course)

        # Seed Linux modules and challenges
        self._seed_linux_modules(linux_course)

        self.stdout.write(self.style.SUCCESS("\n✓ Course seeding complete!"))

    def _seed_git_modules(self, course):
        """Create modules and challenges for Practical Git course."""
        self.stdout.write(f"\nSeeding modules for {course.title}...")

        # Module 1: Git Basics
        module1, created = Module.objects.get_or_create(
            course=course,
            order=1,
            defaults={
                "title": "Git Basics",
                "content": "Learn fundamental Git commands and concepts including initialization, staging, and committing changes.",
                "points": 50,
                "skill_tags": {"topics": ["init", "add", "commit", "status", "log"]},
            },
        )
        if created:
            self.stdout.write(f"  ✓ Created module: {module1.title}")
            
            # Challenges for Module 1
            Challenge.objects.create(
                module=module1,
                title="Initialize a Git Repository",
                prompt="Initialize a new Git repository in the current directory.",
                expected_output="Initialized empty Git repository",
                difficulty="easy",
            )
            Challenge.objects.create(
                module=module1,
                title="Stage and Commit Changes",
                prompt="Create a file named 'hello.txt' with the content 'Hello Git', stage it, and commit with message 'Initial commit'.",
                expected_output="1 file changed, 1 insertion(+)",
                difficulty="easy",
            )
            Challenge.objects.create(
                module=module1,
                title="Check Repository Status",
                prompt="Check the current status of your Git repository.",
                expected_output="nothing to commit, working tree clean",
                difficulty="easy",
            )

        # Module 2: Branching and Merging
        module2, created = Module.objects.get_or_create(
            course=course,
            order=2,
            defaults={
                "title": "Branching and Merging",
                "content": "Master Git branching strategies and learn to merge branches effectively.",
                "points": 75,
                "skill_tags": {"topics": ["branch", "checkout", "merge", "rebase"]},
            },
        )
        if created:
            self.stdout.write(f"  ✓ Created module: {module2.title}")
            
            # Challenges for Module 2
            Challenge.objects.create(
                module=module2,
                title="Create a New Branch",
                prompt="Create a new branch named 'feature' and switch to it.",
                expected_output="Switched to a new branch 'feature'",
                difficulty="medium",
            )
            Challenge.objects.create(
                module=module2,
                title="Merge Branches",
                prompt="Merge the 'feature' branch into 'main' branch.",
                expected_output="Fast-forward",
                difficulty="medium",
            )

        # Module 3: Remote Repositories
        module3, created = Module.objects.get_or_create(
            course=course,
            order=3,
            defaults={
                "title": "Remote Repositories",
                "content": "Learn to collaborate using remote repositories with push, pull, and fetch operations.",
                "points": 100,
                "skill_tags": {"topics": ["remote", "push", "pull", "fetch", "clone"]},
            },
        )
        if created:
            self.stdout.write(f"  ✓ Created module: {module3.title}")
            
            # Challenges for Module 3
            Challenge.objects.create(
                module=module3,
                title="Add Remote Repository",
                prompt="Add a remote repository named 'origin' with URL 'https://github.com/user/repo.git'.",
                expected_output="remote origin added",
                difficulty="medium",
            )
            Challenge.objects.create(
                module=module3,
                title="Push to Remote",
                prompt="Push your local 'main' branch to the remote 'origin'.",
                expected_output="Branch 'main' set up to track remote branch",
                difficulty="hard",
            )

    def _seed_linux_modules(self, course):
        """Create modules and challenges for Linux Foundation course."""
        self.stdout.write(f"\nSeeding modules for {course.title}...")

        # Module 1: Navigation and File Management
        module1, created = Module.objects.get_or_create(
            course=course,
            order=1,
            defaults={
                "title": "Navigation and File Management",
                "content": "Master the Linux filesystem hierarchy and essential navigation commands.",
                "points": 50,
                "skill_tags": {"topics": ["cd", "ls", "pwd", "mkdir", "rm", "cp", "mv"]},
            },
        )
        if created:
            self.stdout.write(f"  ✓ Created module: {module1.title}")
            
            # Challenges for Module 1
            Challenge.objects.create(
                module=module1,
                title="Navigate Directories",
                prompt="Navigate to the /tmp directory and print the current working directory.",
                expected_output="/tmp",
                difficulty="easy",
            )
            Challenge.objects.create(
                module=module1,
                title="Create Directory Structure",
                prompt="Create a directory named 'projects' with subdirectories 'web' and 'mobile'.",
                expected_output="projects/web projects/mobile",
                difficulty="easy",
            )
            Challenge.objects.create(
                module=module1,
                title="Copy and Move Files",
                prompt="Copy 'file1.txt' to 'file2.txt' and move it to the 'backup' directory.",
                expected_output="backup/file2.txt",
                difficulty="medium",
            )

        # Module 2: Permissions and Ownership
        module2, created = Module.objects.get_or_create(
            course=course,
            order=2,
            defaults={
                "title": "Permissions and Ownership",
                "content": "Understand Linux file permissions, ownership, and security fundamentals.",
                "points": 75,
                "skill_tags": {"topics": ["chmod", "chown", "chgrp", "umask"]},
            },
        )
        if created:
            self.stdout.write(f"  ✓ Created module: {module2.title}")
            
            # Challenges for Module 2
            Challenge.objects.create(
                module=module2,
                title="Change File Permissions",
                prompt="Change permissions of 'script.sh' to make it executable by the owner.",
                expected_output="-rwxr--r--",
                difficulty="medium",
            )
            Challenge.objects.create(
                module=module2,
                title="Change File Ownership",
                prompt="Change the owner of 'data.txt' to user 'admin'.",
                expected_output="admin",
                difficulty="medium",
            )

        # Module 3: Process Management
        module3, created = Module.objects.get_or_create(
            course=course,
            order=3,
            defaults={
                "title": "Process Management",
                "content": "Learn to monitor and control system processes effectively.",
                "points": 100,
                "skill_tags": {"topics": ["ps", "top", "kill", "bg", "fg", "jobs"]},
            },
        )
        if created:
            self.stdout.write(f"  ✓ Created module: {module3.title}")
            
            # Challenges for Module 3
            Challenge.objects.create(
                module=module3,
                title="List Running Processes",
                prompt="Display all running processes for the current user.",
                expected_output="PID TTY",
                difficulty="easy",
            )
            Challenge.objects.create(
                module=module3,
                title="Kill a Process",
                prompt="Terminate the process with PID 1234 using the kill command.",
                expected_output="terminated",
                difficulty="medium",
            )
            Challenge.objects.create(
                module=module3,
                title="Background Processes",
                prompt="Run a long process in the background and list all background jobs.",
                expected_output="Running",
                difficulty="hard",
            )

        # Module 4: Shell Scripting
        module4, created = Module.objects.get_or_create(
            course=course,
            order=4,
            defaults={
                "title": "Shell Scripting Basics",
                "content": "Automate tasks with bash scripting fundamentals including variables, loops, and conditionals.",
                "points": 125,
                "skill_tags": {"topics": ["bash", "variables", "loops", "conditionals", "functions"]},
            },
        )
        if created:
            self.stdout.write(f"  ✓ Created module: {module4.title}")
            
            # Challenges for Module 4
            Challenge.objects.create(
                module=module4,
                title="Create a Simple Script",
                prompt="Create a bash script that prints 'Hello, Linux!' to the console.",
                expected_output="Hello, Linux!",
                difficulty="easy",
            )
            Challenge.objects.create(
                module=module4,
                title="Use Variables and Conditionals",
                prompt="Write a script that checks if a file exists and prints a message accordingly.",
                expected_output="File exists",
                difficulty="medium",
            )
            Challenge.objects.create(
                module=module4,
                title="Loop Through Files",
                prompt="Create a script that loops through all .txt files in a directory and prints their names.",
                expected_output="file1.txt file2.txt",
                difficulty="hard",
            )
