# list_users.py

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_management.settings')
django.setup()

from users.models import User

# Fetch and print all users
users = User.objects.all()
for user in users:
    print(f"Username: {user.username}, First Name: {user.first_name}, Last Name: {user.last_name}, Email: {user.email}, Role: {user.role}, Joined: {user.date_joined}")
