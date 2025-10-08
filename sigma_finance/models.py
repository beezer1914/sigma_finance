from sigma_finance.extensions import db, bcrypt
from flask_login import UserMixin, current_user
from datetime import datetime, date
from werkzeug.security import check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)
    role = db.Column(db.String(20), default="member")  # 'admin', 'treasurer','member'
    status = db.Column(db.Boolean, default=True)
    financial_status = db.Column(db.String(20), default="not financial")
    active = db.Column(db.Boolean, default=True)
    initiation_date = db.Column(db.Date, nullable=True)

    # 🔗 Relationships
    payments = db.relationship("Payment", backref="user", lazy="dynamic")
    payment_plans = db.relationship("PaymentPlan", backref="user", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



    def get_reset_token(self, expires_in=600):
        secret = str(current_app.config["SECRET_KEY"])
        s = Serializer(secret, salt="password-reset")
        return s.dumps({"user_id": self.id})

    @staticmethod
    def verify_reset_token(token):
        secret = str(current_app.config["SECRET_KEY"])
        s = Serializer(secret, salt="password-reset")
        try:
            data = s.loads(token, max_age=600)
        except Exception:
            return None
        return User.query.get(data["user_id"])
    
    def is_neophyte(self):
    # Check if explicitly marked as neophyte
        if self.financial_status == "neophyte":
            return True
    # Also check if initiated within last year
        if self.initiation_date and (date.today() - self.initiation_date).days <= 365:
            return True
        return False
    
    def is_financial(self):
        if self.is_neophyte():
            return True
        return self.financial_status == "financial"


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    method = db.Column(db.String(50))
    payment_type = db.Column(db.String(20))  # 'one-time' or 'installment'
    notes = db.Column(db.String(255))

    # 🔗 Relationship to payment plan
    plan_id = db.Column(db.Integer, db.ForeignKey("payment_plan.id"), nullable=True)
    plan = db.relationship("PaymentPlan", backref="payments")

    def total_paid(self):
        return sum(p.amount for p in self.payments)

    def is_complete(self):
        return self.total_paid() >= self.total_amount


class PaymentPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    frequency = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    installment_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default="active") 
    expected_installments = db.Column(db.Integer, nullable=True)
    enforce_installments = db.Column(db.Boolean, default=False)

    def total_paid(self):
        return sum(payment.amount for payment in self.payments)

class ArchivedPaymentPlan(db.Model):
    __tablename__ = "archived_payment_plan"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    frequency = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    installment_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default="active") 
    completed_on = db.Column(db.DateTime)

class InviteCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    role = db.Column(db.String(20), default="member")  # 'member', 'admin', etc.
    used = db.Column(db.Boolean, default=False)
    used_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    used_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())

    # Relationships
    issuer = db.relationship("User", foreign_keys=[created_by], backref="invites_created")
    redeemer = db.relationship("User", foreign_keys=[used_by], backref="invite_used")


class WebhookEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(64), nullable=False)
    payload = db.Column(db.Text, nullable=False)
    received_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.String(255))  # Optional: error messages or context
  