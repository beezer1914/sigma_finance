from flask import Blueprint, request, current_app
from datetime import datetime, timedelta
from decimal import Decimal
import stripe

from sigma_finance.extensions import db
from sigma_finance.models import Payment, User, WebhookEvent, PaymentPlan
from sigma_finance.utils.status_updater import update_financial_status
from sigma_finance.routes.payments import archive_plan_if_completed
from sigma_finance.services.stats import invalidate_payment_cache, invalidate_user_cache, invalidate_plan_cache

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def stripe_webhook():
    """
    Secure Stripe webhook handler with enhanced security features:
    - Signature verification
    - Idempotency (duplicate prevention)
    - Event ID tracking
    - Timestamp validation
    - Comprehensive error handling
    """
    print("✅ Webhook received")

    payload = request.get_data(as_text=False)
    sig_header = request.headers.get("Stripe-Signature")

    # SECURITY CHECK 1: Verify Stripe signature
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            current_app.config["STRIPE_WEBHOOK_SECRET"]
        )
    except ValueError as e:
        print(f"❌ Invalid payload: {e}")
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError as e:
        print(f"❌ Invalid signature: {e}")
        return "Invalid signature", 400

    print(f"📦 Event type: {event['type']}")
    event_id = event.get('id')
    
    # SECURITY CHECK 2: Verify event timestamp (reject events older than 5 minutes)
    event_timestamp = event.get('created')
    if event_timestamp:
        event_time = datetime.fromtimestamp(event_timestamp)
        time_diff = datetime.utcnow() - event_time
        if time_diff > timedelta(minutes=5):
            print(f"⚠️ Event too old: {time_diff.total_seconds()}s")
            return "Event timestamp too old", 400

    # SECURITY CHECK 3: Check for duplicate events (idempotency)
    existing_event = WebhookEvent.query.filter_by(
        event_type=event["type"],
        payload=payload.decode("utf-8")
    ).first()
    
    if existing_event and existing_event.processed:
        print(f"⚠️ Duplicate webhook detected: {event_id}")
        return "Event already processed", 200  # Return 200 to prevent Stripe retries

    # Audit log for all events
    try:
        audit = WebhookEvent(
            event_type=event["type"],
            payload=payload.decode("utf-8"),
            received_at=datetime.utcnow(),
            processed=False
        )
        db.session.add(audit)
        db.session.commit()
        print("📝 Webhook event logged")
    except Exception as e:
        print(f"⚠️ Audit log error: {e}")
        db.session.rollback()
        return "Failed to log event", 500

    # Handle completed checkout session
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})
        email = session.get("customer_details", {}).get("email")
        plan_id = metadata.get("plan_id")
        amount_total = session.get("amount_total")

        print(f"📧 Email: {email}")
        print(f"🧾 Metadata: {metadata}")
        print(f"📌 Plan ID: {plan_id}")
        print(f"💰 Amount: ${amount_total / 100 if amount_total else 0}")

        # VALIDATION: Check required fields
        if not email:
            print("❌ Missing customer email in session")
            audit.notes = "Missing customer email"
            db.session.commit()
            return "Missing customer email", 400

        if not amount_total or amount_total <= 0:
            print("❌ Invalid payment amount")
            audit.notes = "Invalid amount"
            db.session.commit()
            return "Invalid amount", 400

        # Find user
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"❌ No matching user found for email: {email}")
            audit.notes = f"User not found: {email}"
            db.session.commit()
            return "User not found", 404

        # SECURITY CHECK 4: Prevent duplicate payments (same user, same amount, within 5 minutes)
        recent_payment = Payment.query.filter(
            Payment.user_id == user.id,
            Payment.amount == Decimal(amount_total) / 100,
            Payment.date >= datetime.utcnow() - timedelta(minutes=5)
        ).first()
        
        if recent_payment:
            print(f"⚠️ Duplicate payment detected for user {user.id}")
            audit.processed = True
            audit.notes = f"Duplicate payment prevented (existing payment ID: {recent_payment.id})"
            db.session.commit()
            return "Duplicate payment", 200

        # Create payment record
        try:
            new_payment = Payment(
                user_id=user.id,
                amount=Decimal(amount_total) / 100,
                method="stripe",
                payment_type=metadata.get("payment_type", "one_time"),
                notes=metadata.get("notes", ""),
                plan_id=int(plan_id) if plan_id else None
            )
            db.session.add(new_payment)
            
            # Mark webhook as processed
            audit.processed = True
            audit.notes = f"Payment created successfully: ID {new_payment.id}"
            
            db.session.commit()
            print(f"✅ Payment logged to DB: ID {new_payment.id}")

            # Invalidate caches
            invalidate_payment_cache()
            invalidate_user_cache(user.id)
            if plan_id:
                invalidate_plan_cache()

            # Update financial status
            update_financial_status(user.id)

            # Check if payment plan should be archived
            if new_payment.plan_id:
                print(f"🔄 Checking if plan {new_payment.plan_id} should be archived")
                plan = PaymentPlan.query.get(new_payment.plan_id)
                if plan:
                    archive_plan_if_completed(plan, user.id, silent=True)

        except Exception as e:
            print(f"❌ Payment processing error: {e}")
            db.session.rollback()
            audit.notes = f"Processing error: {str(e)}"
            db.session.commit()
            return "Payment processing failed", 500

    # Handle other event types (can add more as needed)
    elif event["type"] == "checkout.session.expired":
        print("⏰ Checkout session expired")
        audit.processed = True
        audit.notes = "Session expired"
        db.session.commit()
    
    elif event["type"] == "payment_intent.payment_failed":
        print("❌ Payment failed")
        audit.processed = True
        audit.notes = "Payment failed"
        db.session.commit()
    
    else:
        # Mark other events as processed but don't do anything
        audit.processed = True
        audit.notes = f"Event type {event['type']} - no action needed"
        db.session.commit()

    return "", 200