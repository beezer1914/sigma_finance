from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sigma_finance.models import Payment, PaymentPlan
from sqlalchemy import func

dashboard = Blueprint("dashboard", __name__)

@dashboard.route("/dashboard")
@login_required
def show_dashboard():
    payments = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.date.desc()).all()
    plan = PaymentPlan.query.filter_by(user_id=current_user.id, status="Active").first()



    remaining_balance = None
    percent_paid = None

    if plan:
        # Sum of installment payments
        paid = (
            Payment.query
            .with_entities(func.sum(Payment.amount))
            .filter_by(user_id=current_user.id, plan_id=plan.id, payment_type="installment")
            .scalar()
        ) or 0

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