#!/usr/bin/env python3
"""
Simple Manual Payment Entry - Non-Interactive
Edit the variables below and run: python add_payment_simple.py
"""

from sigma_finance.app import create_app
from sigma_finance.models import Payment, User, PaymentPlan
from sigma_finance.extensions import db
from sigma_finance.utils.status_updater import update_financial_status
from sigma_finance.services.stats import invalidate_payment_cache, invalidate_user_cache, invalidate_plan_cache
from datetime import datetime, timezone
from decimal import Decimal

# ============================================================
# EDIT THESE VALUES:
# ============================================================
USER_EMAIL = "user@example.com"  # ← Change this
AMOUNT = "100.00"                 # ← Change this
PAYMENT_TYPE = "installment"     # ← "installment" or "one-time"
PAYMENT_METHOD = "stripe"        # ← "stripe", "cash", "check", etc.
NOTES = "Manual entry - missed webhook from earlier today"
LINK_TO_ACTIVE_PLAN = True       # ← Set to False if not linking to plan
# ============================================================

def add_payment():
    app = create_app()

    with app.app_context():
        print("\n" + "="*60)
        print("MANUAL PAYMENT ENTRY (Non-Interactive)")
        print("="*60 + "\n")

        # Find user
        user = User.query.filter_by(email=USER_EMAIL).first()
        if not user:
            print(f"❌ ERROR: No user found with email '{USER_EMAIL}'")
            return False

        print(f"✅ Found user: {user.name} (ID: {user.id})")

        # Parse amount
        try:
            amount = Decimal(AMOUNT)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except Exception as e:
            print(f"❌ ERROR: Invalid amount '{AMOUNT}': {e}")
            return False

        # Find active plan if needed (check both "active" and "Active")
        plan_id = None
        if PAYMENT_TYPE == "installment" and LINK_TO_ACTIVE_PLAN:
            active_plan = PaymentPlan.query.filter(
                PaymentPlan.user_id == user.id,
                PaymentPlan.status.in_(["active", "Active"])
            ).first()
            if active_plan:
                plan_id = active_plan.id
                print(f"✅ Linking to active payment plan (ID: {plan_id})")

        # Create payment
        try:
            payment = Payment(
                user_id=user.id,
                amount=amount,
                method=PAYMENT_METHOD,
                payment_type=PAYMENT_TYPE,
                notes=NOTES,
                date=datetime.now(timezone.utc),
                plan_id=plan_id
            )

            db.session.add(payment)
            db.session.commit()

            print(f"\n✅ SUCCESS! Payment #{payment.id} created")
            print(f"   User:   {user.name}")
            print(f"   Amount: ${amount}")
            print(f"   Type:   {PAYMENT_TYPE}")
            print(f"   Method: {PAYMENT_METHOD}")
            print(f"   Plan:   {plan_id or 'None'}")

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
            return True

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: Failed to create payment: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = add_payment()
    exit(0 if success else 1)
