#!/usr/bin/env python
"""
Setup script to initialize Django admin user
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hiremind_admin.settings')
django.setup()

from django.contrib.auth.models import User

# Create superuser if it doesn't exist
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@hiremind.local', 'admin123')
    print("✓ Superuser 'admin' created with password 'admin123'")
else:
    print("✓ Superuser already exists")

print("\nDjango Admin is ready!")
print("Access the admin panel at: http://localhost:8001/admin/")
print("Username: admin")
print("Password: admin123")
