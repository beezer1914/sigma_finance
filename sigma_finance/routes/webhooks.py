# webhooks.py
from flask import Blueprint, request, current_app
from datetime import datetime
from decimal import Decimal
import stripe

from sigma_finance.extensions import db
from sigma_finance.models import Payment, User, WebhookEvent

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

    # Optional: log every event for audit trail
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

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print(f"💳 Payment for {session['amount_total']} from {session['customer_details']['email']}")

        # Lookup user by email (assuming email is unique or indexed)
        user = User.query.filter_by(email=session["customer_details"]["email"]).first()
        if not user:
            print("❌ No matching user found for email")
            return "", 400

        try:
            new_payment = Payment(
                user_id=user.id,
                amount=Decimal(session["amount_total"]) / 100,  # Stripe sends amount in cents
                method="stripe",
                payment_type="one-time",
                notes=f"Stripe session ID: {session['id']}"
            )
            db.session.add(new_payment)
            db.session.commit()
            print("✅ Payment logged to DB")
        except Exception as e:
            print(f"❌ DB insert error: {e}")

    return "", 200