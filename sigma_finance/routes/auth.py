import datetime
from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash
from sigma_finance.models import InviteCode, User
from sigma_finance.forms.login_form import LoginForm
from sigma_finance.forms.register_form import RegisterForm
from sigma_finance.extensions import db
from sigma_finance.utils.decorators import role_required
import logging

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

@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.show_dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            flash("Logged in successfully!", "success")
            return redirect(url_for("dashboard.show_dashboard"))
        flash("Invalid credentials", "danger")

    return render_template("login.html", form=form)

@auth.route("/logout")
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for("auth.login"))

@auth.route("/register", methods=["GET", "POST"])
def register():
    logger.info("Register route accessed")

    form = RegisterForm()
    code = request.args.get("code")
    

    if form.validate_on_submit():
        invite = InviteCode.query.filter_by(code=code, used=False).first()
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
            db.session.flush()  # Ensure new_user.id is available

            if invite:
                logger.info(f"Marking invite {invite.code} as used by user {new_user.id}")
                invite.used = True
                invite.used_by = new_user.id
                invite.used_at = datetime.datetime.utcnow()
                #db.session.merge(invite)

            db.session.commit()
            flash("Account created successfully!", "success")
            return redirect(url_for("auth.login"))

        except Exception as e:
            db.session.rollback()
            logger.error("Commit failed", exc_info=True)
            flash("An error occurred during registration. Please try again.", "danger")

    return render_template("register.html", form=form)