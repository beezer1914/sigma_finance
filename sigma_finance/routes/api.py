from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash
from sigma_finance.models import Payment, PaymentPlan, User, InviteCode
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from sigma_finance.extensions import db, limiter

api_bp = Blueprint("api", __name__, url_prefix="/api")


# ============================================================================
# Health Check Endpoint (No Auth Required)
# ============================================================================

@api_bp.route("/health", methods=["GET"])
@limiter.exempt  # Exempt health check from rate limiting
def health_check():
    """
    Health check endpoint for monitoring services.
    Checks database connectivity and returns service status.

    Returns:
        JSON with status, database connectivity, and timestamp
    """
    import time
    from datetime import datetime

    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "checks": {}
    }

    # Check database connectivity
    try:
        start = time.time()
        db.session.execute(db.text("SELECT 1"))
        db_latency = round((time.time() - start) * 1000, 2)  # ms
        health_status["checks"]["database"] = {
            "status": "up",
            "latency_ms": db_latency
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "down",
            "error": str(e)
        }
        return jsonify(health_status), 503

    return jsonify(health_status), 200


# ============================================================================
# Public Endpoints (No Auth Required)
# ============================================================================

@api_bp.route("/donate/link", methods=["GET"])
def get_donation_link():
    """
    Get the public Stripe donation link.
    No authentication required.
    """
    from flask import current_app
    donation_link = current_app.config.get("DONATION_STRIPE_LINK", "")
    return jsonify({
        "success": True,
        "donation_link": donation_link
    }), 200


# ============================================================================
# Authentication Endpoints
# ============================================================================

