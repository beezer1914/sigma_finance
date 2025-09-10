from datetime import datetime, timedelta
from flask import Blueprint, current_app, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sigma_finance.utils.generate_invite import generate_invite_code
from sigma_finance.models import InviteCode, db
from sigma_finance.utils.decorators import role_required
from sigma_finance.forms import invite_form
from sigma_finance.utils.send_invite_email import send_email
from flask import render_template, redirect, url_for, flash, request
from sigma_finance.models import User
from sigma_finance.extensions import db


invite_bp = Blueprint("invite", __name__, url_prefix="/invite")

@invite_bp.route("/create_invite", methods=["GET", "POST"])
@login_required
@role_required("treasurer")
def create_invite():
    form = invite_form.InviteForm()
    if form.validate_on_submit():
        code, expires_at, role = generate_invite_code(
            role=form.role.data,
            expires_in_days=form.expires_in_days.data
        )
        invite = InviteCode(
            code=code,
            role=role,
            expires_at=expires_at,
            created_by=current_user.id
        )
        db.session.add(invite)
        db.session.commit()

        # ✅ Build and send the email via SendGrid
        signup_url = url_for("auth.register", _external=True)
        context = {
            "code": code,
            "expires_at": expires_at,
            "signup_url": signup_url
        }

        plain_text = render_template("invite/email_invite.txt", **context)
        html_content = render_template("invite/email_invite.html", **context)

        send_email(
            subject="Your Sigma Finance Invite Code",
            to_email=form.email.data,
            plain_text=plain_text,
            html_content=html_content
        )

        flash(f"Invite code sent to: {form.email.data}", "success")
        return redirect(url_for("invite.create_invite"))

    return render_template("treasurer/create_invite.html", form=form)