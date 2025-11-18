#!/usr/bin/env python
"""
Create a test user for testing the application
Run with: python create_test_user.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'codequest.settings')
django.setup()

from accounts.models import CustomUser

def create_test_user():
    print("Creating test user...")
    
    # Create test student user
    test_user, created = CustomUser.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'testuser@example.com',
            'role': 'student',
            'phone_number': '+9771234567890'
        }
    )
    
    if created:
        test_user.set_password('testpass123')
        test_user.save()
        print(f"✓ Created test user: {test_user.username}")
        print(f"  Email: {test_user.email}")
        print(f"  Password: testpass123")
        print(f"  Role: {test_user.role}")
    else:
        print(f"✓ Test user already exists: {test_user.username}")
        print("  Password: testpass123 (reset if needed)")
    
    print("\n" + "="*50)
    print("TEST CREDENTIALS")
    print("="*50)
    print("Admin:")
    print("  Username: admin")
    print("  Password: (set during superuser creation)")
    print("\nTest User:")
    print(f"  Username: {test_user.username}")
    print("  Password: testpass123")
    print("="*50)

if __name__ == '__main__':
    create_test_user()

