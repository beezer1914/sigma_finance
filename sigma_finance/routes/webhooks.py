# webhooks.py
from flask import Blueprint, request, current_app
from datetime import datetime
from decimal import Decimal
import stripe

from sigma_finance.extensions import db
from sigma_finance.models import Payment, User, WebhookEvent, PaymentPlan
from sigma_finance.utils.status_updater import update_financial_status
from sigma_finance.routes.payments import archive_plan_if_completed

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def stripe_webhook():
    print("✅ Webhook received")

    payload = request.get_data(as_text=False)
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            current_app.config["STRIPE_WEBHOOK_SECRET"]
        )
    except Exception as e:
        print(f"❌ Webhook signature error: {e}")
        return "", 400

    print(f"📦 Event type: {event['type']}")

    # Audit log for all events
    try:
        audit = WebhookEvent(
            event_type=event["type"],
            payload=payload.decode("utf-8"),
            received_at=datetime.utcnow()
        )
        db.session.add(audit)
        db.session.commit()
        print("📝 Webhook event logged")
    except Exception as e:
        print(f"⚠️ Audit log error: {e}")

    # Handle completed checkout session
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})
        email = session.get("customer_details", {}).get("email")
        plan_id = metadata.get("plan_id")

        print(f"📧 Email: {email}")
        print(f"🧾 Metadata: {metadata}")
        print(f"📌 Plan ID: {plan_id}")

        if not email:
            print("❌ Missing customer email in session")
            return "", 400

        user = User.query.filter_by(email=email).first()
        if not user:
            print("❌ No matching user found for email")
            return "", 400

        try:
            new_payment = Payment(
                user_id=user.id,
                amount=Decimal(session["amount_total"]) / 100,
                method="stripe",
                payment_type=metadata.get("payment_type", "one_time"),
                notes=metadata.get("notes", ""),
                plan_id=int(plan_id) if plan_id else None
            )
            db.session.add(new_payment)
            db.session.commit()
            print("✅ Payment logged to DB")

            update_financial_status(user.id)

            if new_payment.plan_id:
                print(f"🔄 Checking if plan {new_payment.plan_id} should be archived")
                plan = PaymentPlan.query.get(new_payment.plan_id)
                if plan:
                    archive_plan_if_completed(plan, user.id)

        except Exception as e:
            print(f"❌ DB insert error: {e}")

    return "", 200