import datetime
from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_user
from flask_login import logout_user
from sigma_finance.models import InviteCode, User
from sigma_finance.forms.login_form import LoginForm
from sigma_finance.forms.register_form import RegisterForm
from sigma_finance.extensions import db, bcrypt
from sigma_finance.utils.decorators import role_required
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", __name__)

from flask_login import current_user

@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.show_dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)  # ✅ persistent session
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
    form = RegisterForm()
    code = request.args.get("code")
    invite = None

    # 🔍 Validate invite code before form submission
    if code:
        invite = InviteCode.query.filter_by(code=code, used=False).first()
        if not invite or (invite.expires_at and invite.expires_at < datetime.utcnow()):
            flash("Invalid or expired invite code", "danger")
            return redirect(url_for("auth.register"))

    if form.validate_on_submit():
        # 🧠 Use role from invite if present, fallback to 'member'
        role = invite.role if invite else "member"

        # 👤 Create new user with default financial status and active flag
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            role=role,
            password_hash=generate_password_hash(form.password.data),
            financial_status="not financial",
            active=True
        )

        db.session.add(new_user)
        db.session.flush()  # Ensures new_user.id is available before commit

        # 🔐 Mark invite as used and link to user
        if invite:
            invite.used = True
            invite.used_by = new_user.id

        db.session.commit()
        flash("Account created successfully!", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)