@api_bp.route("/auth/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    """
    Authenticate a user and create a session.

    Request JSON:
        {
            "email": "user@example.com",
            "password": "password123"
        }

    Returns:
        JSON with user data and success status
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        login_user(user, remember=True)
        return jsonify({
            "success": True,
            "message": "Logged in successfully",
            "user": user.to_dict()
        }), 200

    return jsonify({"error": "Invalid credentials"}), 401


@api_bp.route("/auth/register", methods=["POST"])
@limiter.limit("3 per hour")
def register():
    """
    Register a new user with an invite code.

    Request JSON:
        {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123",
            "invite_code": "ABC123"
        }

    Returns:
        JSON with success status and message
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    invite_code = data.get("invite_code")

    # Validation
    if not all([name, email, password, invite_code]):
        return jsonify({"error": "All fields are required"}), 400

    # Check if email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 400

    # Validate invite code
    invite = InviteCode.query.filter_by(code=invite_code.strip()).first()

    if not invite:
        return jsonify({"error": "Invalid invite code"}), 400

    if invite.used:
        return jsonify({"error": "Invite code already used"}), 400

    if invite.expires_at and invite.expires_at < datetime.utcnow():
        return jsonify({"error": "Invite code has expired"}), 400

    # Create new user
    role = invite.role if invite else "member"

    new_user = User(
        name=name,
        email=email,
        role=role,
        password_hash=generate_password_hash(password),
        financial_status="not financial",
        active=True
    )

    try:
        db.session.add(new_user)
        db.session.flush()

        # Mark invite as used
        invite.used = True
        invite.used_by = new_user.id
        invite.used_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Account created successfully"
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred during registration"}), 500


@api_bp.route("/auth/logout", methods=["POST"])
@login_required
def logout():
    """
    Log out the current user.

    Returns:
        JSON with success status
    """
    logout_user()
    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    }), 200


@api_bp.route("/auth/user", methods=["GET"])
@login_required
def get_current_user():
    """
    Get the currently authenticated user.

    Returns:
        JSON with user data
    """
    return jsonify({
        "success": True,
        "user": current_user.to_dict()
    }), 200


@api_bp.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    """
    Update current user's profile.

    Request JSON:
        {
            "name": "New Name",
            "email": "new@email.com",
            "current_password": "required if changing password",
            "new_password": "optional new password"
        }

    Returns:
        JSON with updated user data
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get("name")
    email = data.get("email")
    current_password = data.get("current_password")
    new_password = data.get("new_password")

    # Update name if provided
    if name and name.strip():
        current_user.name = name.strip()

    # Update email if provided and different
    if email and email.strip() and email != current_user.email:
        # Check if email is already taken
        existing = User.query.filter_by(email=email).first()
        if existing and existing.id != current_user.id:
            return jsonify({"error": "Email already in use"}), 400
        current_user.email = email.strip()

    # Update password if provided
    if new_password:
        if not current_password:
            return jsonify({"error": "Current password required to change password"}), 400
        if not current_user.check_password(current_password):
            return jsonify({"error": "Current password is incorrect"}), 400
        if len(new_password) < 6:
            return jsonify({"error": "New password must be at least 6 characters"}), 400
        current_user.password_hash = generate_password_hash(new_password)

    try:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Profile updated successfully",
            "user": current_user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update profile"}), 500


# ============================================================================
# Dashboard Endpoints
# ============================================================================

@api_bp.route("/dashboard")
@login_required
def dashboard_data():
    """
    Provides the data for the user dashboard.
    """
    # Fetch all payments for the current user
    payments_query = (
        Payment.query
        .options(joinedload(Payment.plan))  # Prevent N+1 query for plan
        .filter_by(user_id=current_user.id)
        .order_by(Payment.date.desc())
        .limit(20)  # Only show recent payments
        .all()
    )

    payments = [p.to_dict() for p in payments_query]

    # Fetch active payment plan, if any
    plan_query = (
        PaymentPlan.query
        .filter_by(user_id=current_user.id, status="Active")
        .first()
    )

    plan = plan_query.to_dict() if plan_query else None

    # Initialize progress metrics
    remaining_balance = None
    percent_paid = None

    if plan and plan_query:
        # OPTIMIZATION 3: Use aggregate query instead of loading all payments
        # This is MUCH faster than: sum(p.amount for p in plan.payments)
        paid = (
            db.session.query(func.sum(Payment.amount))
            .filter_by(plan_id=plan_query.id)
            .scalar() or 0
        )
        
        # Calculate remaining balance and progress percentage
        total = float(plan_query.total_amount)
        paid_amount = float(paid)
        
        remaining_balance = round(total - paid_amount, 2)
        percent_paid = round((paid_amount / total) * 100, 0) if total > 0 else 0

    return jsonify(
        name=current_user.name,
        payments=payments,
        plan=plan,
        remaining_balance=remaining_balance,
        percent_paid=percent_paid,
        initiation_date=current_user.initiation_date.strftime('%Y-%m-%d') if current_user.initiation_date else None,
        status=current_user.status
    )


# ============================================================================
# Payment Endpoints
# ============================================================================

@api_bp.route("/payments", methods=["GET"])
@login_required
def get_payments():
    """
    Get user's payment history with optional pagination.

    Query Parameters:
        limit (int): Number of payments to return (default: 50, max: 100)
        offset (int): Number of payments to skip (default: 0)

    Returns:
        JSON with payments list and pagination info
    """
    limit = min(int(request.args.get('limit', 50)), 100)
    offset = int(request.args.get('offset', 0))

    query = (
        Payment.query
        .filter_by(user_id=current_user.id)
        .order_by(Payment.date.desc())
    )

    total = query.count()
    payments = query.limit(limit).offset(offset).all()

    return jsonify({
        "success": True,
        "payments": [p.to_dict() for p in payments],
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total
        }
    }), 200


