#!/usr/bin/env python
"""
Update all existing challenges with proper pedagogical structure
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'codequest.settings')
django.setup()

from courses.models import Course, Module, Challenge

def update_all_challenges():
    print("Updating all challenges with pedagogical content...")
    
    # Get Linux Basics course
    linux_course = Course.objects.get(slug='linux-basics')
    
    # Update Module 1: Understanding the Linux Filesystem Root
    module1, _ = Module.objects.get_or_create(
        course=linux_course,
        order=1,
        defaults={
            'title': 'Understanding the Linux Filesystem Root',
            'content': 'Learn the fundamental structure of the Linux filesystem, starting from the root directory (/) and understanding how directories are organized.',
            'points': 100,
            'skill_tags': {
                'linux_filesystem': 1.0,
                'directory_structure': 1.0,
                'ls': 0.9,
                'pwd': 0.8
            }
        }
    )
    # Update module if it exists
    if not module1.title.startswith('Understanding'):
        module1.title = 'Understanding the Linux Filesystem Root'
        module1.content = 'Learn the fundamental structure of the Linux filesystem, starting from the root directory (/) and understanding how directories are organized.'
        module1.save()
    
    # Challenge 1: Understanding Root Directory Structure (START FROM /)
    challenge1, created = Challenge.objects.update_or_create(
        module=module1,
        order=1,
        defaults={
            'title': 'Understanding Root Directory Structure',
            'theory_content': '''The Linux filesystem is organized in a hierarchical tree structure, starting from the root directory (/).

Think of the root directory (/) as the foundation of a building. Everything in Linux is organized under this single root:

• /bin - Essential system binaries (commands like ls, cp, mv)
• /boot - Boot loader files
• /dev - Device files (representing hardware)
• /etc - System configuration files
• /home - User home directories
• /lib - Shared libraries
• /root - Root user's home directory
• /usr - User programs and data
• /var - Variable data (logs, cache)

The root directory is the starting point for all paths in Linux. When you see a path starting with "/", it's an absolute path from the root.

This is where your Linux journey begins - understanding the foundation of the entire system.''',
            'visualization_script': 'ls -la /',
            'setup_commands': '''cd /
mkdir -p /home/testuser
cd /home/testuser
touch .bashrc .profile file1.txt file2.txt''',
            'prompt': 'Navigate to the root directory (/) and list all files and directories using `ls -la /`. Observe the standard Linux directory structure.',
            'command_to_practice': 'ls -la /',
            'expected_output': 'bin boot dev etc home lib',
            'evaluation_type': 'contains',
            'difficulty': 'easy'
        }
    )
    print(f"✓ Challenge 1: {challenge1.title}")
    
    # Challenge 2: Exploring Your Current Location
    challenge2, created = Challenge.objects.update_or_create(
        module=module1,
        order=2,
        defaults={
            'title': 'Exploring Your Current Location',
            'theory_content': '''The `pwd` command stands for "Print Working Directory". It shows you exactly where you are in the filesystem.

When you first log into a Linux system, you typically start in your home directory (/home/username). But you can navigate anywhere.

Understanding your current location is crucial because:
• Relative paths depend on where you are
• Commands often operate on files in your current directory
• You need to know your location to navigate effectively

Think of `pwd` as your GPS coordinates in the filesystem. It always tells you your exact position in the directory tree.''',
            'visualization_script': 'pwd',
            'setup_commands': '''cd /home/testuser
pwd''',
            'prompt': 'Use the `pwd` command to display your current directory path. This shows you exactly where you are in the filesystem.',
            'command_to_practice': 'pwd',
            'expected_output': '/home/testuser',
            'evaluation_type': 'contains',
            'difficulty': 'easy'
        }
    )
    print(f"✓ Challenge 2: {challenge2.title}")
    
    # Challenge 3: Listing Files in Your Home Directory
    challenge3, created = Challenge.objects.update_or_create(
        module=module1,
        order=3,
        defaults={
            'title': 'Listing Files in Your Home Directory',
            'theory_content': '''The `ls` command lists files and directories. It's one of the most fundamental commands in Linux.

Key variations:
• `ls` - Lists visible files and directories
• `ls -a` - Lists ALL files, including hidden ones (files starting with ".")
• `ls -l` - Long format with details (permissions, size, date)
• `ls -la` - Combines both: all files in long format

Hidden files in Linux start with a dot (.). They're often configuration files like .bashrc, .profile, etc. The `-a` flag reveals these hidden files.

In your home directory, you'll typically see:
• Hidden config files (.bashrc, .profile)
• Your personal files and folders
• System-generated files

Mastering `ls` is essential - it's how you explore and understand any directory.''',
            'visualization_script': 'ls -a',
            'setup_commands': '''cd /home/testuser
ls -a''',
            'prompt': 'Use `ls -a` to list all files in your current directory, including hidden files. Look for files starting with a dot (.).',
            'command_to_practice': 'ls -a',
            'expected_output': '.bashrc .profile file1.txt file2.txt',
            'evaluation_type': 'file_exists',
            'difficulty': 'easy'
        }
    )
    print(f"✓ Challenge 3: {challenge3.title}")
    
    # Module 2: Navigation Commands
    module2, _ = Module.objects.get_or_create(
        course=linux_course,
        order=2,
        defaults={
            'title': 'Navigation Commands',
            'content': 'Master the art of moving through the Linux filesystem using cd, understanding relative vs absolute paths.',
            'points': 150,
            'skill_tags': {
                'cd': 1.0,
                'navigation': 1.0,
                'paths': 0.9
            }
        }
    )
    
    # Challenge 4: Changing Directories
    challenge4, created = Challenge.objects.update_or_create(
        module=module2,
        order=1,
        defaults={
            'title': 'Changing Directories with cd',
            'theory_content': '''The `cd` command changes your current directory. It's how you navigate through the filesystem.

Key concepts:
• `cd /path/to/dir` - Absolute path (starts from root /)
• `cd relative/path` - Relative path (from current location)
• `cd ~` or `cd` - Go to home directory
• `cd ..` - Go up one directory (parent)
• `cd -` - Go to previous directory

Absolute paths always start with "/" and give the full path from root.
Relative paths don't start with "/" and are relative to where you are now.

Navigation is the key to efficiency in Linux. Once you master `cd`, you can move anywhere instantly.''',
            'visualization_script': 'cd /home/testuser && pwd',
            'setup_commands': '''cd /home/testuser
mkdir -p /home/testuser/documents
cd /home/testuser/documents
touch doc1.txt doc2.txt''',
            'prompt': 'Use `cd ~` to navigate to your home directory, then use `pwd` to confirm your location.',
            'command_to_practice': 'cd ~',
            'expected_output': '/home/testuser',
            'evaluation_type': 'command',
            'difficulty': 'easy'
        }
    )
    print(f"✓ Challenge 4: {challenge4.title}")
    
    # Git Fundamentals course
    git_course = Course.objects.get(slug='git-fundamentals')
    
    # Git Module 1: Git Setup and Configuration
    git_module1, _ = Module.objects.get_or_create(
        course=git_course,
        order=1,
        defaults={
            'title': 'Git Setup and Configuration',
            'content': 'Learn to configure Git and understand the basics of version control.',
            'points': 80,
            'skill_tags': {
                'git-config': 1.0,
                'git-init': 0.9
            }
        }
    )
    
    # Git Challenge 1: Configure Git User
    git_challenge1, created = Challenge.objects.update_or_create(
        module=git_module1,
        order=1,
        defaults={
            'title': 'Configure Git User',
            'theory_content': '''Git needs to know who you are before you can make commits. This information is stored in Git's configuration.

The `git config` command sets configuration values:
• `git config --global user.name "Your Name"` - Sets your name
• `git config --global user.email "your@email.com"` - Sets your email

The `--global` flag means this applies to all Git repositories on your system. Without it, the setting only applies to the current repository.

This identity is attached to every commit you make, so others can see who made changes. It's like signing your work in the version control system.

Think of it as introducing yourself to Git - "Hi, I'm [Your Name], and this is my email."''',
            'visualization_script': 'git config --global --list | grep user',
            'setup_commands': '''cd /home/testuser
git config --global user.name "CodeQuest User"
git config --global user.email "user@codequest.com"''',
            'prompt': 'Configure Git with your name using: `git config --global user.name "Your Name"`',
            'command_to_practice': 'git config --global user.name',
            'expected_output': '',
            'evaluation_type': 'command',
            'difficulty': 'easy'
        }
    )
    print(f"✓ Git Challenge 1: {git_challenge1.title}")
    
    print("\n✓ All challenges updated with pedagogical content!")
    print(f"\nTotal challenges updated: {Challenge.objects.count()}")

if __name__ == '__main__':
    update_all_challenges()

