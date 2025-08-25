from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import db, PaymentPlan  # Add other models if needed

dashboard = Blueprint("dashboard", __name__)

@dashboard.route("/history")
@login_required
def payment_history():
    completed_plans = (
        PaymentPlan.query
        .filter_by(user_id=current_user.id, status="Completed")
        .order_by(PaymentPlan.completed_on.desc())
        .all()
    )
    return render_template("history.html", plans=completed_plans)