@api_bp.route("/payments/create-checkout", methods=["POST"])
@login_required
@limiter.limit("5 per minute")
def create_checkout_session():
    """
    Create a Stripe checkout session for payment.

    Request JSON:
        {
            "amount": 100.00,
            "payment_type": "one-time" | "installment",
            "notes": "Optional notes"
        }

    Returns:
        JSON with Stripe checkout session URL
    """
    import stripe
    from flask import current_app
    from decimal import Decimal

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    amount = data.get("amount")
    payment_type = data.get("payment_type", "one-time")
    notes = data.get("notes", "")

    if not amount:
        return jsonify({"error": "Amount is required"}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"error": "Amount must be greater than 0"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid amount"}), 400

    # Calculate total including Stripe processing fees
    def calculate_total_with_fees(amount):
        amount_decimal = Decimal(str(amount))
        fee_percentage = Decimal("0.029")  # 2.9%
        fixed_fee = Decimal("0.30")
        total_with_fees = (amount_decimal + fixed_fee) / (Decimal("1") - fee_percentage)
        return total_with_fees.quantize(Decimal("0.01"))

    total_with_fees = calculate_total_with_fees(amount)

    # Get active plan if exists
    plan = PaymentPlan.query.filter_by(user_id=current_user.id, status="Active").first()

    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]

    try:
        # Get frontend URL from config (Vite dev server locally, same domain in prod)
        frontend_url = current_app.config.get("FRONTEND_URL", "http://localhost:5173")

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "Installment Payment" if payment_type == "installment" else "One-Time Dues"
                    },
                    "unit_amount": int(total_with_fees * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            customer_email=current_user.email,  # Pre-fill email for webhook matching
            success_url=frontend_url.rstrip('/') + "/payment/success",
            cancel_url=frontend_url.rstrip('/') + "/payment/cancel",
            metadata={
                "user_id": current_user.id,
                "payment_type": payment_type,
                "notes": notes,
                "plan_id": str(plan.id) if plan else "",
                "base_amount": str(amount)
            }
        )

        return jsonify({
            "success": True,
            "checkout_url": session.url,
            "session_id": session.id
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/payment-plans", methods=["POST"])
@login_required
def create_payment_plan():
    """
    Enroll in a new payment plan.

    Request JSON:
        {
            "frequency": "weekly" | "monthly" | "quarterly",
            "start_date": "2025-01-01",
            "amount": 500.00
        }

    Returns:
        JSON with created payment plan
    """
    from dateutil.relativedelta import relativedelta
    from sigma_finance.services.stats import invalidate_plan_cache

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    frequency = data.get("frequency")
    start_date_str = data.get("start_date")
    total_amount = data.get("amount")

    # Validation
    if not all([frequency, start_date_str, total_amount]):
        return jsonify({"error": "All fields are required"}), 400

    if frequency not in ["weekly", "monthly", "quarterly"]:
        return jsonify({"error": "Invalid frequency"}), 400

    # Check if user already has an active plan
    existing_plan = PaymentPlan.query.filter_by(
        user_id=current_user.id,
        status="Active"
    ).first()

    if existing_plan:
        return jsonify({"error": "You already have an active payment plan"}), 400

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        total_amount = float(total_amount)

        if total_amount <= 0:
            return jsonify({"error": "Amount must be greater than 0"}), 400

    except (ValueError, TypeError):
        return jsonify({"error": "Invalid date or amount"}), 400

    # Calculate plan details
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

    # Create payment plan
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

    try:
        db.session.add(plan)
        db.session.commit()
        invalidate_plan_cache()

        return jsonify({
            "success": True,
            "message": "Payment plan created successfully",
            "plan": plan.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create payment plan"}), 500


# ============================================================================
# Treasurer Endpoints (Role-Based Access)
# ============================================================================

def has_full_access():
    """Check if current user has full treasurer access"""
    return current_user.role in ['admin', 'treasurer', 'president', 'vice_1']

def has_report_access():
    """Check if current user can view reports and create invites"""
    return current_user.role in ['admin', 'treasurer', 'president', 'vice_1', 'vice_2', 'secretary']

# Legacy alias for backwards compatibility
def is_treasurer():
    """Check if current user is treasurer or admin (legacy)"""
    return has_full_access()


@api_bp.route("/treasurer/stats", methods=["GET"])
@login_required
def get_treasurer_stats():
    """
    Get treasurer dashboard statistics.
    Requires treasurer or admin role.
    """
    if not is_treasurer():
        return jsonify({"error": "Access denied"}), 403

    from sigma_finance.services.stats import (
        get_total_payments,
        get_users_with_active_plans,
        get_unpaid_members,
        get_payment_summary_by_type,
        get_payment_method_stats,
    )

    # Get all stats
    total_collected = get_total_payments()
    active_plan_users = get_users_with_active_plans()
    unpaid_members = get_unpaid_members()
    payment_types = get_payment_summary_by_type()
    payment_methods = get_payment_method_stats()
    total_members = User.query.filter_by(active=True).count()

    return jsonify({
        "success": True,
        "stats": {
            "total_collected": total_collected,
            "active_plans": len(active_plan_users),
            "unpaid_members": len(unpaid_members),
            "total_members": total_members,
            "payment_types": payment_types,
            "payment_methods": payment_methods,
        }
    }), 200


@api_bp.route("/treasurer/members", methods=["GET"])
@login_required
def get_all_members():
    """
    Get all members with optional filtering.
    Requires treasurer or admin role.

    Query Parameters:
        search (str): Search by name or email
        status (str): Filter by financial_status (financial, not_financial, neophyte)
        has_plan (str): Filter by plan status (active, none)
        limit (int): Number of results (default: 50, max: 100)
        offset (int): Pagination offset (default: 0)
    """
    if not is_treasurer():
        return jsonify({"error": "Access denied"}), 403

    from sigma_finance.services.stats import get_user_outstanding_balance

    # Get query parameters
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', 'all')
    plan_filter = request.args.get('has_plan', 'all')
    limit = min(int(request.args.get('limit', 50)), 100)
    offset = int(request.args.get('offset', 0))

    # Build query
    query = User.query.filter_by(active=True)

    # Search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                User.name.ilike(search_term),
                User.email.ilike(search_term)
            )
        )

    # Financial status filter
    if status_filter != 'all':
        query = query.filter(User.financial_status == status_filter)

    # Payment plan filter
    if plan_filter == 'active':
        query = query.join(PaymentPlan).filter(PaymentPlan.status == "Active")
    elif plan_filter == 'none':
        # Users without active plans
        subquery = db.session.query(PaymentPlan.user_id).filter(
            PaymentPlan.status == "Active"
        ).subquery()
        query = query.filter(~User.id.in_(subquery))

    # Get total count before pagination
    total = query.count()

    # Apply pagination and ordering
    members = query.order_by(User.name).limit(limit).offset(offset).all()

    # Build response with additional data
    members_data = []
    for member in members:
        # Get active plan if exists
        active_plan = PaymentPlan.query.filter_by(
            user_id=member.id, status="Active"
        ).first()

        # Calculate total paid
        total_paid = db.session.query(func.sum(Payment.amount)).filter(
            Payment.user_id == member.id
        ).scalar() or 0

        members_data.append({
            **member.to_dict(),
            'total_paid': float(total_paid),
            'has_active_plan': active_plan is not None,
            'plan_balance': get_user_outstanding_balance(member.id) if active_plan else 0,
            'is_neophyte': member.is_neophyte(),
        })

    return jsonify({
        "success": True,
        "members": members_data,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total
        }
    }), 200


@api_bp.route("/treasurer/members/<int:user_id>", methods=["GET"])
@login_required
def get_member_detail(user_id):
    """
    Get detailed information about a specific member.
    Requires treasurer or admin role.
    """
    if not is_treasurer():
        return jsonify({"error": "Access denied"}), 403

    from sigma_finance.services.stats import get_member_financial_summary

    member = User.query.get(user_id)
    if not member:
        return jsonify({"error": "Member not found"}), 404

    # Get financial summary
    summary = get_member_financial_summary(user_id)

    # Get payment history
    payments = Payment.query.filter_by(user_id=user_id).order_by(
        Payment.date.desc()
    ).limit(20).all()

    # Get active plan details
    active_plan = PaymentPlan.query.filter_by(
        user_id=user_id, status="Active"
    ).first()

    return jsonify({
        "success": True,
        "member": {
            **member.to_dict(),
            'is_neophyte': member.is_neophyte(),
        },
        "financial_summary": summary,
        "payments": [p.to_dict() for p in payments],
        "active_plan": active_plan.to_dict() if active_plan else None,
    }), 200


@api_bp.route("/treasurer/reports/summary", methods=["GET"])
@login_required
def get_reports_summary():
    """
    Get financial reports summary.
    Requires report access (vice_2, secretary, or higher).
    """
    if not has_report_access():
        return jsonify({"error": "Access denied"}), 403

    from sigma_finance.services.stats import (
        get_total_payments,
        get_payment_summary_by_type,
        get_payment_method_stats,
        get_payment_trends,
    )

    return jsonify({
        "success": True,
        "summary": {
            "total_collected": get_total_payments(),
            "by_type": get_payment_summary_by_type(),
            "by_method": get_payment_method_stats(),
            "trends": get_payment_trends(6),
        }
    }), 200


@api_bp.route("/treasurer/payments", methods=["GET"])
@login_required
def get_all_payments():
    """
    Get all payments (for treasurer view).
    Requires treasurer or admin role.

    Query Parameters:
        limit (int): Number of results (default: 50, max: 100)
        offset (int): Pagination offset (default: 0)
        user_id (int): Filter by user
        payment_type (str): Filter by payment type
        method (str): Filter by payment method
    """
    if not is_treasurer():
        return jsonify({"error": "Access denied"}), 403

    from sqlalchemy.orm import joinedload

    # Get query parameters
    limit = min(int(request.args.get('limit', 50)), 100)
    offset = int(request.args.get('offset', 0))
    user_id = request.args.get('user_id', type=int)
    payment_type = request.args.get('payment_type')
    method = request.args.get('method')

    # Build query with eager loading
    query = Payment.query.options(joinedload(Payment.user))

    # Apply filters
    if user_id:
        query = query.filter(Payment.user_id == user_id)
    if payment_type:
        query = query.filter(Payment.payment_type == payment_type)
    if method:
        query = query.filter(Payment.method == method)

    # Get total count
    total = query.count()

    # Apply pagination
    payments = query.order_by(Payment.date.desc()).limit(limit).offset(offset).all()

    # Build response
    payments_data = []
    for payment in payments:
        data = payment.to_dict()
        data['user_name'] = payment.user.name if payment.user else 'Unknown'
        data['user_email'] = payment.user.email if payment.user else 'Unknown'
        payments_data.append(data)

    return jsonify({
        "success": True,
        "payments": payments_data,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total
        }
    }), 200


