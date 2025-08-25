from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from sigma_finance.extensions import db
from sigma_finance.models import Payment, PaymentPlan, ArchivedPaymentPlan
from sigma_finance.forms.one_time_form import PaymentForm as OneTimePaymentForm
from sigma_finance.forms.plan_form import PaymentPlanForm
from sigma_finance.forms.installment_form import InstallmentPaymentForm
from datetime import timedelta, date, datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

payments = Blueprint("payments", __name__)

# 🔁 Helper function to archive completed plans
def archive_plan_if_completed(plan):
    paid = (
        db.session.query(func.sum(Payment.amount))
        .filter_by(user_id=current_user.id, plan_id=plan.id)
        .scalar()
    ) or 0

    if paid >= plan.total_amount - Decimal("0.01") and plan.status != "Completed":
        # ✅ Update status before archiving
        plan.status = "Completed"
        db.session.commit()

        archived = ArchivedPaymentPlan(
            user_id=plan.user_id,
            frequency=plan.frequency,
            start_date=plan.start_date,
            end_date=plan.end_date,
            total_amount=plan.total_amount,
            installment_amount=plan.installment_amount,
            status="Completed",  # ✅ Explicitly set archived status
            completed_on=datetime.utcnow()
        )
        db.session.add(archived)
        db.session.delete(plan)
        db.session.commit()
        flash("You've completed your payment plan! It's now archived.", "info")

@payments.route("/pay", methods=["GET", "POST"])
@login_required
def pay():
    plan = PaymentPlan.query.filter_by(user_id=current_user.id).first()

    if plan:
        form = InstallmentPaymentForm()
        if form.validate_on_submit():
            payment = Payment(
                user_id=current_user.id,
                amount=form.amount.data,
                payment_type="installment",
                method=form.method.data,
                plan_id=plan.id
            )
            db.session.add(payment)
            db.session.commit()
            flash("Installment payment submitted!", "success")

            # ✅ Check if plan is now complete
            archive_plan_if_completed(plan)

            return redirect(url_for("dashboard.show_dashboard"))

        return render_template("submit_installment.html", form=form, plan=plan)

    else:
        form = OneTimePaymentForm()
        if form.validate_on_submit():
            payment = Payment(
                user_id=current_user.id,
                amount=form.amount.data,
                payment_type="one_time",
                method=form.method.data
            )
            db.session.add(payment)
            db.session.commit()
            flash("One-time payment submitted!", "success")

            # ✅ Check if any active plan is now complete
            plan = PaymentPlan.query.filter_by(user_id=current_user.id).first()
            if plan:
                archive_plan_if_completed(plan)

            return redirect(url_for("dashboard.show_dashboard"))

        return render_template("one_time.html", form=form)

@payments.route("/pay/plan", methods=["GET", "POST"])
@login_required
def plan():
    form = PaymentPlanForm()

    if form.validate_on_submit():
        frequency = form.frequency.data
        start_date = form.start_date.data
        total_amount = form.amount.data

        # Define number of payments and interval
        if frequency == "weekly":
            num_payments = 10
            interval = timedelta(weeks=1)
        elif frequency == "monthly":
            num_payments = 5
            interval = relativedelta(months=1)
        elif frequency == "quarterly":
            num_payments = 2
            interval = relativedelta(months=3)
        else:
            num_payments = 1
            interval = timedelta(0)

        installment_amount = round(total_amount / num_payments, 2)
        end_date = start_date + (interval * (num_payments - 1))

        plan = PaymentPlan(
            user_id=current_user.id,
            frequency=frequency,
            start_date=start_date,
            end_date=end_date,
            total_amount=total_amount,
            installment_amount=installment_amount,
            status="Active"
        )

        db.session.add(plan)
        db.session.commit()
        flash("Payment plan enrolled!", "success")
        return redirect(url_for("dashboard.show_dashboard"))

    return render_template("plan.html", form=form)