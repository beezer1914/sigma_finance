from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request
from flask_login import current_user
from sigma_finance.extensions import db
from sigma_finance.models import Donation, User
from sigma_finance.forms.donation_form import DonationForm
from sigma_finance.utils.decorators import role_required
from sigma_finance.extensions import limiter

donations_bp = Blueprint("donations", __name__)

@donations_bp.route("/donate")
def donate():
    """
    Public donation page - displays the Stripe payment link.
    Anyone can access this page to make a donation.
    """
    donation_link = current_app.config.get("DONATION_STRIPE_LINK", "https://donate.stripe.com/aFa9ATdI3gL572jcuMbQY00")
    return render_template("donate.html", donation_link=donation_link)


@donations_bp.route("/donations/manual", methods=["GET", "POST"])
@role_required("treasurer", "admin")
@limiter.limit("20 per minute")
def manual_donation():
    """
    Manual donation entry form for treasurers/admins.
    Used to record donations made via check, cash, or other methods.
    """
    form = DonationForm()

    if form.validate_on_submit():
        # Check if donor is a registered user
        user = User.query.filter_by(email=form.donor_email.data).first()

        donation = Donation(
            donor_name=form.donor_name.data,
            donor_email=form.donor_email.data,
            amount=form.amount.data,
            method=form.method.data,
            anonymous=form.anonymous.data,
            notes=form.notes.data,
            user_id=user.id if user else None
        )

        db.session.add(donation)
        db.session.commit()

        flash(f"Donation of ${form.amount.data} from {form.donor_name.data} recorded successfully!", "success")
        return redirect(url_for("donations.view_donations"))

    return render_template("donations/manual_donation.html", form=form)


@donations_bp.route("/donations")
@role_required("treasurer", "admin")
def view_donations():
    """
    View all donations - only accessible by treasurers and admins.
    Shows all donations with filtering and sorting options.
    """
    # Get query parameters for filtering
    page = request.args.get('page', 1, type=int)
    per_page = 50

    # Query donations
    query = Donation.query.order_by(Donation.date.desc())

    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    donations = pagination.items

    # Calculate total donations
    total_donations = db.session.query(db.func.sum(Donation.amount)).scalar() or 0

    return render_template(
        "donations/view_donations.html",
        donations=donations,
        pagination=pagination,
        total_donations=total_donations
    )


@donations_bp.route("/donations/<int:donation_id>/delete", methods=["POST"])
@role_required("admin")
def delete_donation(donation_id):
    """
    Delete a donation - admin only.
    Use with caution - this is for correcting errors.
    """
    donation = Donation.query.get_or_404(donation_id)

    donor_name = donation.donor_name
    amount = donation.amount

    db.session.delete(donation)
    db.session.commit()

    flash(f"Donation of ${amount} from {donor_name} has been deleted.", "info")
    return redirect(url_for("donations.view_donations"))
