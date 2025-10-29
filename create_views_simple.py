#!/usr/bin/env python3
"""
Simple script to create database views
Run from project root: python create_views_simple.py
"""

from sigma_finance.app import create_app
from sigma_finance.extensions import db
import os

app = create_app()

with app.app_context():
    db_url = app.config['SQLALCHEMY_DATABASE_URI']

    print(f"Database: {db_url}")

    # Check if SQLite or PostgreSQL
    if 'sqlite' in db_url:
        sql_file = 'database/create_views_sqlite.sql'
        print("\n📁 Using SQLite views...")
    else:
        sql_file = 'database/create_views.sql'
        print("\n📁 Using PostgreSQL views...")

    # Read SQL file
    if not os.path.exists(sql_file):
        print(f"❌ File not found: {sql_file}")
        exit(1)

    with open(sql_file, 'r') as f:
        sql_content = f.read()

    # Split by semicolons and execute each statement
    statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]

    print(f"\n🔨 Executing {len(statements)} SQL statements...\n")

    for i, statement in enumerate(statements, 1):
        # Skip comments and empty statements
        if statement.startswith('--') or not statement.strip():
            continue

        # Only execute CREATE VIEW statements
        if 'CREATE VIEW' in statement.upper() or 'CREATE OR REPLACE VIEW' in statement.upper():
            try:
                db.session.execute(db.text(statement))
                db.session.commit()

                # Extract view name
                view_name = 'unknown'
                if 'dues_paid_view' in statement:
                    view_name = 'dues_paid_view'
                elif 'payment_plan_stats_view' in statement:
                    view_name = 'payment_plan_stats_view'

                print(f"✅ Created: {view_name}")
            except Exception as e:
                print(f"❌ Error: {e}")
                db.session.rollback()

    # Test the views
    print("\n🧪 Testing views...\n")

    try:
        result = db.session.execute(db.text("SELECT COUNT(*) FROM dues_paid_view"))
        count = result.scalar()
        print(f"✓ dues_paid_view: {count} rows")
    except Exception as e:
        print(f"❌ dues_paid_view error: {e}")

    try:
        result = db.session.execute(db.text("SELECT COUNT(*) FROM payment_plan_stats_view"))
        count = result.scalar()
        print(f"✓ payment_plan_stats_view: {count} rows")
    except Exception as e:
        print(f"❌ payment_plan_stats_view error: {e}")

    print("\n✨ Done!")
