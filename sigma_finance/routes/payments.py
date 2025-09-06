from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy import func
from sigma_finance.extensions import db
from sigma_finance.models import Payment, PaymentPlan, ArchivedPaymentPlan
from sigma_finance.forms.one_time_form import PaymentForm as OneTimePaymentForm
from sigma_finance.forms.plan_form import PaymentPlanForm
from sigma_finance.forms.installment_form import InstallmentPaymentForm
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from sigma_finance.utils.status_updater import update_financial_status
import stripe

payments = Blueprint("payments", __name__)

# 🔁 Archive completed plans
def archive_plan_if_completed(plan):
    paid = (
        db.session.query(func.sum(Payment.amount))
        .filter_by(user_id=current_user.id, plan_id=plan.id)
        .scalar()
    ) or 0

    if paid >= plan.total_amount - Decimal("0.01") and plan.status != "Completed":
        plan.status = "Completed"
        db.session.commit()

        archived = ArchivedPaymentPlan(
            user_id=plan.user_id,
            frequency=plan.frequency,
            start_date=plan.start_date,
            end_date=plan.end_date,
            total_amount=plan.total_amount,
            installment_amount=plan.installment_amount,
            status="Completed",
            completed_on=datetime.utcnow()
        )
        db.session.add(archived)
        db.session.delete(plan)
        db.session.commit()
        flash("You've completed your payment plan! It's now archived.", "info")

@payments.route("/pay", methods=["GET", "POST"])
@login_required
def pay():
    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]
    plan = PaymentPlan.query.filter_by(user_id=current_user.id).first()
    form = OneTimePaymentForm()

    if form.validate_on_submit():
        if form.method.data == "card" and form.type.data == "one-time":
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": "One-Time Dues"},
                        "unit_amount": int(form.amount.data * 100),
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=url_for("payments.success", _external=True),
                cancel_url=url_for("payments.cancel", _external=True),
                metadata={
                    "user_id": current_user.id,
                    "payment_type": "one_time",
                    "notes": form.notes.data or "",
                    "plan_id": str(plan.id) if plan else None
                }
            )
            return redirect(session.url, code=303)

        payment = Payment(
            user_id=current_user.id,
            amount=form.amount.data,
            payment_type=form.type.data,
            method=form.method.data,
            notes=form.notes.data,
            plan_id=plan.id if plan else None
        )
        db.session.add(payment)
        db.session.commit()
        update_financial_status(current_user.id)
        flash("Manual payment submitted!", "success")

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

@payments.route("/create-one-time-session", methods=["POST"])
@login_required
def create_one_time_session():
    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": "One-Time Payment"},
                "unit_amount": 5000,
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=url_for("payments.success", _external=True),
        cancel_url=url_for("payments.cancel", _external=True),
    )
    return {"id": session.id}

@payments.route("/payment/success")
@login_required
def success():
    flash("Payment successful!", "success")
    return redirect(url_for("dashboard.show_dashboard"))

@payments.route("/payment/cancel")
@login_required
def cancel():
    flash("Payment was canceled or not completed.", "warning")
    return redirect(url_for("dashboard.show_dashboard"))

@payments.route("/")
@login_required
def dashboard():
    if current_user.role == "treasurer":
        payments = Payment.query.order_by(Payment.date.desc()).limit(100).all()
    else:
        payments = (
            Payment.query
            .filter_by(user_id=current_user.id)
            .order_by(Payment.date.desc())
            .limit(100)
            .all()
        )
    print(f"Found {len(payments)} payments")
    return render_template("treasurer/payments.html", payments=payments)