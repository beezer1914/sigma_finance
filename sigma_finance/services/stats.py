# sigma_finance/services/stats.py - HEAVILY OPTIMIZED VERSION

from sigma_finance.extensions import db
from sigma_finance.models import User, Payment, PaymentPlan
from sqlalchemy import func, and_, or_
from datetime import datetime

# 🧮 Total amount paid by all users - OPTIMIZED
def get_total_payments():
    """
    Single aggregate query - MUCH faster than loading all payments
    """
    result = db.session.query(func.sum(Payment.amount)).scalar()
    return float(result or 0)


# 👥 Users with active payment plans - OPTIMIZED
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


# 📅 Payments made this month - OPTIMIZED
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


# 🧾 Total paid by a specific user - OPTIMIZED
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


# 📉 Outstanding balance for a user's active plan - OPTIMIZED
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


# 📋 Summary of payments by type - OPTIMIZED
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


# 🧮 Count of unpaid members - HEAVILY OPTIMIZED
DUES_AMOUNT = 200  # Move to config later

def get_unpaid_members():
    """
    Ultra-optimized query using subqueries
    
    Before: Load all users, all payments, loop in Python - SLOW!
    After: Single SQL query with subqueries - FAST!
    """
    
    # Subquery: Users who have paid $200 or more
    paid_users_subquery = (
        db.session.query(Payment.user_id)
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
    unpaid_members = (
        db.session.query(User)
        .filter(
            User.active == True,
            ~User.id.in_(paid_users_subquery),
            ~User.id.in_(active_plan_users_subquery)
        )
        .order_by(User.name)
        .all()
    )
    
    return unpaid_members


# 📊 Payment method breakdown - OPTIMIZED
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


# 📈 Get payment trends - NEW FUNCTION
def get_payment_trends(months=6):
    """
    Get monthly payment totals for the last N months
    Useful for charts/graphs
    """
    from dateutil.relativedelta import relativedelta
    
    end_date = datetime.utcnow()
    start_date = end_date - relativedelta(months=months)
    
    # Group by month and sum amounts
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


# 🎯 Get member financial summary - NEW FUNCTION
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


# 🔍 Search members efficiently - NEW FUNCTION
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