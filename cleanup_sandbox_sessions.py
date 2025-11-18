#!/usr/bin/env python
"""
Clean up sandbox sessions - mark inactive sessions as inactive
Run this after stopping Docker containers manually
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'codequest.settings')
django.setup()

from sandbox.models import SandboxSession
from django.utils import timezone

def cleanup_sessions():
    """Mark all active sandbox sessions as inactive"""
    active_sessions = SandboxSession.objects.filter(is_active=True)
    count = active_sessions.count()
    
    active_sessions.update(is_active=False)
    
    print(f"✓ Marked {count} sandbox sessions as inactive")
    print(f"✓ All sessions cleaned up. New containers will be created automatically when users start new sessions.")

if __name__ == '__main__':
    cleanup_sessions()