# ============================================================================
# Donations API (Treasurer/Admin Only)
# ============================================================================

@api_bp.route("/donations", methods=["GET"])
@login_required
def get_donations():
    """
    Get all donations with pagination and filtering.
    Requires treasurer or admin role.
    """
    if not is_treasurer():
        return jsonify({"error": "Access denied"}), 403

    from sigma_finance.models import Donation

    # Get query parameters
    limit = min(int(request.args.get('limit', 50)), 100)
    offset = int(request.args.get('offset', 0))
    method = request.args.get('method')
    anonymous = request.args.get('anonymous')

    # Build query
    query = Donation.query

    # Apply filters
    if method and method != 'all':
        query = query.filter(Donation.method == method)
    if anonymous == 'true':
        query = query.filter(Donation.anonymous == True)
    elif anonymous == 'false':
        query = query.filter(Donation.anonymous == False)

    # Get total count
    total = query.count()

    # Apply pagination
    donations = query.order_by(Donation.date.desc()).limit(limit).offset(offset).all()

    # Build response
    donations_data = []
    for donation in donations:
        donations_data.append({
            'id': donation.id,
            'donor_name': donation.donor_name if not donation.anonymous else 'Anonymous',
            'donor_email': donation.donor_email if not donation.anonymous else '---',
            'amount': float(donation.amount),
            'date': donation.date.strftime('%Y-%m-%d') if donation.date else None,
            'method': donation.method,
            'anonymous': donation.anonymous,
            'notes': donation.notes,
            'user_id': donation.user_id,
        })

    return jsonify({
        "success": True,
        "donations": donations_data,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total
        }
    }), 200


