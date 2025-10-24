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
from sigma_finance.utils.send_invite_email import send_email
from sigma_finance.forms import invite_form
from sqlalchemy.orm import joinedload
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

# 📊 Optimized Dashboard
@treasurer_bp.route('/', endpoint='treasurer_dashboard')
def treasurer_dashboard():
    # These functions are now optimized (see stats.py)
    total_dues = get_total_payments()
    unpaid_members = get_unpaid_members()
    active_plan_users = get_users_with_active_plans()
    
    # Calculate outstanding balances
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

# 💰 Optimized Payments View with Pagination
@treasurer_bp.route('/payments', endpoint='treasurer_payments')
@login_required
def treasurer_payments():
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # OPTIMIZATION: Eager load user relationship and paginate
    pagination = (
        Payment.query
        .options(joinedload(Payment.user))  # Prevent N+1 queries
        .order_by(Payment.date.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    
    payments = pagination.items

    return render_template(
        'treasurer/payments.html',
        payments=payments,
        pagination=pagination,
        payment_type_summary=get_payment_summary_by_type(),
        payment_method_stats=get_payment_method_stats()
    )

# 👥 Optimized Members View
@treasurer_bp.route('/members', endpoint='treasurer_members')
def treasurer_members():
    # OPTIMIZATION: Eager load payment relationships
    all_members = (
        User.query
        .options(joinedload(User.payments))
        .options(joinedload(User.payment_plans))
        .order_by(User.name)
        .all()
    )
    
    unpaid_members = get_unpaid_members()
    active_plan_users = get_users_with_active_plans()
    
    return render_template(
        'treasurer/members.html',
        all_members=all_members,
        unpaid_members=unpaid_members,
        active_plan_users=active_plan_users
    )

# 🔧 Manage Members (Optimized)
@treasurer_bp.route('/manage-members', endpoint='treasurer_manage_members')
def treasurer_manage_members():
    # Simple query - no joins needed
    users = User.query.order_by(User.name).all()
    return render_template('treasurer/manage-members.html', users=users)

# 🔁 Confirm Reset Payments
@treasurer_bp.route("/reset_user/<int:user_id>/confirm", methods=["GET"], endpoint='treasurer_confirm_reset_user')
def treasurer_confirm_reset_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("treasurer/confirm_reset.html", user=user)

# 🔁 Reset Payments (Transaction-safe)
@treasurer_bp.route("/reset_user/<int:user_id>", methods=["POST"], endpoint='treasurer_reset_user')
def treasurer_reset_user(user_id):
    # Require confirmation text "DELETE"
    if request.form.get("confirm") != "DELETE":
        flash("Confirmation text must be exactly 'DELETE'", "danger")
        return redirect(url_for("treasurer_bp.treasurer_confirm_reset_user", user_id=user_id))

    user = User.query.get_or_404(user_id)

    try:
        # Use a transaction for safety
        # Delete payments first (foreign key constraint)
        Payment.query.filter_by(user_id=user.id).delete()
        
        # Delete payment plans
        PaymentPlan.query.filter_by(user_id=user.id).delete()
        
        # Delete archived plans
        ArchivedPaymentPlan.query.filter_by(user_id=user.id).delete()
        
        db.session.commit()
        flash(f"Payment plans and payments reset for {user.name}", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error resetting user: {str(e)}", "danger")
    
    return redirect(url_for("treasurer_bp.treasurer_manage_members"))

# ✏️ Edit Member
@treasurer_bp.route("/edit-member/<int:member_id>", methods=["GET", "POST"])
@login_required
def treasurer_edit_member(member_id):
    member = User.query.get_or_404(member_id)

    if request.method == "POST":
        member.name = request.form["name"]
        member.email = request.form["email"]
        member.role = request.form["role"].lower()
        member.active = "is_active" in request.form

        submitted_status = request.form.get("financial_status")
        member.financial_status = submitted_status.lower() if submitted_status else member.financial_status

        initiation_date_raw = request.form.get("initiation_date")
        if initiation_date_raw:
            try:
                member.initiation_date = datetime.strptime(initiation_date_raw, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid initiation date format. Please use YYYY-MM-DD.", "error")

        db.session.commit()
        flash(f"Updated member: {member.name}", "success")
        return redirect(url_for("treasurer_bp.treasurer_manage_members"))

    return render_template("treasurer/edit_member.html", member=member)

# ❌ Deactivate Member
@treasurer_bp.route('/members/<int:member_id>/deactivate', methods=['POST'], endpoint='treasurer_deactivate_member')
def treasurer_deactivate_member(member_id):
    member = User.query.get_or_404(member_id)
    member.active = False
    db.session.commit()
    flash("Member deactivated", "warning")
    return redirect(url_for('treasurer_bp.treasurer_manage_members'))

# ✅ Activate Member
@treasurer_bp.route('/members/<int:member_id>/activate', methods=['POST'], endpoint='treasurer_activate_member')
def treasurer_activate_member(member_id):
    member = User.query.get_or_404(member_id)
    member.active = True
    db.session.commit()
    flash("Member activated", "success")
    return redirect(url_for('treasurer_bp.treasurer_manage_members'))

# ➕ Add Member
@treasurer_bp.route('/members/add', methods=['GET', 'POST'], endpoint='treasurer_add_member')
def treasurer_add_member():
    if request.method == 'POST':
        initiation_date_raw = request.form.get("initiation_date")
        initiation_date = None

        if initiation_date_raw:
            try:
                initiation_date = datetime.strptime(initiation_date_raw, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid initiation date format. Please use YYYY-MM-DD.", "error")
                return redirect(url_for('treasurer_bp.treasurer_add_member'))

        new_member = User(
            name=request.form["name"],
            email=request.form["email"],
            role=request.form["role"].lower(),  # normalize casing
            active=True,
            initiation_date=initiation_date
        )
        new_member.set_password(request.form["password"])
        db.session.add(new_member)
        db.session.commit()

        flash("🕊️ New member added successfully", "success")
        return redirect(url_for('treasurer_bp.treasurer_manage_members'))

    return render_template('treasurer/add_members.html')

# 📩 Invite Dashboard
@treasurer_bp.route('/invite-dashboard', endpoint='treasurer_invite_dashboard')
def treasurer_invite_dashboard():
    invites = InviteCode.query.order_by(InviteCode.created_at.desc()).all()
    form = invite_form.InviteForm()
    return render_template('treasurer/invite_dashboard.html', invites=invites, form=form)

# ✉️ Send Invite
@treasurer_bp.route("/send_invite", methods=["GET"], endpoint='treasurer_send_invite')
def treasurer_send_invite():
    email = request.form.get("email")
    role = request.form.get("role", "member")
    code = generate_invite_code(role=role)
    send_email(email, code)
    flash(f"Invite sent to {email}", "success")
    return redirect(url_for("treasurer_bp.treasurer_dashboard"))

# 🔧 Manage Invites
@treasurer_bp.route("/manage_invites", methods=["POST"], endpoint='treasurer_manage_invites')
def treasurer_manage_invites():
    action = request.form.get("action")
    if not action:
        flash("No action specified", "warning")
        return redirect(url_for("treasurer_bp.treasurer_invite_dashboard"))

    action_type, invite_id = action.split("_")
    invite = InviteCode.query.get(invite_id)

    if not invite:
        flash("Invite not found", "danger")
        return redirect(url_for("treasurer_bp.treasurer_invite_dashboard"))

    if action_type == "resend":
        send_email(invite.email, invite.code)
        flash(f"Resent invite to {invite.email}", "info")

    elif action_type == "revoke" and invite.status == "active":
        db.session.delete(invite)
        db.session.commit()
        flash(f"Revoked invite for {invite.email}", "warning")

    elif action_type == "update":
        invite.role = request.form.get(f"role_{invite.id}")
        invite.expires = datetime.strptime(request.form.get(f"expires_{invite.id}"), "%Y-%m-%d")
        db.session.commit()
        flash(f"Updated invite for {invite.email}", "success")

    return redirect(url_for("treasurer_bp.treasurer_invite_dashboard"))