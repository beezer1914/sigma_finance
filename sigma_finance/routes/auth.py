import datetime
import logging
from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash
from sigma_finance.models import InviteCode, User
from sigma_finance.forms.login_form import LoginForm, ResetPasswordForm,ForgotPasswordForm
from sigma_finance.forms.register_form import RegisterForm
from sigma_finance.extensions import db
from sigma_finance.utils.decorators import role_required
from sigma_finance.utils.send_invite_email import send_password_reset_email

auth = Blueprint("auth", __name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_invite(code):
    if not code:
        return None

    invite = InviteCode.query.filter_by(code=code).first()
    if not invite:
        flash("Invite code not found", "danger")
        return None
    if invite.used:
        flash("Invite code already used", "danger")
        return None
    if invite.expires_at and invite.expires_at < datetime.datetime.utcnow():
        flash("Invite code has expired", "danger")
        return None

    return invite

def get_dashboard_route(user):
    # Maps user roles to their respective dashboard endpoints
    return {
        "treasurer": "treasurer_bp.treasurer_dashboard",  # Defined in treasurer.py
        "member": "dashboard.show_dashboard"
    }.get(user.role, "index")

@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        print("Already authenticated as:", current_user.email)
        print("Role:", current_user.role)
        print("Redirecting to:", get_dashboard_route(current_user))
        return redirect(url_for(get_dashboard_route(current_user)))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            flash("Logged in successfully!", "success")
            print("Logged in as:", user.email)
            print("Role:", user.role)
            print("Redirecting to:", get_dashboard_route(user))
            return redirect(url_for(get_dashboard_route(user)))
        flash("Invalid credentials", "danger")
    else:
        print("Form errors:", form.errors)

    return render_template("login.html", form=form)

@auth.route("/logout")
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for("auth.login"))

@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        code = form.invite_code.data.strip()
        invite = InviteCode.query.filter_by(code=code).first()

        role = invite.role if invite else "member"

        new_user = User(
            name=form.name.data,
            email=form.email.data,
            role=role,
            password_hash=generate_password_hash(form.password.data),
            financial_status="not financial",
            active=True
        )

        try:
            db.session.add(new_user)
            db.session.flush()

            if invite:
                invite.used = True
                invite.used_by = new_user.id
                invite.used_at = datetime.datetime.utcnow()

            db.session.commit()
            flash("Account created successfully!", "success")
            return redirect(url_for("auth.login"))

        except Exception as e:
            db.session.rollback()
            logger.error("Commit failed", exc_info=True)
            flash("An error occurred during registration. Please try again.", "danger")

    return render_template("register.html", form=form)



@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.get_reset_token()
            send_password_reset_email(user)
        flash("If your email is registered, you'll receive a reset link shortly.", "info")
        return redirect(url_for('auth.login'))
    return render_template('forgot_password.html', form=form)


@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_reset_token(token)
    if not user:
        flash("Invalid or expired token.", "danger")
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been updated.", "success")
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', form=form)