@api_bp.route("/donations/summary", methods=["GET"])
@login_required
def get_donations_summary():
    """
    Get donations summary statistics.
    Requires treasurer or admin role.
    """
    if not is_treasurer():
        return jsonify({"error": "Access denied"}), 403

    from sigma_finance.models import Donation
    from flask import current_app

    # Total donations
    total_donated = db.session.query(func.sum(Donation.amount)).scalar() or 0
    donation_count = Donation.query.count()

    # Anonymous count
    anonymous_count = Donation.query.filter_by(anonymous=True).count()

    # By method - include both count and total for each method
    methods = ['stripe', 'cash', 'check', 'other']
    by_method = {}
    for method in methods:
        if method == 'other':
            method_donations = Donation.query.filter(
                Donation.method.notin_(['stripe', 'cash', 'check'])
            )
        else:
            method_donations = Donation.query.filter_by(method=method)

        method_count = method_donations.count()
        method_total = db.session.query(func.sum(Donation.amount)).filter(
            Donation.method == method if method != 'other'
            else Donation.method.notin_(['stripe', 'cash', 'check'])
        ).scalar() or 0

        if method_count > 0:
            by_method[method] = {
                'count': method_count,
                'total': float(method_total)
            }

    # Monthly trends (last 6 months)
    from dateutil.relativedelta import relativedelta
    end_date = datetime.utcnow()
    start_date = end_date - relativedelta(months=6)

    db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
    is_sqlite = 'sqlite' in db_url.lower()

    if is_sqlite:
        month_expr = func.strftime('%Y-%m', Donation.date)
        results = (
            db.session.query(
                month_expr.label('month'),
                func.sum(Donation.amount).label('total'),
                func.count(Donation.id).label('count')
            )
            .filter(Donation.date >= start_date)
            .group_by(month_expr)
            .order_by(month_expr)
            .all()
        )
        monthly_trends = [{'month': r.month, 'total': float(r.total), 'count': r.count} for r in results]
    else:
        results = (
            db.session.query(
                func.date_trunc('month', Donation.date).label('month'),
                func.sum(Donation.amount).label('total'),
                func.count(Donation.id).label('count')
            )
            .filter(Donation.date >= start_date)
            .group_by(func.date_trunc('month', Donation.date))
            .order_by(func.date_trunc('month', Donation.date))
            .all()
        )
        monthly_trends = [{'month': r.month.strftime('%Y-%m'), 'total': float(r.total), 'count': r.count} for r in results]

    return jsonify({
        "success": True,
        "summary": {
            "total_donated": float(total_donated),
            "donation_count": donation_count,
            "anonymous_count": anonymous_count,
            "by_method": by_method,
            "monthly_trends": monthly_trends,
        }
    }), 200


