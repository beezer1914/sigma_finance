from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import func
from sigma_finance.app import create_app
from sigma_finance.extensions import db
from sigma_finance.models import PaymentPlan, Payment
from sigma_finance.utils.email_sender import send_payment_reminder

app = create_app()

def calculate_next_due_date(plan, today):
    """
    Calculate the next payment due date based on plan frequency.
    Returns None if no payment is due soon.
    """
    start = plan.start_date

    if plan.frequency == 'weekly':
        # Calculate weeks since start
        weeks_elapsed = (today - start).days // 7
        next_due = start + timedelta(weeks=weeks_elapsed + 1)
        # Send reminder if due within next 3 days
        if 0 <= (next_due - today).days <= 3:
            return next_due

    elif plan.frequency == 'monthly':
        # Calculate months since start
        months_elapsed = (today.year - start.year) * 12 + (today.month - start.month)
        next_due = start + relativedelta(months=months_elapsed + 1)
        # Send reminder if it's the 1st of the month (or first 3 days)
        if today.day <= 3:
            return date(today.year, today.month, 1)

    elif plan.frequency == 'quarterly':
        # Calculate quarters since start (every 3 months)
        months_elapsed = (today.year - start.year) * 12 + (today.month - start.month)
        quarters_elapsed = months_elapsed // 3
        next_due = start + relativedelta(months=(quarters_elapsed + 1) * 3)
        # Send reminder if it's the 1st 3 days of a quarter month
        if today.day <= 3 and today.month in [1, 4, 7, 10]:
            return date(today.year, today.month, 1)

    return None

def send_reminders(test_mode=False, override_email=None):
    """
    Send payment reminders to all active payment plan members based on their frequency.
    - Weekly plans: reminded if payment due within 3 days
    - Monthly plans: reminded on 1st-3rd of month
    - Quarterly plans: reminded on 1st-3rd of Jan/Apr/Jul/Oct
    """
    today = date.today()

    # Find all active payment plans that are currently in effect
    plans = PaymentPlan.query.filter(
        PaymentPlan.status.ilike("active"),
        func.date(PaymentPlan.start_date) <= today,
        func.date(PaymentPlan.end_date) >= today
    ).all()

    if not plans:
        print("No active payment plans found")
        return

    print(f"Found {len(plans)} active payment plan(s)")
    sent_count = 0

    for plan in plans:
        user = plan.user  # Get user first, before checking next_due

        # Calculate if reminder is due for this plan
        next_due = calculate_next_due_date(plan, today)

        if next_due:
            recipient = override_email if test_mode else user.email

            send_payment_reminder(
                to_email=recipient,
                name=user.name,
                due_date=next_due,
                amount=plan.installment_amount,
                frequency=plan.frequency
            )
            print(f"✅ Sent {plan.frequency} reminder to {user.name} ({recipient})")
            sent_count += 1
        else:
            print(f"⏭️  Skipped {user.name} - no {plan.frequency} payment due soon")

    print(f"\n📧 Total reminders sent: {sent_count}/{len(plans)}")

if __name__ == "__main__":
    with app.app_context():
        send_reminders()