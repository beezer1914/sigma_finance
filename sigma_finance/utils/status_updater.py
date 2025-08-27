from datetime import datetime
from sigma_finance.models import User, Payment, PaymentPlan
from sigma_finance.extensions import db

def update_financial_status(user_id):
    user = User.query.get(user_id)
    if not user:
        return False

    current_year = datetime.utcnow().year

    # Check for one-time payment of $200 made this year
    one_time_payment = user.payments.filter(
        Payment.payment_type == "one-time",
        Payment.amount == 200,
        db.extract("year", Payment.date) == current_year
    ).first()

    # Check for any completed payment plan with end_date in current year
    completed_plan = any(
        plan.total_paid() >= plan.total_amount and plan.end_date.year == current_year
        for plan in user.payment_plans
    )

    if one_time_payment or completed_plan:
        user.financial_status = "financial"
        db.session.commit()
        return True

    return False