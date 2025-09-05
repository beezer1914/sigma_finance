from sigma_finance.extensions import db
from sigma_finance.models import User, Payment, PaymentPlan
from sqlalchemy import func
from datetime import datetime

# 🧮 Total amount paid by all users
def get_total_payments():
    return db.session.query(func.sum(Payment.amount)).scalar() or 0

# 👥 Users with active payment plans
def get_users_with_active_plans():
    return (
        db.session.query(User)
        .join(PaymentPlan, PaymentPlan.user_id == User.id)
        .filter(PaymentPlan.status.ilike("active"))
        .all()
    )

# 📅 Payments made this month
def get_monthly_payments():
    now = datetime.utcnow()
    return (
        db.session.query(Payment)
        .filter(func.extract("year", Payment.date) == now.year)
        .filter(func.extract("month", Payment.date) == now.month)
        .all()
    )

# 🧾 Total paid by a specific user
def get_user_total_paid(user_id):
    return (
        db.session.query(func.sum(Payment.amount))
        .filter(Payment.user_id == user_id)
        .scalar()
    ) or 0

# 📉 Outstanding balance for a user's active plan
def get_user_outstanding_balance(user_id):
    plan = (
        db.session.query(PaymentPlan)
        .filter(PaymentPlan.user_id == user_id, PaymentPlan.status == "active")
        .first()
    )
    if not plan:
        return 0

    paid = (
        db.session.query(func.sum(Payment.amount))
        .filter(Payment.user_id == user_id, Payment.plan_id == plan.id)
        .scalar()
    ) or 0

    return float(plan.total_amount) - float(paid)

# 📋 Summary of payments by type
def get_payment_summary_by_type():
   summary = {
       "one_time": db.session.query(func.count(Payment.id)).filter_by(payment_type="one-time").scalar() or 0,
       "plan": db.session.query(func.count(Payment.id)).filter_by(payment_type="plan").scalar() or 0
   }
   return summary
   
   
    #return (
       # db.session.query(Payment.payment_type, func.sum(Payment.amount))
       # .group_by(Payment.payment_type)
       # .all()
   # )

# 🧮 Count of unpaid members (no payments at all)
DUES_AMOUNT = 200  # Replace with your actual dues amount

def get_unpaid_members():
    all_members = User.query.all()
    unpaid = []

    for member in all_members:
        total_paid = sum(p.amount for p in member.payments)
        has_active_plan = any(
            plan.status and plan.status.strip().lower() == "active"
            for plan in member.payment_plans
        )

        if total_paid < DUES_AMOUNT and not has_active_plan:
            unpaid.append(member)

    return unpaid

# 📊 Payment method breakdown
def get_payment_method_stats():
   
   stats = {
        "stripe": db.session.query(func.count(Payment.id)).filter_by(method="stripe").scalar() or 0,
        "manual": db.session.query(func.count(Payment.id)).filter_by(method="manual").scalar() or 0
   }

   return stats
   
   
   
    #return (
     #   db.session.query(Payment.method, func.count(Payment.id), func.sum(Payment.amount))
      #  .group_by(Payment.method)
     #   .all()
   # )