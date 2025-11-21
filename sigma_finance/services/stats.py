# sigma_finance/services/stats.py - WITH CACHING

from sigma_finance.extensions import db, cache  # Add cache import
from sigma_finance.models import User, Payment, PaymentPlan
from sqlalchemy import func, and_, or_
from datetime import datetime

# 🧮 Total amount paid by all users - CACHED
@cache.memoize(timeout=300)  # Cache for 5 minutes
def get_total_payments():
    """
    Single aggregate query - MUCH faster than loading all payments
    """
    result = db.session.query(func.sum(Payment.amount)).scalar()
    return float(result or 0)


# 👥 Users with active payment plans - CACHED
@cache.memoize(timeout=300)
def get_users_with_active_plans():
    """
    Use a join instead of loading all plans then filtering
    """
    return (
        db.session.query(User)
        .join(PaymentPlan, PaymentPlan.user_id == User.id)
        .filter(PaymentPlan.status.ilike("active"))
        .distinct()  # Prevent duplicate users if they have multiple plans
        .all()
    )


# 📅 Payments made this month - CACHED
@cache.memoize(timeout=600)  # Cache for 10 minutes
def get_monthly_payments():
    """
    Filter at database level, not in Python
    """
    now = datetime.utcnow()
    return (
        db.session.query(Payment)
        .filter(
            func.extract("year", Payment.date) == now.year,
            func.extract("month", Payment.date) == now.month
        )
        .all()
    )


# 🧾 Total paid by a specific user - CACHED
@cache.memoize(timeout=300)
def get_user_total_paid(user_id):
    """
    Single aggregate query instead of loading all payments
    """
    result = (
        db.session.query(func.sum(Payment.amount))
        .filter(Payment.user_id == user_id)
        .scalar()
    )
    return float(result or 0)


# 📉 Outstanding balance for a user's active plan - CACHED
@cache.memoize(timeout=180)  # Cache for 3 minutes (changes more frequently)
def get_user_outstanding_balance(user_id):
    """
    Combined query to get plan and payment sum in one go
    """
    # Get active plan
    plan = (
        db.session.query(PaymentPlan)
        .filter(
            PaymentPlan.user_id == user_id,
            PaymentPlan.status == "active"
        )
        .first()
    )
    
    if not plan:
        return 0

    # Get sum of payments for this plan
    paid = (
        db.session.query(func.sum(Payment.amount))
        .filter(
            Payment.user_id == user_id,
            Payment.plan_id == plan.id
        )
        .scalar() or 0
    )

    return float(plan.total_amount) - float(paid)


# 📋 Summary of payments by type - CACHED
@cache.memoize(timeout=300)
def get_payment_summary_by_type():
    """
    Use COUNT instead of loading all records
    """
    summary = {
        "one_time": db.session.query(func.count(Payment.id))
            .filter_by(payment_type="one-time")
            .scalar() or 0,
        "installment": db.session.query(func.count(Payment.id))
            .filter_by(payment_type="installment")
            .scalar() or 0
    }
    return summary


# 🧮 Count of unpaid members - CACHED
DUES_AMOUNT = 200  # Move to config later

@cache.memoize(timeout=300)
def get_unpaid_members():
    """
    Ultra-optimized query using subqueries
    Only counts payments from current dues year (Oct 1 - Sept 30)
    """
    from datetime import datetime
    
    # Determine current dues year start date (October 1)
    today = datetime.utcnow()
    if today.month >= 10:  # October or later
        dues_year_start = datetime(today.year, 10, 1)
    else:  # Before October
        dues_year_start = datetime(today.year - 1, 10, 1)
    
    # Subquery: Users who have paid $200 or more this dues year
    paid_users_subquery = (
        db.session.query(Payment.user_id)
        .filter(Payment.date >= dues_year_start)  # Only count from Oct 1 onwards
        .group_by(Payment.user_id)
        .having(func.sum(Payment.amount) >= DUES_AMOUNT)
        .subquery()
    )
    
    # Subquery: Users with active payment plans
    active_plan_users_subquery = (
        db.session.query(PaymentPlan.user_id)
        .filter(PaymentPlan.status.ilike("active"))
        .subquery()
    )
    
    # Main query: Find users NOT in either subquery
    all_unpaid = (
        db.session.query(User)
        .filter(
            User.active == True,
            ~User.id.in_(paid_users_subquery),
            ~User.id.in_(active_plan_users_subquery)
        )
        .order_by(User.name)
        .all()
    )
    
    # Filter out neophytes (they are exempt from dues)
    unpaid_members = [
        user for user in all_unpaid 
        if not (hasattr(user, 'is_neophyte') and user.is_neophyte())
    ]
    
    return unpaid_members


