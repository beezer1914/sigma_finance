#!/usr/bin/env python3
"""
Manual Payment Entry Script
Use this to add payments that were missed by webhooks
"""

from sigma_finance.app import create_app
from sigma_finance.models import Payment, User, PaymentPlan
from sigma_finance.extensions import db
from sigma_finance.utils.status_updater import update_financial_status
from sigma_finance.services.stats import invalidate_payment_cache, invalidate_user_cache, invalidate_plan_cache
from datetime import datetime, timezone
from decimal import Decimal

def add_manual_payment():
    """Interactive script to add a manual payment"""

    app = create_app()

    with app.app_context():
        print("\n" + "="*60)
        print("MANUAL PAYMENT ENTRY")
        print("="*60 + "\n")

        # Get user email
        email = input("Enter user email: ").strip()
        user = User.query.filter_by(email=email).first()

        if not user:
            print(f"\n❌ ERROR: No user found with email '{email}'")
            print("   Please check the email and try again.\n")
            return

        print(f"\n✅ Found user: {user.name} (ID: {user.id})")

        # Get payment details
        print("\nEnter payment details:")
        amount = input("  Amount (e.g., 100.00): $").strip()

        try:
            amount = Decimal(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except (ValueError, Exception) as e:
            print(f"\n❌ ERROR: Invalid amount '{amount}'. {e}\n")
            return

        # Payment type
        print("\n  Payment type:")
        print("    1. One-time")
        print("    2. Installment")
        payment_type_choice = input("  Select (1 or 2): ").strip()

        payment_type = "one-time" if payment_type_choice == "1" else "installment"

        # Payment method
        print("\n  Payment method:")
        print("    1. Stripe (default for missed webhooks)")
        print("    2. Cash")
        print("    3. Check")
        print("    4. Other")
        method_choice = input("  Select (1-4, default 1): ").strip() or "1"

        methods = {"1": "stripe", "2": "cash", "3": "check", "4": "other"}
        method = methods.get(method_choice, "stripe")

        # Notes
        notes = input("\n  Notes (optional): ").strip() or "Manual entry - missed webhook"

        # Check for payment plan (check both "active" and "Active" for compatibility)
        plan_id = None
        if payment_type == "installment":
            active_plan = PaymentPlan.query.filter(
                PaymentPlan.user_id == user.id,
                PaymentPlan.status.in_(["active", "Active"])
            ).first()

            if active_plan:
                print(f"\n  Found active payment plan (ID: {active_plan.id})")
                print(f"  Total: ${active_plan.total_amount}, Installment: ${active_plan.installment_amount}")
                link_to_plan = input("  Link this payment to the plan? (y/n, default y): ").strip().lower()
                if link_to_plan != 'n':
                    plan_id = active_plan.id
            else:
                print(f"\n  No active payment plan found for this user")

        # Confirm
        print("\n" + "="*60)
        print("CONFIRM PAYMENT DETAILS:")
        print("="*60)
        print(f"  User:         {user.name} ({user.email})")
        print(f"  Amount:       ${amount}")
        print(f"  Type:         {payment_type}")
        print(f"  Method:       {method}")
        print(f"  Plan ID:      {plan_id or 'None'}")
        print(f"  Notes:        {notes}")
        print("="*60)

        confirm = input("\nAdd this payment? (y/n): ").strip().lower()

        if confirm != 'y':
            print("\n❌ Cancelled. No payment added.\n")
            return

        # Create payment
        try:
            payment = Payment(
                user_id=user.id,
                amount=amount,
                method=method,
                payment_type=payment_type,
                notes=notes,
                date=datetime.now(timezone.utc),
                plan_id=plan_id
            )

            db.session.add(payment)
            db.session.commit()

            print(f"\n✅ SUCCESS! Payment #{payment.id} created")

            # Update financial status
            update_financial_status(user.id)
            print("✅ Financial status updated")

            # Invalidate caches
            invalidate_payment_cache()
            invalidate_user_cache(user.id)
            if plan_id:
                invalidate_plan_cache()
            print("✅ Caches cleared")

            print("\n" + "="*60)
            print("PAYMENT SUCCESSFULLY RECORDED!")
            print("="*60 + "\n")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: Failed to create payment: {e}\n")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    add_manual_payment()
