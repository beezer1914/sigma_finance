from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from sigma_finance.models import db, User, PaymentPlan, Payment, ArchivedPaymentPlan, InviteCode
from sigma_finance.services.stats import (
    get_total_payments,
    get_payment_summary_by_type,
    get_payment_method_stats,
    get_users_with_active_plans,
    get_unpaid_members,
    get_user_outstanding_balance,
)
from sigma_finance.utils.decorators import role_required
from sigma_finance.utils.generate_invite import generate_invite_code
from sigma_finance.utils.send_invite_email import send_invite_email
from sigma_finance.forms import invite_form
from datetime import datetime

treasurer_bp = Blueprint('treasurer_bp', __name__, url_prefix='/treasurer', template_folder='treasurer')

def is_treasurer():
    return current_user.role in ['admin', 'treasurer']

@treasurer_bp.before_request
@login_required
def restrict_to_treasurers():
    if not is_treasurer():
        flash("Access denied: Treasurer-only area.", "danger")
        return redirect(url_for('index'))

# 📊 Dashboard
@treasurer_bp.route('/', endpoint='treasurer_dashboard')
def treasurer_dashboard():
    total_dues = get_total_payments()
    unpaid_members = get_unpaid_members()
    active_plan_users = get_users_with_active_plans()
    outstanding_balances = {
        user.id: get_user_outstanding_balance(user.id)
        for user in active_plan_users
    }

    return render_template(
        'treasurer/index.html',
        total_dues=total_dues,
        unpaid_members=unpaid_members,
        active_payment_plans=len(active_plan_users),
        outstanding_balances=outstanding_balances,
        active_plan_users=active_plan_users
    )

# 💳 Payment Stats
@treasurer_bp.route('/payments', endpoint='treasurer_payments')
def treasurer_payments():
    return render_template(
        'treasurer/payments.html',
        payment_type_summary=get_payment_summary_by_type(),
        payment_method_stats=get_payment_method_stats()
    )

# 👥 Legacy Members View
@treasurer_bp.route('/members', endpoint='treasurer_members')
def treasurer_members():
    return render_template(
        'treasurer/members.html',
        all_members=User.query.order_by(User.name).all(),
        unpaid_members=get_unpaid_members(),
        active_plan_users=get_users_with_active_plans()
    )

# 🔧 Manage Members (New View)
@treasurer_bp.route('/manage-members', endpoint='treasurer_manage_members')
def treasurer_manage_members():
    users = User.query.order_by(User.name).all()
    return render_template('treasurer/manage-members.html', users=users)

# 🔁 Reset Payments
@treasurer_bp.route("/reset_user/<int:user_id>", methods=["POST"], endpoint='treasurer_reset_user')
def treasurer_reset_user(user_id):
    user = User.query.get_or_404(user