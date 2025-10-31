from flask import Blueprint, request, current_app
from datetime import datetime, timedelta
from decimal import Decimal
import stripe

from sigma_finance.extensions import db, csrf
from sigma_finance.models import Payment, User, WebhookEvent, PaymentPlan
from sigma_finance.utils.status_updater import update_financial_status
from sigma_finance.routes.payments import archive_plan_if_completed
from sigma_finance.services.stats import invalidate_payment_cache, invalidate_user_cache, invalidate_plan_cache

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["POST"])
@csrf.exempt  # Stripe webhooks don't have CSRF tokens
def stripe_webhook():
    """
    Secure Stripe webhook handler with enhanced security features:
    - Signature verification
    - Idempotency (duplicate prevention)
    - Event ID tracking
    - Timestamp validation
    - Comprehensive error handling
    """
    current_app.logger.info("✅ Webhook received")

    payload = request.get_data(as_text=False)
    sig_header = request.headers.get("Stripe-Signature")

    # SECURITY CHECK 1: Verify Stripe signature
    webhook_secret = current_app.config.get("STRIPE_WEBHOOK_SECRET")

    if not webhook_secret:
        current_app.logger.error("❌ STRIPE_WEBHOOK_SECRET not configured!")
        return "Webhook secret not configured", 500

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            webhook_secret
        )
    except ValueError as e:
        current_app.logger.error(f"❌ Invalid payload: {e}")
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError as e:
        current_app.logger.error(f"❌ Invalid signature: {e}")
        current_app.logger.error(f"   Signature header present: {bool(sig_header)}")
        current_app.logger.error(f"   Webhook secret configured: {bool(webhook_secret)}")
        return "Invalid signature", 400

    current_app.logger.info(f"📦 Event type: {event['type']}")
    event_id = event.get('id')

    # SECURITY CHECK 2: Verify event timestamp (reject events older than 1 hour)
    event_timestamp = event.get('created')
    if event_timestamp:
        event_time = datetime.fromtimestamp(event_timestamp)
        time_diff = datetime.utcnow() - event_time
        if time_diff > timedelta(hours=1):
            current_app.logger.warning(f"⚠️ Event too old: {time_diff.total_seconds()}s")
            return "Event timestamp too old", 400

    # SECURITY CHECK 3: Check for duplicate events using event_id (idempotency)
    if event_id:
        existing_event = WebhookEvent.query.filter_by(event_id=event_id).first()

        if existing_event and existing_event.processed:
            current_app.logger.warning(f"⚠️ Duplicate webhook detected: {event_id}")
            return "Event already processed", 200  # Return 200 to prevent Stripe retries

    # Audit log for all events
    try:
        audit = WebhookEvent(
            event_id=event_id,
            event_type=event["type"],
            payload=payload.decode("utf-8"),
            received_at=datetime.utcnow(),
            processed=False
        )
        db.session.add(audit)
        db.session.commit()
        current_app.logger.info("📝 Webhook event logged")
    except Exception as e:
        current_app.logger.error(f"⚠️ Audit log error: {e}")
        db.session.rollback()
        return "Failed to log event", 500

    # Handle completed checkout session
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})
        email = session.get("customer_details", {}).get("email")
        plan_id = metadata.get("plan_id")
        amount_total = session.get("amount_total")

        # Use base_amount if available (original amount before Stripe fees)
        # Otherwise fall back to amount_total for backwards compatibility
        base_amount = metadata.get("base_amount")
        amount_to_record = Decimal(base_amount) if base_amount else (Decimal(amount_total) / 100)

        current_app.logger.info(f"📧 Email: {email}")
        current_app.logger.info(f"🧾 Metadata: {metadata}")
        current_app.logger.info(f"📌 Plan ID: {plan_id}")
        current_app.logger.info(f"💰 Amount charged: ${amount_total / 100 if amount_total else 0}")
        current_app.logger.info(f"💵 Base amount (recorded): ${amount_to_record}")

        # VALIDATION: Check required fields
        if not email:
            current_app.logger.error("❌ Missing customer email in session")
            audit.notes = "Missing customer email"
            db.session.commit()
            return "Missing customer email", 400

        if not amount_total or amount_total <= 0:
            current_app.logger.error("❌ Invalid payment amount")
            audit.notes = "Invalid amount"
            db.session.commit()
            return "Invalid amount", 400

        # Find user
        user = User.query.filter_by(email=email).first()
        if not user:
            current_app.logger.error(f"❌ No matching user found for email: {email}")
            audit.notes = f"User not found: {email}"
            db.session.commit()
            return "User not found", 404

        # SECURITY CHECK 4: Prevent duplicate payments (same user, same amount, within 5 minutes)
        recent_payment = Payment.query.filter(
            Payment.user_id == user.id,
            Payment.amount == amount_to_record,
            Payment.date >= datetime.utcnow() - timedelta(minutes=5)
        ).first()

        if recent_payment:
            current_app.logger.warning(f"⚠️ Duplicate payment detected for user {user.id}")
            audit.processed = True
            audit.notes = f"Duplicate payment prevented (existing payment ID: {recent_payment.id})"
            db.session.commit()
            return "Duplicate payment", 200

        # Create payment record
        try:
            new_payment = Payment(
                user_id=user.id,
                amount=amount_to_record,  # Record the base amount (before Stripe fees)
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
            current_app.logger.info(f"✅ Payment logged to DB: ID {new_payment.id}")

            # Invalidate caches
            invalidate_payment_cache()
            invalidate_user_cache(user.id)
            if plan_id:
                invalidate_plan_cache()

            # Update financial status
            update_financial_status(user.id)

            # Check if payment plan should be archived
            if new_payment.plan_id:
                current_app.logger.info(f"🔄 Checking if plan {new_payment.plan_id} should be archived")
                plan = PaymentPlan.query.get(new_payment.plan_id)
                if plan:
                    archive_plan_if_completed(plan, user.id, silent=True)

        except Exception as e:
            current_app.logger.error(f"❌ Payment processing error: {e}", exc_info=True)
            db.session.rollback()
            audit.notes = f"Processing error: {str(e)}"
            db.session.commit()
            return "Payment processing failed", 500

    # Handle other event types (can add more as needed)
    elif event["type"] == "checkout.session.expired":
        current_app.logger.info("⏰ Checkout session expired")
        audit.processed = True
        audit.notes = "Session expired"
        db.session.commit()

    elif event["type"] == "payment_intent.payment_failed":
        current_app.logger.warning("❌ Payment failed")
        audit.processed = True
        audit.notes = "Payment failed"
        db.session.commit()

    else:
        # Mark other events as processed but don't do anything
        current_app.logger.info(f"Event type {event['type']} - no action needed")
        audit.processed = True
        audit.notes = f"Event type {event['type']} - no action needed"
        db.session.commit()

    return "", 200