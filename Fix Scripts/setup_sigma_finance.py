import os
import subprocess

BASE_DIR = "sigma_finance"
folders = [
    "routes", "forms", "templates", "static", "venv"
]
templates = {
    "login.html": "<h2>Login</h2>{% for field in form %}{{ field.label }}{{ field }}<br>{% endfor %}",
    "dashboard.html": "<h2>Welcome {{ name }}</h2><a href='/pay/one-time'>One-Time Payment</a> | <a href='/pay/plan'>Payment Plan</a>",
    "one_time.html": "<h2>One-Time Payment</h2>{% for field in form %}{{ field.label }}{{ field }}<br>{% endfor %}",
    "plan.html": "<h2>Payment Plan</h2>{% for field in form %}{{ field.label }}{{ field }}<br>{% endfor %}"
}

def write_file(path, content):
    with open(path, "w") as f:
        f.write(content)

def create_structure():
    os.makedirs(BASE_DIR, exist_ok=True)
    for folder in folders:
        os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)
    for name, html in templates.items():
        write_file(os.path.join(BASE_DIR, "templates", name), html)

def write_core_files():
    # config.py
    write_file(os.path.join(BASE_DIR, "config.py"), """import os
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev_secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
""")

    # extensions.py
    write_file(os.path.join(BASE_DIR, "extensions.py"), """from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
""")

    # models.py
    write_file(os.path.join(BASE_DIR, "models.py"), """from extensions import db, bcrypt
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    method = db.Column(db.String(50))
    type = db.Column(db.String(20))  # 'one-time' or 'installment'
    notes = db.Column(db.String(255))

class PaymentPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    frequency = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    installment_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default="active")
""")

    # app.py
    write_file(os.path.join(BASE_DIR, "app.py"), """from flask import Flask
from config import Config
from extensions import db, bcrypt, login_manager
from routes.auth import auth
from routes.dashboard import dashboard
from routes.payments import payments

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "auth.login"

app.register_blueprint(auth)
app.register_blueprint(dashboard)
app.register_blueprint(payments)

if __name__ == "__main__":
    app.run(debug=True)
""")

def write_routes_and_forms():
    # auth.py
    write_file(os.path.join(BASE_DIR, "routes", "auth.py"), """from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user
from models import User
from forms.login_form import LoginForm

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for("dashboard.dashboard"))
        flash("Invalid credentials", "danger")
    return render_template("login.html", form=form)
""")

    # dashboard.py
    write_file(os.path.join(BASE_DIR, "routes", "dashboard.py"), """from flask import Blueprint, render_template
from flask_login import login_required, current_user

dashboard = Blueprint("dashboard", __name__)

@dashboard.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", name=current_user.email)
""")

    # payments.py
    write_file(os.path.join(BASE_DIR, "routes", "payments.py"), """from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Payment, PaymentPlan
from forms.one_time_form import OneTimePaymentForm
from forms.plan_form import PaymentPlanForm

payments = Blueprint("payments", __name__)

@payments.route("/pay/one-time", methods=["GET", "POST"])
@login_required
def one_time():
    form = OneTimePaymentForm()
    if form.validate_on_submit():
        payment = Payment(
            user_id=current_user.id,
            amount=form.amount.data,
            method=form.method.data,
            type="one-time",
            notes=form.notes.data
        )
        db.session.add(payment)
        db.session.commit()
        flash("Payment submitted successfully!", "success")
        return redirect(url_for("dashboard.dashboard"))
    return render_template("one_time.html", form=form)

@payments.route("/pay/plan", methods=["GET", "POST"])
@login_required
def plan():
    form = PaymentPlanForm()
    if form.validate_on_submit():
        plan = PaymentPlan(
            user_id=current_user.id,
            frequency=form.frequency.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            total_amount=form.total_amount.data,
            installment_amount=form.installment_amount.data
        )
        db.session.add(plan)
        db.session.commit()
        flash("Payment plan enrolled!", "success")
        return redirect(url_for("dashboard.dashboard"))
    return render_template("plan.html", form=form)
""")

    # login_form.py
    write_file(os.path.join(BASE_DIR, "forms", "login_form.py"), """from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")
""")

    # one_time_form.py
    write_file(os.path.join(BASE_DIR, "forms", "one_time_form.py"), """from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SubmitField
from wtforms.validators import DataRequired

class OneTimePaymentForm(FlaskForm):
    amount = DecimalField("Amount", validators=[DataRequired()])
    method = StringField("Payment Method", validators=[DataRequired()])
    notes = StringField("Notes")
    submit = SubmitField("Submit Payment")
""")

    # plan_form.py
    write_file(os.path.join(BASE_DIR, "forms", "plan_form.py"), """from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateField, SubmitField
from wtforms.validators import DataRequired

class PaymentPlanForm(FlaskForm):
    frequency = StringField("Frequency", validators=[DataRequired()])
    start_date = DateField("Start Date", validators=[DataRequired()])
    end_date = DateField("End Date", validators=[DataRequired()])
    total_amount = DecimalField("Total Amount", validators=[DataRequired()])
    installment_amount = DecimalField("Installment Amount", validators=[DataRequired()])
    submit = SubmitField("Enroll in Plan")
""")

def install_dependencies():
    subprocess.run(["python", "-m", "venv", os.path.join(BASE_DIR, "venv")])
    subprocess.run([os.path.join(BASE_DIR, "venv", "Scripts", "pip"), "install", "flask", "flask_sqlalchemy", "flask_bcrypt", "flask_login", "flask_wtf"])

def main():
    create_structure()
    write_core_files()
    write_routes_and_forms()
    install_dependencies()
    print("✅ Sigma Finance scaffold created successfully.")
    print("👉 To run the app:")
    print("   1. Activate the virtual environment:")
    print("      sigma_finance\\venv\\Scripts\\activate")
    print("   2. Run the app:")
    print("      python app.py")

if __name__ == "__main__":
    main()