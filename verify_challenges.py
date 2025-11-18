#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'codequest.settings')
django.setup()

from courses.models import Challenge, Module

m = Module.objects.get(course__slug='linux-basics', order=1)
print(f'Module: {m.title}')
print('=' * 60)
for c in m.challenges.all().order_by('order'):
    print(f'\n{c.order}. {c.title}')
    print(f'   Theory: {"✓" if c.theory_content else "✗"}')
    print(f'   Visualization: {"✓" if c.visualization_script else "✗"}')
    print(f'   Setup: {"✓" if c.setup_commands else "✗"}')
    print(f'   Command: {c.command_to_practice or "N/A"}')
    if c.order == 1:
        print(f'   Expected: {c.expected_output[:50]}...')

