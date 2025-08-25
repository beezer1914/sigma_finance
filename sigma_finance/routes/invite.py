from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sigma_finance.utils.generate_invite import generate_invite_code
from sigma_finance.models import InviteCode, db
from sigma_finance.utils.decorators import role_required
from sigma_finance.routes.treasurer import treasurer_bp

invite_bp = Blueprint("invite", __name__, url_prefix="/invite")

@invite_bp.route("/create", methods=["POST", "GET"])
@login_required
@role_required("treasurer")
def create_invite():
    code = generate_invite_code()
    invite = InviteCode(code=code, expires_at=datetime.utcnow() + timedelta(days=7))
    db.session.add(invite)
    db.session.commit()
    flash(f"Invite code created: {code}", "success")
    return redirect(url_for("treasurer_bp.dashboard"))