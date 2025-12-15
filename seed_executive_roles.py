#!/usr/bin/env python3
"""
Seed script to create test users for new executive roles.
Run this script to add test accounts for testing role-based access.
"""

import sys
import os

# Add the parent directory to the path so we can import sigma_finance
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sigma_finance.app import create_app
from sigma_finance.models import db, User

def seed_executive_users():
    """Create test users for each executive role"""

    app = create_app()

    with app.app_context():
        # Define test users
        test_users = [
            {
                'name': 'Test President',
                'email': 'president@test.com',
                'role': 'president',
                'password': 'TestPass123!',  # Updated to meet new security requirements
            },
            {
                'name': 'Test First Vice',
                'email': 'vice1@test.com',
                'role': 'vice_1',
                'password': 'TestPass123!',  # Updated to meet new security requirements
            },
            {
                'name': 'Test Second Vice',
                'email': 'vice2@test.com',
                'role': 'vice_2',
                'password': 'TestPass123!',  # Updated to meet new security requirements
            },
            {
                'name': 'Test Secretary',
                'email': 'secretary@test.com',
                'role': 'secretary',
                'password': 'TestPass123!',  # Updated to meet new security requirements
            },
        ]

        print("Seeding executive role test users...\n")

        for user_data in test_users:
            # Check if user already exists
            existing_user = User.query.filter_by(email=user_data['email']).first()

            if existing_user:
                print(f"[UPDATE] User {user_data['email']} already exists. Updating role to {user_data['role']}...")
                existing_user.role = user_data['role']
                existing_user.name = user_data['name']
                existing_user.active = True
                existing_user.set_password(user_data['password'])
            else:
                print(f"[CREATE] Creating user: {user_data['name']} ({user_data['email']}) - Role: {user_data['role']}")
                new_user = User(
                    name=user_data['name'],
                    email=user_data['email'],
                    role=user_data['role'],
                    active=True
                )
                new_user.set_password(user_data['password'])
                db.session.add(new_user)

        try:
            db.session.commit()
            print("\n[SUCCESS] Executive role test users seeded!\n")
            print("=" * 60)
            print("TEST CREDENTIALS")
            print("=" * 60)
            print("\n[FULL ACCESS] (can access all treasurer features):")
            print("   President:       president@test.com / TestPass123!")
            print("   1st Vice:        vice1@test.com / TestPass123!")
            print("\n[REPORT ACCESS] (can view reports and create invites):")
            print("   2nd Vice:        vice2@test.com / TestPass123!")
            print("   Secretary:       secretary@test.com / TestPass123!")
            print("\n" + "=" * 60)
            print("\nLogin at: http://localhost:5173/login")
            print("\nNOTE: Password meets security requirements:")
            print("  - 12+ characters, uppercase, lowercase, digit, special char")

        except Exception as e:
            db.session.rollback()
            print(f"\n[ERROR] Failed to seed users: {e}")
            sys.exit(1)

if __name__ == '__main__':
    seed_executive_users()
