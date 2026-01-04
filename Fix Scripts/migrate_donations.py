#!/usr/bin/env python3
"""
Script to migrate donation payments from the Payment table to the Donation table.
This is useful for cleaning up transactions that were recorded as dues but were actually donations.

Usage:
    python migrate_donations.py --dry-run  # Preview what will be migrated
    python migrate_donations.py            # Actually perform the migration
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Add the parent directory to the path so we can import sigma_finance
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sigma_finance.app import create_app
from sigma_finance.extensions import db
from sigma_finance.models import Payment, Donation, User


def find_donation_payments(start_date=None, end_date=None, min_amount=None, max_amount=None):
    """
    Find payments that look like donations based on criteria.

    Args:
        start_date: Earliest date to consider (datetime)
        end_date: Latest date to consider (datetime)
        min_amount: Minimum payment amount
        max_amount: Maximum payment amount

    Returns:
        List of Payment objects
    """
    query = Payment.query

    if start_date:
        query = query.filter(Payment.date >= start_date)
    if end_date:
        query = query.filter(Payment.date <= end_date)
    if min_amount:
        query = query.filter(Payment.amount >= min_amount)
    if max_amount:
        query = query.filter(Payment.amount <= max_amount)

    # Order by date for easier review
    query = query.order_by(Payment.date.desc())

    return query.all()


def preview_migration(payments):
    """
    Show what would be migrated without actually doing it.
    """
    if not payments:
        print("No payments found matching the criteria.")
        return

    print(f"\n{'='*80}")
    print(f"MIGRATION PREVIEW - {len(payments)} payment(s) found")
    print(f"{'='*80}\n")

    total_amount = Decimal('0.00')

    for i, payment in enumerate(payments, 1):
        user = payment.user
        total_amount += payment.amount

        print(f"{i}. Payment ID: {payment.id}")
        print(f"   User: {user.name} ({user.email})")
        print(f"   Amount: ${payment.amount}")
        print(f"   Date: {payment.date.strftime('%Y-%m-%d %I:%M %p') if payment.date else 'N/A'}")
        print(f"   Method: {payment.method or 'N/A'}")
        print(f"   Type: {payment.payment_type or 'N/A'}")
        print(f"   Notes: {payment.notes or 'N/A'}")
        print(f"   Plan ID: {payment.plan_id or 'None'}")
        print()

    print(f"{'='*80}")
    print(f"Total amount to migrate: ${total_amount}")
    print(f"{'='*80}\n")


def migrate_payment_to_donation(payment, anonymous=False, notes_prefix=None):
    """
    Convert a Payment to a Donation.

    Args:
        payment: Payment object to migrate
        anonymous: Whether the donation should be anonymous
        notes_prefix: Optional prefix to add to notes (e.g., "Migrated: ")

    Returns:
        The created Donation object
    """
    user = payment.user

    # Prepare notes
    original_notes = payment.notes or ""
    if notes_prefix:
        new_notes = f"{notes_prefix}{original_notes}" if original_notes else notes_prefix
    else:
        new_notes = f"Migrated from Payment #{payment.id}. {original_notes}".strip()

    # Create the donation
    donation = Donation(
        donor_name=user.name,
        donor_email=user.email,
        amount=payment.amount,
        date=payment.date,
        method=payment.method or "unknown",
        stripe_payment_id=None,  # Payments don't have this field
        anonymous=anonymous,
        notes=new_notes,
        user_id=user.id
    )

    return donation


def perform_migration(payments, anonymous=False, delete_payments=True, notes_prefix="Donation drive - "):
    """
    Actually perform the migration.

    Args:
        payments: List of Payment objects to migrate
        anonymous: Whether donations should be anonymous
        delete_payments: Whether to delete the original payments after migration
        notes_prefix: Prefix to add to notes

    Returns:
        Number of payments successfully migrated
    """
    if not payments:
        print("No payments to migrate.")
        return 0

    print(f"\n{'='*80}")
    print(f"STARTING MIGRATION - {len(payments)} payment(s)")
    print(f"{'='*80}\n")

    migrated_count = 0
    errors = []

    for payment in payments:
        try:
            # Create donation
            donation = migrate_payment_to_donation(payment, anonymous, notes_prefix)
            db.session.add(donation)

            # Delete original payment if requested
            if delete_payments:
                db.session.delete(payment)

            db.session.commit()

            migrated_count += 1
            print(f"✓ Migrated Payment #{payment.id} → Donation #{donation.id} (${payment.amount} from {payment.user.name})")

        except Exception as e:
            db.session.rollback()
            error_msg = f"✗ Failed to migrate Payment #{payment.id}: {str(e)}"
            print(error_msg)
            errors.append(error_msg)

    print(f"\n{'='*80}")
    print(f"MIGRATION COMPLETE")
    print(f"{'='*80}")
    print(f"Successfully migrated: {migrated_count}")
    print(f"Errors: {len(errors)}")

    if errors:
        print("\nErrors encountered:")
        for error in errors:
            print(f"  {error}")

    return migrated_count


def interactive_mode():
    """
    Interactive mode to help select which payments to migrate.
    """
    print("\n" + "="*80)
    print("DONATION MIGRATION TOOL - Interactive Mode")
    print("="*80 + "\n")

    # Get date range
    print("Step 1: Date Range")
    print("-" * 40)

    # Suggest weekend dates
    today = datetime.now()
    # Find last Saturday/Sunday
    days_since_sunday = (today.weekday() + 1) % 7
    last_sunday = today - timedelta(days=days_since_sunday)
    last_saturday = last_sunday - timedelta(days=1)

    print(f"Last weekend was: {last_saturday.strftime('%Y-%m-%d')} to {last_sunday.strftime('%Y-%m-%d')}")

    use_weekend = input("\nUse last weekend's dates? (y/n): ").lower().strip()

    if use_weekend == 'y':
        start_date = last_saturday.replace(hour=0, minute=0, second=0)
        end_date = last_sunday.replace(hour=23, minute=59, second=59)
    else:
        start_str = input("Start date (YYYY-MM-DD) or press Enter to skip: ").strip()
        end_str = input("End date (YYYY-MM-DD) or press Enter to skip: ").strip()

        start_date = datetime.strptime(start_str, '%Y-%m-%d') if start_str else None
        end_date = datetime.strptime(end_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59) if end_str else None

    print(f"\nDate range: {start_date.strftime('%Y-%m-%d') if start_date else 'Any'} to {end_date.strftime('%Y-%m-%d') if end_date else 'Any'}")

    # Get amount range (optional)
    print("\n\nStep 2: Amount Range (optional)")
    print("-" * 40)
    min_str = input("Minimum amount (or press Enter to skip): ").strip()
    max_str = input("Maximum amount (or press Enter to skip): ").strip()

    min_amount = Decimal(min_str) if min_str else None
    max_amount = Decimal(max_str) if max_str else None

    # Find matching payments
    print("\nSearching for payments...")
    payments = find_donation_payments(start_date, end_date, min_amount, max_amount)

    # Preview
    preview_migration(payments)

    if not payments:
        return

    # Confirm migration
    print("\nStep 3: Confirm Migration")
    print("-" * 40)

    confirm = input(f"Migrate {len(payments)} payment(s) to donations? (yes/no): ").lower().strip()

    if confirm != 'yes':
        print("\nMigration cancelled.")
        return

    # Migration options
    anonymous = input("Make donations anonymous? (y/n): ").lower().strip() == 'y'
    notes_prefix = input("Notes prefix (default: 'Donation drive - '): ").strip() or "Donation drive - "
    delete_orig = input("Delete original payments? (y/n, recommended: y): ").lower().strip() == 'y'

    # Perform migration
    perform_migration(payments, anonymous=anonymous, delete_payments=delete_orig, notes_prefix=notes_prefix)


def main():
    """Main entry point."""
    app = create_app()

    with app.app_context():
        # Check if --dry-run flag is present
        if '--dry-run' in sys.argv:
            # Simple dry run with last weekend's dates
            today = datetime.now()
            days_since_sunday = (today.weekday() + 1) % 7
            last_sunday = today - timedelta(days=days_since_sunday)
            last_saturday = last_sunday - timedelta(days=1)

            start_date = last_saturday.replace(hour=0, minute=0, second=0)
            end_date = last_sunday.replace(hour=23, minute=59, second=59)

            print(f"Searching for payments from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
            payments = find_donation_payments(start_date, end_date)
            preview_migration(payments)
        else:
            # Interactive mode
            interactive_mode()


if __name__ == "__main__":
    main()
