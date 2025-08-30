from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sigma_finance.utils.generate_invite import generate_invite_code
from sigma_finance.models import InviteCode, db
from sigma_finance.utils.decorators import role_required
from sigma_finance.routes.treasurer import treasurer_bp
from sigma_finance.forms import invite_form
from flask_mail import Message
from sigma_finance.extensions import mail

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

        #Build and send the e-mail

        msg = Message("Your Sigma Finance Invite Code",
                      recipients=[form.email.data])
        
        #render_template can load both .txt and .html versions

        msg.body = render_template("invite/email_invite.txt", code=code, expires_at=expires_at, signup_url=url_for("auth.register", _external=True))
        msg.html = render_template("invite/email_invite.html", code=code, expires_at=expires_at, signup_url=url_for("auth.register", _external=True))
        mail.send(msg)

        flash(f"Invite code sent to: {form.email.data}", "success")
        return redirect(url_for("invite.create_invite"))
    return render_template("treasurer/create_invite.html", form=form)



