from datetime import date, timedelta
from sqlalchemy import func
from sigma_finance.app import create_app
from sigma_finance.extensions import db
from sigma_finance.models import PaymentPlan
from sigma_finance.utils.email_sender import send_payment_reminder

app = create_app()

def send_reminders(test_mode=False, override_email=None):
    upcoming = date.today() + timedelta(days=3)

    plans = PaymentPlan.query.filter(
        PaymentPlan.status.ilike("active"),
        func.date(PaymentPlan.start_date) <= upcoming
    ).all()

    if not plans:
        return

    for plan in plans:
        user = plan.user
        recipient = override_email if test_mode else user.email

        send_payment_reminder(
            to_email=recipient,
            name=user.name,
            due_date=plan.start_date,
            amount=plan.installment_amount
        )

if __name__ == "__main__":
    with app.app_context():
        send_reminders()