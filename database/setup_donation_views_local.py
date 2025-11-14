#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup donation views in local SQLite database

This script creates the donation reporting views in your local SQLite database.
Run this after deploying the donation table migration.

Usage:
    python database/setup_donation_views_local.py
"""

import sqlite3
import os
import sys

# Fix Windows console encoding issues
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_donation_views():
    """Create donation views in SQLite database"""

    # Path to SQLite database
    db_path = os.path.join('instance', 'sigma.db')

    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        print("   Make sure you're running this from the project root directory")
        return False

    # Path to SQL file
    sql_file = os.path.join('database', 'create_donation_view_sqlite.sql')

    if not os.path.exists(sql_file):
        print(f"❌ SQL file not found at {sql_file}")
        return False

    try:
        # Read SQL file
        with open(sql_file, 'r') as f:
            sql_script = f.read()

        # Connect to database
        print(f"📂 Connecting to database: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute SQL script
        print("⚙️  Creating donation views...")
        cursor.executescript(sql_script)

        # Commit changes
        conn.commit()

        # Verify views were created
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='view' AND name LIKE '%donation%'
            ORDER BY name
        """)

        views = cursor.fetchall()

        if views:
            print("\n✅ Successfully created donation views:")
            for view in views:
                print(f"   • {view[0]}")

            # Test each view
            print("\n🧪 Testing views...")

            test_queries = [
                ("donation_stats_view", "SELECT COUNT(*) FROM donation_stats_view"),
                ("donation_monthly_summary", "SELECT COUNT(*) FROM donation_monthly_summary"),
                ("top_donors_view", "SELECT COUNT(*) FROM top_donors_view")
            ]

            all_passed = True
            for view_name, query in test_queries:
                try:
                    cursor.execute(query)
                    count = cursor.fetchone()[0]
                    print(f"   ✓ {view_name}: {count} rows")
                except Exception as e:
                    print(f"   ✗ {view_name}: ERROR - {str(e)}")
                    all_passed = False

            if all_passed:
                print("\n🎉 All views created successfully!")
            else:
                print("\n⚠️  Some views may have errors. Check the output above.")
        else:
            print("⚠️  No donation views found after creation")
            return False

        # Close connection
        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("Sigma Finance - Setup Donation Views (SQLite)")
    print("=" * 60)
    print()

    success = create_donation_views()

    print()
    print("=" * 60)

    if success:
        print("✅ Setup complete! You can now use the donation reports.")
        print()
        print("Next steps:")
        print("  1. Start your Flask app: flask run")
        print("  2. Navigate to: http://localhost:5000/reports/donations")
        print("  3. Test the HTMX filtering functionality")
        sys.exit(0)
    else:
        print("❌ Setup failed. Please check the errors above.")
        sys.exit(1)
