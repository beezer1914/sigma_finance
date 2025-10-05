from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sigma_finance.models import Payment, PaymentPlan
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from sigma_finance.extensions import db

dashboard = Blueprint("dashboard", __name__)

@dashboard.route("/dashboard")
@login_required
def show_dashboard():
    # Fetch all payments for the current user
    payments = (
        Payment.query
        .options(joinedload(Payment.plan))  # Prevent N+1 query for plan
        .filter_by(user_id=current_user.id)
        .order_by(Payment.date.desc())
        .limit(20)  # Only show recent payments
        .all()
    )

    # Fetch active payment plan, if any
    plan = (
        PaymentPlan.query
        .filter_by(user_id=current_user.id, status="Active")
        .first()
    )

    # Initialize progress metrics
    remaining_balance = None
    percent_paid = None

    if plan:
        # OPTIMIZATION 3: Use aggregate query instead of loading all payments
        # This is MUCH faster than: sum(p.amount for p in plan.payments)
        paid = (
            db.session.query(func.sum(Payment.amount))
            .filter_by(plan_id=plan.id)
            .scalar() or 0
        )
        
        # Calculate remaining balance and progress percentage
        total = float(plan.total_amount)
        paid_amount = float(paid)
        
        remaining_balance = round(total - paid_amount, 2)
        percent_paid = round((paid_amount / total) * 100, 0) if total > 0 else 0

    return render_template(
        "dashboard.html",
        name=current_user.name,
        payments=payments,
        plan=plan,
        remaining_balance=remaining_balance,
        percent_paid=percent_paid
    )

@dashboard.route("/payment-history")
@login_required
def payment_history():
    """
    Full payment history with pagination for users who want to see all payments
    """
    from flask import request
    
    page = request.args.get('page', 1, type=int)
    per_page = 25
    
    # Paginated query with eager loading
    pagination = (
        Payment.query
        .options(joinedload(Payment.plan))
        .filter_by(user_id=current_user.id)
        .order_by(Payment.date.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    
    return render_template(
        'payment_history.html',
        payments=pagination.items,
        pagination=pagination
    )