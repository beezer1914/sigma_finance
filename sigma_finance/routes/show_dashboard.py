from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sigma_finance.models import Payment, PaymentPlan
from sqlalchemy import func

dashboard = Blueprint("dashboard", __name__)

@dashboard.route("/dashboard")
@login_required
def show_dashboard():
    # Fetch all payments for the current user
    payments = (
        Payment.query
        .filter_by(user_id=current_user.id)
        .order_by(Payment.date.desc())
        .all()
    )

    # Fetch active payment plan, if any
    plan = PaymentPlan.query.filter_by(user_id=current_user.id, status="Active").first()

    # Initialize progress metrics
    remaining_balance = None
    percent_paid = None

    if plan:
        # Sum all payments linked to this plan
        paid = (
            Payment.query
            .with_entities(func.sum(Payment.amount))
            .filter_by(plan_id=plan.id)
            .scalar()
        ) or 0

        # Calculate remaining balance and progress percentage
        remaining_balance = round(plan.total_amount - paid, 2)
        percent_paid = round((paid / plan.total_amount) * 100, 0)

    return render_template(
        "dashboard.html",
        name=current_user.name,
        payments=payments,
        plan=plan,
        remaining_balance=remaining_balance,
        percent_paid=percent_paid
    )