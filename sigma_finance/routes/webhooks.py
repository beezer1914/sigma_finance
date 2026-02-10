from flask import Blueprint, request, current_app
from datetime import datetime, timedelta
from decimal import Decimal
import stripe
import os
import requests

from sigma_finance.extensions import db, csrf
from sigma_finance.models import Payment, User, WebhookEvent, PaymentPlan, Donation, EmailEvent
from sigma_finance.utils.status_updater import update_financial_status
from sigma_finance.routes.payments import archive_plan_if_completed
from sigma_finance.services.stats import invalidate_payment_cache, invalidate_user_cache, invalidate_plan_cache

webhook_bp = Blueprint("webhook", __name__)


def send_discord_notification(event_type, email, category=None, reason=None):
    """Send email event notification to Discord webhook."""
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return

    # Emoji mapping for different event types
    emoji_map = {
        "delivered": "✅",
        "processed": "📤",
        "opened": "👀",
        "click": "🔗",
        "bounce": "🔴",
        "dropped": "⛔",
        "spam_report": "🚨",
        "unsubscribe": "🚫",
        "deferred": "⏳",
    }

    emoji = emoji_map.get(event_type, "📧")

    # Build the message
    message = f"{emoji} **Email {event_type.upper()}**\n"
    message += f"📬 To: `{email}`\n"
    if category:
        message += f"🏷️ Category: `{category}`\n"
    if reason:
        message += f"⚠️ Reason: {reason}\n"
    message += f"🕐 {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"

    try:
        requests.post(webhook_url, json={"content": message}, timeout=5)
    except Exception as e:
        current_app.logger.error(f"Discord notification failed: {e}")


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
        event_time = datetime.utcfromtimestamp(event_timestamp)
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

        # Note: Duplicate prevention is handled by event_id check above (SECURITY CHECK 3)
        # Each Stripe webhook event has a unique event_id, so we don't need amount+time checks

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


@webhook_bp.route("/webhook/donations", methods=["POST"])
@csrf.exempt  # Stripe webhooks don't have CSRF tokens
def stripe_donation_webhook():
    """
    Secure Stripe webhook handler for DONATIONS (separate Stripe account).
    This handles webhooks from the donation payment link.

    Security features:
    - Signature verification with donation webhook secret
    - Idempotency (duplicate prevention)
    - Event ID tracking
    - Timestamp validation
    """
    current_app.logger.info("✅ Donation webhook received")

    payload = request.get_data(as_text=False)
    sig_header = request.headers.get("Stripe-Signature")

    # SECURITY CHECK 1: Verify Stripe signature with DONATION webhook secret
    webhook_secret = current_app.config.get("DONATION_STRIPE_WEBHOOK_SECRET")

    if not webhook_secret:
        current_app.logger.error("❌ DONATION_STRIPE_WEBHOOK_SECRET not configured!")
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
        return "Invalid signature", 400

    current_app.logger.info(f"📦 Donation event type: {event['type']}")
    event_id = event.get('id')

    # SECURITY CHECK 2: Verify event timestamp (reject events older than 1 hour)
    event_timestamp = event.get('created')
    if event_timestamp:
        event_time = datetime.utcfromtimestamp(event_timestamp)
        time_diff = datetime.utcnow() - event_time
        if time_diff > timedelta(hours=1):
            current_app.logger.warning(f"⚠️ Event too old: {time_diff.total_seconds()}s")
            return "Event timestamp too old", 400

    # SECURITY CHECK 3: Check for duplicate events (idempotency)
    if event_id:
        existing_event = WebhookEvent.query.filter_by(event_id=event_id).first()

        if existing_event and existing_event.processed:
            current_app.logger.warning(f"⚠️ Duplicate donation webhook: {event_id}")
            return "Event already processed", 200

    # Audit log for all donation events
    try:
        audit = WebhookEvent(
            event_id=event_id,
            event_type=event["type"],
            payload=payload.decode("utf-8"),
            received_at=datetime.utcnow(),
            processed=False,
            source="donations"  # Mark as donation webhook
        )
        db.session.add(audit)
        db.session.commit()
        current_app.logger.info("📝 Donation webhook event logged")
    except Exception as e:
        current_app.logger.error(f"⚠️ Audit log error: {e}")
        db.session.rollback()
        return "Failed to log event", 500

    # Handle completed checkout session for donations
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_details = session.get("customer_details", {})
        donor_email = customer_details.get("email")
        donor_name = customer_details.get("name", "Anonymous")
        amount_total = session.get("amount_total")
        session_id = session.get("id")

        current_app.logger.info(f"📧 Donor email: {donor_email}")
        current_app.logger.info(f"👤 Donor name: {donor_name}")
        current_app.logger.info(f"💰 Donation amount: ${amount_total / 100 if amount_total else 0}")

        # VALIDATION: Check required fields
        if not donor_email:
            current_app.logger.error("❌ Missing donor email in session")
            audit.notes = "Missing donor email"
            db.session.commit()
            return "Missing donor email", 400

        if not amount_total or amount_total <= 0:
            current_app.logger.error("❌ Invalid donation amount")
            audit.notes = "Invalid amount"
            db.session.commit()
            return "Invalid amount", 400

        # Check if donor is a registered user (optional)
        user = User.query.filter_by(email=donor_email).first()
        user_id = user.id if user else None

        # Note: Duplicate prevention is handled by event_id check above (SECURITY CHECK 3)
        # Each Stripe webhook event has a unique event_id, so we don't need amount+time checks

        # Create donation record
        try:
            new_donation = Donation(
                donor_name=donor_name,
                donor_email=donor_email,
                amount=Decimal(amount_total) / 100,
                method="stripe",
                stripe_payment_id=session_id,
                anonymous=False,  # Can be updated manually if needed
                notes="Donation via Stripe payment link",
                user_id=user_id
            )
            db.session.add(new_donation)

            # Mark webhook as processed
            audit.processed = True
            audit.notes = f"Donation created successfully: ID {new_donation.id}"

            db.session.commit()
            current_app.logger.info(f"✅ Donation logged to DB: ID {new_donation.id}")

        except Exception as e:
            current_app.logger.error(f"❌ Donation processing error: {e}", exc_info=True)
            db.session.rollback()
            audit.notes = f"Processing error: {str(e)}"
            db.session.commit()
            return "Donation processing failed", 500

    # Handle other event types
    elif event["type"] == "checkout.session.expired":
        current_app.logger.info("⏰ Donation checkout session expired")
        audit.processed = True
        audit.notes = "Session expired"
        db.session.commit()

    else:
        current_app.logger.info(f"Event type {event['type']} - no action needed")
        audit.processed = True
        audit.notes = f"Event type {event['type']} - no action needed"
        db.session.commit()

    return "", 200


