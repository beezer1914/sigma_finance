import logging
import os
from flask import Flask, render_template
from flask_migrate import Migrate

from sigma_finance.config import LocalConfig  # or switch to ProductionConfig
from sigma_finance.extensions import db, bcrypt, login_manager
from sigma_finance.models import User

# Blueprints
from sigma_finance.routes.auth import auth
from sigma_finance.routes.show_dashboard import dashboard
from sigma_finance.routes.payments import payments
from sigma_finance.routes.treasurer import treasurer_bp
from sigma_finance.routes.invite import invite_bp
from sigma_finance.routes.webhooks import webhook_bp  # 👈 new webhook route
from sigma_finance.config import LocalConfig,ProductionConfig

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

def create_app():
    app = Flask(__name__)

    # Use CONFIG_CLASS env var to toggle between LocalConfig and ProductionConfig
    
    config_class = os.getenv("CONFIG_CLASS", "sigma_finance.config.LocalConfig")
    app.config.from_object(config_class)  # swap with ProductionConfig as needed

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    Migrate(app, db)

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(payments)
    app.register_blueprint(treasurer_bp, url_prefix="/treasurer")
    app.register_blueprint(invite_bp, url_prefix="/treasurer/invite")
    app.register_blueprint(webhook_bp)  # 👈 Stripe webhook listener

    # Root route
    @app.route("/")
    def index():
        return render_template("home.html")

    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Optional: Print all routes for debugging
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.rule}")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)