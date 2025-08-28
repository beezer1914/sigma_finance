from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sigma_finance.utils.generate_invite import generate_invite_code
from sigma_finance.models import InviteCode, db
from sigma_finance.utils.decorators import role_required
from sigma_finance.routes.treasurer import treasurer_bp
from sigma_finance.forms import invite_form

invite_bp = Blueprint("invite", __name__, url_prefix="/invite")

@invite_bp.route("/create", methods=["GET", "POST"])
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
        flash(f"Invite code created: {code}", "success")
        return redirect(url_for("invite.create_invite"))
    return render_template("treasurer/create_invite.html", form=form)