@api_bp.route("/donations", methods=["POST"])
@login_required
@limiter.limit("10 per minute")
def create_donation():
    """
    Create a manual donation entry.
    Requires treasurer or admin role.
    """
    if not is_treasurer():
        return jsonify({"error": "Access denied"}), 403

    from sigma_finance.models import Donation

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    donor_name = data.get('donor_name')
    donor_email = data.get('donor_email')
    amount = data.get('amount')
    method = data.get('method', 'other')
    anonymous = data.get('anonymous', False)
    notes = data.get('notes', '')

    # Validation
    if not donor_name or not donor_email or not amount:
        return jsonify({"error": "Donor name, email, and amount are required"}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"error": "Amount must be greater than 0"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid amount"}), 400

    # Check if donor is a registered user
    user = User.query.filter_by(email=donor_email).first()

    donation = Donation(
        donor_name=donor_name,
        donor_email=donor_email,
        amount=amount,
        method=method,
        anonymous=anonymous,
        notes=notes,
        user_id=user.id if user else None
    )

    try:
        db.session.add(donation)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Donation recorded successfully",
            "donation": {
                'id': donation.id,
                'donor_name': donation.donor_name,
                'amount': float(donation.amount),
                'method': donation.method,
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to record donation"}), 500


# ============================================================================
# Invite Code Endpoints (Treasurer Only)
# ============================================================================

@api_bp.route("/invites", methods=["GET"])
@login_required
def get_invites():
    """
    Get all invite codes with pagination.
    Requires report access (vice_2, secretary, or higher).
    """
    if not has_report_access():
        return jsonify({"error": "Access denied"}), 403

    from sigma_finance.models import InviteCode

    # Pagination
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)

    # Filter by status
    status = request.args.get('status')  # 'used', 'unused', 'expired'

    query = InviteCode.query

    if status == 'used':
        query = query.filter_by(used=True)
    elif status == 'unused':
        query = query.filter_by(used=False).filter(
            (InviteCode.expires_at == None) | (InviteCode.expires_at > datetime.utcnow())
        )
    elif status == 'expired':
        query = query.filter_by(used=False).filter(
            InviteCode.expires_at <= datetime.utcnow()
        )

    total = query.count()
    invites = query.order_by(InviteCode.created_at.desc()).offset(offset).limit(limit).all()

    return jsonify({
        "success": True,
        "invites": [{
            'id': inv.id,
            'code': inv.code,
            'role': inv.role,
            'used': inv.used,
            'used_by': inv.redeemer.name if inv.redeemer else None,
            'used_at': inv.used_at.isoformat() if inv.used_at else None,
            'created_by': inv.issuer.name if inv.issuer else None,
            'expires_at': inv.expires_at.isoformat() if inv.expires_at else None,
            'created_at': inv.created_at.isoformat() if inv.created_at else None,
            'is_expired': inv.expires_at and inv.expires_at < datetime.utcnow() if not inv.used else False,
        } for inv in invites],
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total
        }
    }), 200


