#!/usr/bin/env python3
"""
Fix duplicate historical payments
This script identifies and removes duplicate historical payments that were imported twice.

Usage: python fix_duplicate_historical_payments.py
"""

import sys
from datetime import datetime
from sigma_finance.app import create_app
from sigma_finance.extensions import db
from sigma_finance.models import Payment, User

def analyze_duplicates(dry_run=True):
    """
    Analyze and optionally fix duplicate historical payments.

    Historical payments are identified by:
    - method='historical'
    - notes containing 'Historical' and 'imported'
    """

    print(f"\n{'='*60}")
    print(f"DUPLICATE HISTORICAL PAYMENTS ANALYSIS")
    print(f"{'='*60}")
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE FIX'}")
    print(f"{'='*60}\n")

    # Get all historical payments
    historical_payments = Payment.query.filter(
        Payment.method == 'historical'
    ).order_by(Payment.user_id, Payment.date, Payment.id).all()

    print(f"Total historical payments found: {len(historical_payments)}")

    if not historical_payments:
        print("No historical payments found. Nothing to fix.")
        return

    # Group by user_id, date, and amount to find duplicates
    from collections import defaultdict
    payment_groups = defaultdict(list)

    for payment in historical_payments:
        # Create a key based on user_id, date, and amount
        key = (payment.user_id, payment.date.date(), float(payment.amount))
        payment_groups[key].append(payment)

    # Find duplicate groups (more than one payment with same key)
    duplicates = {k: v for k, v in payment_groups.items() if len(v) > 1}

    if not duplicates:
        print("\nNo duplicate historical payments found. Database is clean!")
        return

    print(f"\n{'='*60}")
    print(f"FOUND {len(duplicates)} DUPLICATE GROUPS")
    print(f"{'='*60}\n")

    stats = {
        'duplicate_groups': len(duplicates),
        'total_duplicates': 0,
        'payments_to_keep': 0,
        'payments_to_delete': 0,
        'total_amount_to_delete': 0.0
    }

    payments_to_delete = []

    for (user_id, date, amount), payments in duplicates.items():
        user = User.query.get(user_id)

        # Sort by ID (keep the oldest, delete the newer ones)
        payments_sorted = sorted(payments, key=lambda p: p.id)
        keep_payment = payments_sorted[0]
        delete_payments = payments_sorted[1:]

        stats['total_duplicates'] += len(payments)
        stats['payments_to_keep'] += 1
        stats['payments_to_delete'] += len(delete_payments)

        print(f"User: {user.name if user else f'ID:{user_id}'}")
        print(f"  Date: {date}, Amount: ${amount}")
        print(f"  Found {len(payments)} identical payments:")

        for i, payment in enumerate(payments_sorted):
            is_keep = (i == 0)
            status = "KEEP" if is_keep else "DELETE"
            print(f"    [{status}] Payment ID: {payment.id}, Created: {payment.date}")

            if not is_keep:
                payments_to_delete.append(payment)
                stats['total_amount_to_delete'] += float(payment.amount)

        print()

    # Summary
    print(f"{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Duplicate groups found:     {stats['duplicate_groups']}")
    print(f"Total duplicate payments:   {stats['total_duplicates']}")
    print(f"Payments to keep:           {stats['payments_to_keep']}")
    print(f"Payments to delete:         {stats['payments_to_delete']}")
    print(f"Total amount to delete:     ${stats['total_amount_to_delete']:.2f}")
    print(f"{'='*60}\n")

    # Delete duplicates if not dry run
    if not dry_run:
        print("Deleting duplicate payments...")

        try:
            for payment in payments_to_delete:
                db.session.delete(payment)

            db.session.commit()
            print(f"\n[SUCCESS] Deleted {len(payments_to_delete)} duplicate payments!")
            print("User totals will be recalculated automatically.")

        except Exception as e:
            db.session.rollback()
            print(f"\n[ERROR] Failed to delete payments: {str(e)}")
            print("No changes were made.")
            return False
    else:
        print("[DRY RUN] No changes made. Run with dry_run=False to delete duplicates.")

    return True

def recalculate_user_totals():
    """
    Recalculate total_paid for all users based on their payment records.
    This ensures accuracy after deleting duplicates.
    """
    print(f"\n{'='*60}")
    print("RECALCULATING USER TOTALS")
    print(f"{'='*60}\n")

    users = User.query.all()

    for user in users:
        total = sum(float(p.amount) for p in user.payments)
        old_total = user.total_paid if hasattr(user, 'total_paid') else 0

        if old_total != total:
            print(f"{user.name}: ${old_total} -> ${total}")
            if hasattr(user, 'total_paid'):
                user.total_paid = total

    try:
        db.session.commit()
        print("\n[SUCCESS] User totals recalculated!")
    except Exception as e:
        db.session.rollback()
        print(f"\n[ERROR] Failed to recalculate totals: {str(e)}")

def main():
    """Main function"""
    app = create_app()

    with app.app_context():
        print("\nStep 1: Analyzing duplicate payments...\n")

        # First do a dry run
        analyze_duplicates(dry_run=True)

        # Ask for confirmation
        response = input("\nDo you want to delete the duplicate payments? (yes/no): ")

        if response.lower() in ['yes', 'y']:
            print("\n[FIXING] Deleting duplicate payments...\n")
            success = analyze_duplicates(dry_run=False)

            if success:
                # Optionally recalculate user totals
                recalc = input("\nRecalculate user totals to ensure accuracy? (yes/no): ")
                if recalc.lower() in ['yes', 'y']:
                    recalculate_user_totals()

                print("\n[SUCCESS] Fix complete!")
            else:
                print("\n[ERROR] Fix failed. Database unchanged.")
        else:
            print("\n[CANCELLED] No changes made.")

if __name__ == "__main__":
    main()
