import logging
import os
from flask import Flask, render_template
from flask_migrate import Migrate


from sigma_finance.config import LocalConfig  # or switch to ProductionConfig
from sigma_finance.extensions import db, bcrypt, login_manager, cache, limiter, talisman
from sigma_finance.models import User

# Blueprints
from sigma_finance.routes.auth import auth
from sigma_finance.routes.show_dashboard import dashboard
from sigma_finance.routes.payments import payments
from sigma_finance.routes.treasurer import treasurer_bp
from sigma_finance.routes.invite import invite_bp
from sigma_finance.routes.webhooks import webhook_bp  # 👈 new webhook route
from sigma_finance.config import LocalConfig,ProductionConfig
from sigma_finance.config import read_render_secret

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

def create_app():
    app = Flask(__name__)

    # Use CONFIG_CLASS env var to toggle between LocalConfig and ProductionConfig

    config_class = read_render_secret("CONFIG_CLASS") or "sigma_finance.config.LocalConfig"
    app.config.from_object(config_class)
    print(f"Using configuration: {config_class}")

    


    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    Migrate(app, db)
    cache.init_app(app)
    limiter.init_app(app)


    # Initialize Talisman (Security Headers) - ONLY IN PRODUCTION
    if not app.debug:
        talisman.init_app(app,
            force_https=True,
            strict_transport_security=True,
            strict_transport_security_max_age=31536000,  # 1 year
            content_security_policy={
                'default-src': "'self'",
                'script-src': [
                    "'self'",
                    "'unsafe-inline'",  # Needed for inline JS
                    'https://js.stripe.com',
                    'https://cdnjs.cloudflare.com'
                ],
                'style-src': [
                    "'self'",
                    "'unsafe-inline'"  # Needed for Tailwind
                ],
                'img-src': [
                    "'self'",
                    'data:',
                    'https:'
                ],
                'font-src': [
                    "'self'",
                    'https://cdnjs.cloudflare.com'
                ],
                'connect-src': [
                    "'self'",
                    'https://api.stripe.com'
                ],
                'frame-src': [
                    "'self'",
                    'https://js.stripe.com',
                    'https://hooks.stripe.com'
                ]
            },
            content_security_policy_nonce_in=['script-src'],
            feature_policy={
                'geolocation': "'none'",
                'camera': "'none'",
                'microphone': "'none'"
            },
            # Set secure session cookie
            session_cookie_secure=True,
            session_cookie_samesite='Lax'
        )
    
    # Add min/max to Jinja2
    app.jinja_env.globals.update(min=min, max=max)

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(payments)
    app.register_blueprint(treasurer_bp, url_prefix="/treasurer")
    app.register_blueprint(invite_bp, url_prefix="/treasurer/invite")
    app.register_blueprint(webhook_bp)  # 👈 Stripe webhook listener

    app.jinja_env.globals.update(min=min, max=max)

    # Root route
    @app.route("/")
    def index():
        return render_template("home.html")

    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Error handler for rate limit exceeded
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return render_template('errors/429.html'), 429

    # Optional: Print all routes for debugging
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.rule}")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)