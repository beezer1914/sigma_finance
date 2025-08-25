from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from sigma_finance.models import db, User, PaymentPlan, Payment, ArchivedPaymentPlan
from sigma_finance.services.stats import (
    get_total_payments,
    get_payment_summary_by_type,
    get_payment_method_stats,
    get_users_with_active_plans,
    get_unpaid_members,
    get_user_outstanding_balance,
)
from sigma_finance.utils.decorators import role_required

treasurer_bp = Blueprint('treasurer_bp', __name__, template_folder='../templates/treasurer')

def is_treasurer():
    return current_user.role in ['admin', 'treasurer']

@treasurer_bp.before_request
@login_required
def restrict_to_treasurers():
    if not is_treasurer():
        flash("Access denied: Treasurer-only area.", "danger")
        return redirect(url_for('index'))

# 📊 Dashboard
@treasurer_bp.route('/')
def dashboard():
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
@treasurer_bp.route('/treasurer/payments')
def payments():
    return render_template(
        'treasurer/payments.html',
        payment_type_summary=get_payment_summary_by_type(),
        payment_method_stats=get_payment_method_stats()
    )

# 👥 Legacy Members View
@treasurer_bp.route('/treasurer/members')
def members():
    return render_template(
        'treasurer/members.html',
        all_members=User.query.order_by(User.name).all(),
        unpaid_members=get_unpaid_members(),
        active_plan_users=get_users_with_active_plans()
    )

# 🔧 Manage Members (New View)
@treasurer_bp.route('/manage-members')
def manage_members():
    users = User.query.order_by(User.name).all()
    return render_template('treasurer/manage-members.html', users=users)

# 🔁 Reset Payments
@treasurer_bp.route("/treasurer/reset_user/<int:user_id>", methods=["POST"])
def reset_user_payments(user_id):
    user = User.query.get_or_404(user_id)

    for plan in user.payment_plans:
        for payment in plan.payments:
            db.session.delete(payment)
        db.session.delete(plan)

    archived = ArchivedPaymentPlan.query.filter_by(user_id=user.id).all()
    for plan in archived:
        db.session.delete(plan)

    db.session.commit()
    flash(f"Payment plans and payments reset for {user.name}", "success")
    return redirect(url_for("treasurer_bp.manage_members"))

# ✏️ Edit Member
@treasurer_bp.route('/members/<int:member_id>/edit', methods=['GET', 'POST'])
def edit_member(member_id):
    member = User.query.get_or_404(member_id)
    if request.method == 'POST':
        member.name = request.form['name']
        member.email = request.form['email']
        member.role = request.form['role']
        member.is_active = 'is_active' in request.form  # ✅ Handle checkbox
        db.session.commit()
        flash("Member updated successfully", "success")
        return redirect(url_for('treasurer_bp.manage_members'))
    return render_template('treasurer/edit_member.html', member=member)

# ❌ Deactivate Member
@treasurer_bp.route('/treasurer/members/<int:member_id>/deactivate', methods=['POST'])
def deactivate_member(member_id):
    member = User.query.get_or_404(member_id)
    member.active = False
    db.session.commit()
    flash("Member deactivated", "warning")
    return redirect(url_for('treasurer_bp.manage_members'))

# ✅ Activate Member
@treasurer_bp.route('/treasurer/members/<int:member_id>/activate', methods=['POST'])
def activate_member(member_id):
    member = User.query.get_or_404(member_id)
    member.active = True
    db.session.commit()
    flash("Member activated", "success")
    return redirect(url_for('treasurer_bp.manage_members'))

# ➕ Add Member
@treasurer_bp.route('/treasurer/members/add', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        new_member = User(
            name=request.form['name'],
            email=request.form['email'],
            role=request.form['role'],
            active=True
        )
        new_member.set_password(request.form['password'])
        db.session.add(new_member)
        db.session.commit()
        flash("New member added successfully", "success")
        return redirect(url_for('treasurer_bp.manage_members'))

    return render_template('treasurer/add_members.html')