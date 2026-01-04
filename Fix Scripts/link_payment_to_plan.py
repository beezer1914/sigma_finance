#!/usr/bin/env python3
"""
Link an existing payment to a payment plan
Use this if you forgot to link a payment when creating it
"""

from sigma_finance.app import create_app
from sigma_finance.models import Payment, User, PaymentPlan, ArchivedPaymentPlan
from sigma_finance.extensions import db
from sigma_finance.services.stats import invalidate_payment_cache, invalidate_user_cache, invalidate_plan_cache
from sigma_finance.utils.status_updater import update_financial_status
from datetime import datetime, timezone
from decimal import Decimal

def link_payment_to_plan():
    app = create_app()

    with app.app_context():
        print("\n" + "="*60)
        print("LINK PAYMENT TO PLAN")
        print("="*60 + "\n")

        # Get user email
        email = input("Enter user email: ").strip()
        user = User.query.filter_by(email=email).first()

        if not user:
            print(f"\n❌ ERROR: No user found with email '{email}'\n")
            return

        print(f"\n✅ Found user: {user.name} (ID: {user.id})")

        # Show recent payments without plan_id
        recent_payments = Payment.query.filter_by(
            user_id=user.id,
            plan_id=None
        ).order_by(Payment.date.desc()).limit(5).all()

        if not recent_payments:
            print("\n❌ No unlinked payments found for this user.\n")
            return

        print("\nRecent unlinked payments:")
        for p in recent_payments:
            print(f"  {p.id}. ${p.amount} - {p.date.strftime('%Y-%m-%d %H:%M')} ({p.payment_type})")

        payment_id = input("\nEnter payment ID to link: ").strip()
        payment = Payment.query.get(int(payment_id))

        if not payment or payment.user_id != user.id:
            print("\n❌ Invalid payment ID\n")
            return

        # Find active plans (try both "active" and "Active")
        active_plan = PaymentPlan.query.filter(
            PaymentPlan.user_id == user.id,
            PaymentPlan.status.in_(["active", "Active"])
        ).first()

        if not active_plan:
            print(f"\n❌ No active payment plan found for {user.name}\n")
            return

        print(f"\n✅ Found active plan:")
        print(f"   Plan ID: {active_plan.id}")
        print(f"   Total: ${active_plan.total_amount}")
        print(f"   Installment: ${active_plan.installment_amount}")
        print(f"   Frequency: {active_plan.frequency}")

        confirm = input("\nLink this payment to this plan? (y/n): ").strip().lower()

        if confirm != 'y':
            print("\n❌ Cancelled.\n")
            return

        try:
            payment.plan_id = active_plan.id
            db.session.commit()

            print(f"\n✅ SUCCESS! Payment #{payment.id} linked to plan #{active_plan.id}")

            # Check if plan is now complete
            all_payments = Payment.query.filter_by(
                user_id=user.id,
                plan_id=active_plan.id
            ).all()

            total_paid = sum(p.amount for p in all_payments)
            print(f"\n📊 Plan Progress:")
            print(f"   Total Paid: ${total_paid}")
            print(f"   Total Due:  ${active_plan.total_amount}")
            print(f"   Remaining:  ${active_plan.total_amount - total_paid}")

            # Check if complete
            if total_paid >= active_plan.total_amount - Decimal("0.01"):
                print(f"\n🎉 Plan is COMPLETE! Archiving...")

                archived = ArchivedPaymentPlan(
                    user_id=active_plan.user_id,
                    frequency=active_plan.frequency,
                    start_date=active_plan.start_date,
                    end_date=active_plan.end_date,
                    total_amount=active_plan.total_amount,
                    installment_amount=active_plan.installment_amount,
                    status="Completed",
                    completed_on=datetime.now(timezone.utc)
                )
                db.session.add(archived)
                db.session.delete(active_plan)
                db.session.commit()

                print(f"✅ Plan archived successfully!")

                # Update financial status
                update_financial_status(user.id)
                print(f"✅ Financial status updated")

            # Clear caches
            invalidate_payment_cache()
            invalidate_user_cache(user.id)
            invalidate_plan_cache()
            print("✅ Caches cleared\n")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: {e}\n")

if __name__ == "__main__":
    link_payment_to_plan()
