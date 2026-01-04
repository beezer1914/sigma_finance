#!/usr/bin/env python3
"""
Check and archive completed payment plans
Run this after manually adding payments to ensure plans are properly archived
"""

from sigma_finance.app import create_app
from sigma_finance.models import Payment, PaymentPlan, ArchivedPaymentPlan, User
from sigma_finance.extensions import db
from sigma_finance.services.stats import invalidate_payment_cache, invalidate_user_cache, invalidate_plan_cache
from sigma_finance.utils.status_updater import update_financial_status
from datetime import datetime, timezone
from decimal import Decimal

def archive_completed_plans():
    app = create_app()

    with app.app_context():
        print("\n" + "="*60)
        print("ARCHIVE COMPLETED PAYMENT PLANS")
        print("="*60 + "\n")

        # Find all active plans (check both "active" and "Active")
        active_plans = PaymentPlan.query.filter(
            PaymentPlan.status.in_(["active", "Active"])
        ).all()

        if not active_plans:
            print("✅ No active payment plans found.\n")
            return

        print(f"Found {len(active_plans)} active payment plan(s)\n")

        archived_count = 0

        for plan in active_plans:
            user = User.query.get(plan.user_id)
            if not user:
                continue

            # Get all payments for this plan
            payments = Payment.query.filter_by(
                user_id=plan.user_id,
                plan_id=plan.id
            ).all()

            paid = sum(p.amount for p in payments)
            actual_installments = len(payments)
            expected_installments = plan.expected_installments or 0

            print(f"\nPlan #{plan.id} - {user.name} ({user.email})")
            print(f"  Total Amount:   ${plan.total_amount}")
            print(f"  Paid:           ${paid}")
            print(f"  Remaining:      ${plan.total_amount - paid}")
            print(f"  Installments:   {actual_installments} / {expected_installments}")
            print(f"  Enforce Count:  {plan.enforce_installments}")

            # Check if plan is complete
            meets_amount = paid >= plan.total_amount - Decimal("0.01")
            meets_installments = (not plan.enforce_installments or
                                actual_installments >= expected_installments)

            if meets_amount and meets_installments:
                print(f"  Status:         ✅ COMPLETE - Should be archived")

                confirm = input(f"\n  Archive this plan? (y/n): ").strip().lower()
                if confirm != 'y':
                    print("  ⏭️  Skipped")
                    continue

                try:
                    # Archive the plan
                    archived = ArchivedPaymentPlan(
                        user_id=plan.user_id,
                        frequency=plan.frequency,
                        start_date=plan.start_date,
                        end_date=plan.end_date,
                        total_amount=plan.total_amount,
                        installment_amount=plan.installment_amount,
                        status="Completed",
                        completed_on=datetime.now(timezone.utc)
                    )
                    db.session.add(archived)
                    db.session.delete(plan)
                    db.session.commit()

                    print(f"  ✅ Plan archived successfully!")

                    # Update user's financial status
                    update_financial_status(user.id)

                    # Clear caches
                    invalidate_payment_cache()
                    invalidate_user_cache(user.id)
                    invalidate_plan_cache()

                    archived_count += 1

                except Exception as e:
                    db.session.rollback()
                    print(f"  ❌ ERROR archiving plan: {e}")

            else:
                print(f"  Status:         ⏳ INCOMPLETE")
                if not meets_amount:
                    print(f"                  - Still needs ${plan.total_amount - paid}")
                if not meets_installments:
                    print(f"                  - Needs {expected_installments - actual_installments} more installment(s)")

        print("\n" + "="*60)
        print(f"SUMMARY: {archived_count} plan(s) archived")
        print("="*60 + "\n")

if __name__ == "__main__":
    archive_completed_plans()