@api_bp.route("/invites/stats", methods=["GET"])
@login_required
def get_invite_stats():
    """
    Get invite code statistics.
    Requires report access (vice_2, secretary, or higher).
    """
    if not has_report_access():
        return jsonify({"error": "Access denied"}), 403

    from sigma_finance.models import InviteCode

    total = InviteCode.query.count()
    used = InviteCode.query.filter_by(used=True).count()
    unused = InviteCode.query.filter_by(used=False).filter(
        (InviteCode.expires_at == None) | (InviteCode.expires_at > datetime.utcnow())
    ).count()
    expired = InviteCode.query.filter_by(used=False).filter(
        InviteCode.expires_at <= datetime.utcnow()
    ).count()

    return jsonify({
        "success": True,
        "stats": {
            "total": total,
            "used": used,
            "unused": unused,
            "expired": expired,
        }
    }), 200


@api_bp.route("/invites", methods=["POST"])
@login_required
@limiter.limit("10 per minute")
def create_invite():
    """
    Create a new invite code and optionally send it via email.
    Requires report access (vice_2, secretary, or higher).
    """
    if not has_report_access():
        return jsonify({"error": "Access denied"}), 403

    from sigma_finance.models import InviteCode
    from sigma_finance.utils.generate_invite import generate_invite_code
    from sigma_finance.utils.send_invite_email import send_email
    from flask import render_template, url_for

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    email = data.get('email')
    role = data.get('role', 'member')
    expires_in_days = data.get('expires_in_days', 7)

    # Validation
    valid_roles = ['member', 'treasurer', 'admin', 'president', 'vice_1', 'vice_2', 'secretary']
    if role not in valid_roles:
        return jsonify({"error": "Invalid role"}), 400

    try:
        expires_in_days = int(expires_in_days)
        if expires_in_days < 1 or expires_in_days > 90:
            return jsonify({"error": "Expiration must be between 1 and 90 days"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid expiration days"}), 400

    # Generate invite code
    code, expires_at, role = generate_invite_code(role=role, expires_in_days=expires_in_days)

    invite = InviteCode(
        code=code,
        role=role,
        expires_at=expires_at,
        created_by=current_user.id
    )

    try:
        db.session.add(invite)
        db.session.commit()

        email_sent = False
        if email:
            # Send email with invite code
            signup_url = url_for("auth.register", _external=True)
            context = {
                "code": code,
                "expires_at": expires_at,
                "signup_url": signup_url
            }

            plain_text = render_template("invite/email_invite.txt", **context)
            html_content = render_template("invite/email_invite.html", **context)

            result = send_email(
                subject="Your Sigma Finance Invite Code",
                to_email=email,
                plain_text=plain_text,
                html_content=html_content
            )
            email_sent = result is not None

        return jsonify({
            "success": True,
            "message": f"Invite code created{' and sent to ' + email if email_sent else ''}",
            "invite": {
                'id': invite.id,
                'code': invite.code,
                'role': invite.role,
                'expires_at': invite.expires_at.isoformat() if invite.expires_at else None,
            },
            "email_sent": email_sent
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create invite code"}), 500


@api_bp.route("/invites/<int:invite_id>", methods=["DELETE"])
@login_required
def delete_invite(invite_id):
    """
    Delete an unused invite code.
    Requires treasurer or admin role.
    """
    if not is_treasurer():
        return jsonify({"error": "Access denied"}), 403

    from sigma_finance.models import InviteCode

    invite = InviteCode.query.get(invite_id)
    if not invite:
        return jsonify({"error": "Invite code not found"}), 404

    if invite.used:
        return jsonify({"error": "Cannot delete a used invite code"}), 400

    try:
        db.session.delete(invite)
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Invite code deleted"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete invite code"}), 500
