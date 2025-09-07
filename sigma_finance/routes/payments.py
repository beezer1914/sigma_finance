from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request
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
def archive_plan_if_completed(plan, user_id, silent=False):
    db.session.expire_all()

    payments = Payment.query.filter_by(user_id=user_id, plan_id=plan.id).all()
    paid = sum(p.amount for p in payments)
    actual_installments = len(payments)
    expected_installments = plan.expected_installments or 0

    print(f"🧮 Paid: {paid}, Target: {plan.total_amount}")
    print(f"📆 Installments: {actual_installments} / {expected_installments}")

    meets_installment_requirement = (not plan.enforce_installments or actual_installments >= expected_installments)

    if paid >= plan.total_amount - Decimal("0.01") and meets_installment_requirement and plan.status != "Completed":

        try:
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

            print(f"📁 Plan {plan.id} archived for user_id {user_id}")

            if not silent:
                flash("🎉 You've completed your payment plan! It's now archived.", "info")

        except Exception as e:
            print(f"❌ Archival failed: {e}")
    else:
        print(f"⏳ Plan {plan.id} not archived — paid: {paid}, required: {plan.total_amount}, installments: {actual_installments}/{expected_installments}")

@payments.route("/pay", methods=["GET", "POST"])
@login_required
def pay():
    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]
    plan = PaymentPlan.query.filter_by(user_id=current_user.id).first()

    # Determine payment type from query param or fallback
    payment_type = request.args.get("type", "one-time")

    if payment_type == "installment":
        form = InstallmentPaymentForm()
        template = "submit_installment.html"
    else:
        form = OneTimePaymentForm()
        template = "one_time.html"

    if form.validate_on_submit():
        # Use form.type.data if available, fallback to payment_type
        payment_kind = getattr(form, "type", None)
        payment_type_value = payment_kind.data if payment_kind else payment_type

        if form.method.data == "card":
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Installment Payment" if payment_type_value == "installment" else "One-Time Dues"
                        },
                        "unit_amount": int(form.amount.data * 100),
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=url_for("payments.success", _external=True),
                cancel_url=url_for("payments.cancel", _external=True),
                metadata={
                    "user_id": current_user.id,
                    "payment_type": payment_type_value,
                    "notes": form.notes.data or "",
                    "plan_id": str(plan.id) if plan else ""
                }
            )
            return redirect(session.url, code=303)

        # Manual payment logic
        payment = Payment(
            user_id=current_user.id,
            amount=form.amount.data,
            payment_type=payment_type_value,
            method=form.method.data,
            notes=form.notes.data,
            plan_id=plan.id if plan else None
        )
        db.session.add(payment)
        db.session.commit()
        update_financial_status(current_user.id)
        flash("Manual payment submitted!", "success")

        if plan:
            archive_plan_if_completed(plan, current_user.id)

        return redirect(url_for("dashboard.show_dashboard"))

    return render_template(template, form=form, plan=plan)


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
            expected_installments=num_payments,
            enforce_installments=False,
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