@webhook_bp.route("/webhook/sendgrid", methods=["POST"])
@csrf.exempt  # SendGrid webhooks don't have CSRF tokens
def sendgrid_webhook():
    """
    SendGrid Event Webhook handler to track email delivery and engagement.

    Security features:
    - Signature verification using SendGrid public key
    - Timestamp validation to prevent replay attacks

    Tracks events:
    - processed: Email received by SendGrid
    - delivered: Email successfully delivered
    - opened: Recipient opened the email
    - click: Recipient clicked a link
    - bounce: Email bounced
    - dropped: SendGrid dropped the email
    - spam_report: Marked as spam
    - unsubscribe: Recipient unsubscribed

    See: https://docs.sendgrid.com/for-developers/tracking-events/event
    """
    current_app.logger.info("📧 SendGrid webhook received")

    # SECURITY CHECK: Verify SendGrid signature (if configured)
    verification_key = current_app.config.get("SENDGRID_WEBHOOK_VERIFICATION_KEY")

    if verification_key:
        try:
            from sendgrid.helpers.eventwebhook import EventWebhook, EventWebhookHeader

            payload = request.get_data(as_text=True)
            signature = request.headers.get(EventWebhookHeader.SIGNATURE.value)
            timestamp = request.headers.get(EventWebhookHeader.TIMESTAMP.value)

            if not signature or not timestamp:
                current_app.logger.error("❌ Missing signature or timestamp headers")
                return "Missing security headers", 401

            event_webhook = EventWebhook()
            ec_public_key = event_webhook.convert_public_key_to_ecdsa(verification_key)

            verified = event_webhook.verify_signature(
                ec_public_key,
                payload,
                signature,
                timestamp
            )

            if not verified:
                current_app.logger.error("❌ Invalid SendGrid signature")
                return "Invalid signature", 403

            current_app.logger.info("✅ SendGrid signature verified")

        except Exception as e:
            current_app.logger.error(f"❌ Signature verification error: {e}")
            return "Signature verification failed", 403
    else:
        current_app.logger.warning("⚠️ SendGrid webhook verification key not configured - running without signature verification")

    try:
        events = request.get_json()

        if not events:
            current_app.logger.error("❌ No events in SendGrid webhook")
            return "No events", 400

        # SendGrid sends events as an array
        if not isinstance(events, list):
            events = [events]

        processed_count = 0

        for event in events:
            try:
                # Extract event data
                event_id = event.get('sg_event_id')
                event_type = event.get('event')
                email = event.get('email')
                timestamp = event.get('timestamp')

                # Get additional fields
                subject = event.get('subject', '')
                category = event.get('category', [''])[0] if event.get('category') else None
                smtp_id = event.get('smtp-id')
                response = event.get('response')
                reason = event.get('reason')
                url = event.get('url')
                ip = event.get('ip')
                user_agent = event.get('useragent')

                # Validate required fields
                if not event_id or not event_type or not email:
                    current_app.logger.warning(f"⚠️ Missing required fields in event: {event}")
                    continue

                # Check for duplicate event
                existing = EmailEvent.query.filter_by(event_id=event_id).first()
                if existing:
                    current_app.logger.info(f"⏭️ Duplicate email event: {event_id}")
                    continue

                # Try to link to user by email
                user = User.query.filter_by(email=email).first()
                user_id = user.id if user else None

                # Convert timestamp to datetime
                event_datetime = datetime.utcfromtimestamp(timestamp) if timestamp else datetime.utcnow()

                # Create email event record
                email_event = EmailEvent(
                    event_id=event_id,
                    email=email,
                    event_type=event_type,
                    timestamp=event_datetime,
                    subject=subject,
                    category=category,
                    user_id=user_id,
                    smtp_id=smtp_id,
                    response=response,
                    reason=reason,
                    url=url,
                    ip=ip,
                    user_agent=user_agent
                )

                db.session.add(email_event)
                processed_count += 1

                current_app.logger.info(
                    f"✅ Email event: {event_type} | {email} | {category or 'no category'}"
                )

                # Send Discord notification for notable events
                notable_events = ["delivered", "bounce", "dropped", "spam_report", "opened", "click"]
                if event_type in notable_events:
                    send_discord_notification(event_type, email, category, reason)

            except Exception as e:
                current_app.logger.error(f"❌ Error processing event: {e}", exc_info=True)
                continue

        # Commit all events
        db.session.commit()
        current_app.logger.info(f"📧 Processed {processed_count} SendGrid events")

        return "", 200

    except Exception as e:
        current_app.logger.error(f"❌ SendGrid webhook error: {e}", exc_info=True)
        db.session.rollback()
        return "Internal server error", 500