# 📊 Payment method breakdown - CACHED
@cache.memoize(timeout=300)
def get_payment_method_stats():
    """
    Use COUNT instead of loading records
    """
    stats = {
        "stripe": db.session.query(func.count(Payment.id))
            .filter_by(method="stripe")
            .scalar() or 0,
        "cash": db.session.query(func.count(Payment.id))
            .filter_by(method="cash")
            .scalar() or 0,
        "other": db.session.query(func.count(Payment.id))
            .filter(Payment.method.notin_(["stripe", "cash"]))
            .scalar() or 0
    }
    
    return stats


# 📈 Get payment trends - CACHED
@cache.memoize(timeout=3600)  # Cache for 1 hour (doesn't change often)
def get_payment_trends(months=6):
    """
    Get monthly payment totals for the last N months
    Useful for charts/graphs
    Works with both PostgreSQL and SQLite
    """
    from dateutil.relativedelta import relativedelta
    from flask import current_app

    end_date = datetime.utcnow()
    start_date = end_date - relativedelta(months=months)

    # Check if we're using SQLite or PostgreSQL
    db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
    is_sqlite = 'sqlite' in db_url.lower()

    if is_sqlite:
        # SQLite: use strftime for date grouping
        month_expr = func.strftime('%Y-%m', Payment.date)
        results = (
            db.session.query(
                month_expr.label('month'),
                func.sum(Payment.amount).label('total'),
                func.count(Payment.id).label('count')
            )
            .filter(Payment.date >= start_date)
            .group_by(month_expr)
            .order_by(month_expr)
            .all()
        )

        return [
            {
                'month': r.month,  # Already a string in YYYY-MM format
                'total': float(r.total),
                'count': r.count
            }
            for r in results
        ]
    else:
        # PostgreSQL: use date_trunc for date grouping
        results = (
            db.session.query(
                func.date_trunc('month', Payment.date).label('month'),
                func.sum(Payment.amount).label('total'),
                func.count(Payment.id).label('count')
            )
            .filter(Payment.date >= start_date)
            .group_by(func.date_trunc('month', Payment.date))
            .order_by(func.date_trunc('month', Payment.date))
            .all()
        )

        return [
            {
                'month': r.month.strftime('%Y-%m'),
                'total': float(r.total),
                'count': r.count
            }
            for r in results
        ]


# 🎯 Get member financial summary - CACHED
@cache.memoize(timeout=300)
def get_member_financial_summary(user_id):
    """
    Get comprehensive financial summary for a member in one query
    """
    # Use a single query with aggregates
    summary = (
        db.session.query(
            func.sum(Payment.amount).label('total_paid'),
            func.count(Payment.id).label('payment_count'),
            func.max(Payment.date).label('last_payment')
        )
        .filter(Payment.user_id == user_id)
        .first()
    )
    
    # Get active plan if exists
    active_plan = (
        PaymentPlan.query
        .filter_by(user_id=user_id, status="Active")
        .first()
    )
    
    return {
        'total_paid': float(summary.total_paid or 0),
        'payment_count': summary.payment_count or 0,
        'last_payment': summary.last_payment,
        'has_active_plan': active_plan is not None,
        'plan_balance': get_user_outstanding_balance(user_id) if active_plan else 0,
        'is_financial': float(summary.total_paid or 0) >= DUES_AMOUNT or active_plan is not None
    }


# 🔍 Search members efficiently
@cache.memoize(timeout=300)
def search_members(query_string, limit=20):
    """
    Search members by name or email with limit
    """
    search_term = f"%{query_string}%"
    
    return (
        User.query
        .filter(
            or_(
                User.name.ilike(search_term),
                User.email.ilike(search_term)
            )
        )
        .limit(limit)
        .all()
    )


# 🔄 CACHE INVALIDATION FUNCTIONS
def invalidate_payment_cache():
    """Clear all payment-related cache when payments change"""
    cache.delete_memoized(get_total_payments)
    cache.delete_memoized(get_payment_summary_by_type)
    cache.delete_memoized(get_payment_method_stats)
    cache.delete_memoized(get_unpaid_members)
    cache.delete_memoized(get_monthly_payments)
    # Don't delete get_payment_trends as it's less frequently changing


def invalidate_user_cache(user_id):
    """Clear cache for a specific user"""
    cache.delete_memoized(get_user_total_paid, user_id)
    cache.delete_memoized(get_user_outstanding_balance, user_id)
    cache.delete_memoized(get_member_financial_summary, user_id)
    cache.delete_memoized(get_unpaid_members)  # Unpaid list might change


def invalidate_plan_cache():
    """Clear plan-related cache"""
    cache.delete_memoized(get_users_with_active_plans)
    cache.delete_memoized(get_unpaid_members)