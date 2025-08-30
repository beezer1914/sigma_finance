from flask import Flask, render_template, redirect, url_for
from sigma_finance.config import Config
from sigma_finance.extensions import db, bcrypt, login_manager
from sigma_finance.routes.auth import auth
from sigma_finance.routes.show_dashboard import dashboard
from sigma_finance.routes.payments import payments
from sigma_finance.models import User
from flask_migrate import Migrate
from sigma_finance.routes.treasurer import treasurer_bp
from sigma_finance.routes.invite import invite_bp
from sigma_finance.extensions import mail


app = Flask(__name__)
app.config.from_object(Config)


db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "auth.login"

mail.init_app(app)

migrate = Migrate(app, db)

# Register blueprints

app.register_blueprint(auth)
app.register_blueprint(dashboard)
app.register_blueprint(payments)
app.register_blueprint(treasurer_bp, url_prefix='/treasurer')
app.register_blueprint(invite_bp, url_prefix="/treasurer/invite")

# 👇 Add this route to handle the root URL
@app.route("/")
def index():
    return render_template("home.html")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint}: {rule.rule}")

if __name__ == "__main__":
    app.run(debug=True)