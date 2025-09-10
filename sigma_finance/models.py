from sigma_finance.extensions import db, bcrypt
from flask_login import UserMixin, current_user
from datetime import datetime
from werkzeug.security import check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)
    role = db.Column(db.String(20), default="member")  # 'admin', 'treasurer','member'
    status = db.Column(db.Boolean, default=True)
    financial_status = db.Column(db.String(20), default="not financial")
    active = db.Column(db.Boolean, default=True)

    # 🔗 Relationships
    payments = db.relationship("Payment", backref="user", lazy="dynamic")
    payment_plans = db.relationship("PaymentPlan", backref="user", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_token(self, expires_in=600):
        secret = str(current_app.config["SECRET_KEY"])  # Defensive cast
        s = Serializer(secret, expires_in)
        return s.dumps({"user_id": self.id})

    @staticmethod
    def verify_reset_token(token):
        secret = str(current_app.config["SECRET_KEY"])  # Defensive cast
        s = Serializer(secret)
        try:
            data = s.loads(token)
        except Exception:
            return None
        return User.query.get(data["user_id"])