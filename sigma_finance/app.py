import logging
import os
from flask import Flask, render_template, send_from_directory
from flask_migrate import Migrate


from sigma_finance.config import LocalConfig, ProductionConfig, read_render_secret
from sigma_finance.extensions import db, bcrypt, login_manager, cache, limiter, talisman, csrf
from sigma_finance.models import User

# Blueprints
from sigma_finance.routes.auth import auth
from sigma_finance.routes.show_dashboard import dashboard
from sigma_finance.routes.payments import payments
from sigma_finance.routes.treasurer import treasurer_bp
from sigma_finance.routes.invite import invite_bp
from sigma_finance.routes.webhooks import webhook_bp
from sigma_finance.routes.reports import reports_bp
from sigma_finance.routes.donations import donations_bp
from sigma_finance.routes.api import api_bp

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

    # Validate production configuration
    if not app.debug and config_class == "sigma_finance.config.ProductionConfig":
        try:
            ProductionConfig.validate()
            print("✅ Production configuration validated successfully")
        except ValueError as e:
            print(f"\n{'='*60}")
            print(f"CONFIGURATION ERROR")
            print(f"{'='*60}")
            print(str(e))
            print(f"{'='*60}\n")
            raise

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Custom unauthorized handler for API routes
    @login_manager.unauthorized_handler
    def unauthorized():
        """
        Handle unauthorized access attempts.
        - For API routes: Return JSON 401 (React handles login redirect)
        - For web routes: Redirect to login page (only in debug mode with Jinja templates)
        """
        from flask import request, jsonify, redirect, url_for

        # For API requests, return JSON 401
        if request.path.startswith('/api/'):
            return jsonify({
                "error": "Authentication required. Please log in.",
                "authenticated": False
            }), 401

        # For web requests in debug mode, redirect to login
        if app.debug:
            return redirect(url_for('auth.login'))

        # For web requests in production, return JSON (templates not registered)
        return jsonify({
            "error": "Authentication required",
            "authenticated": False
        }), 401

    Migrate(app, db)
    cache.init_app(app)
    limiter.init_app(app)  # Rate limiter reads RATELIMIT_STORAGE_URL from app.config automatically
    csrf.init_app(app)  # CSRF protection for all forms


    # Initialize Talisman (Security Headers) - ONLY IN ACTUAL PRODUCTION
    # Skip for local production testing (LocalProductionConfig)
    is_real_production = not app.debug and config_class == "sigma_finance.config.ProductionConfig"
    if is_real_production:
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
            # Note: Removed nonce requirement - React bundles don't use CSP nonces
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

    # Always register API and webhook blueprints (needed for React frontend)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(webhook_bp)

    # ⚠️ SECURITY WARNING: API routes currently exempted from CSRF protection
    # This is a KNOWN SECURITY RISK - API endpoints using session auth are vulnerable to CSRF attacks.
    #
    # MITIGATION IN PLACE:
    # - Rate limiting on sensitive endpoints (login: 3/15min, register: 3/hour, payments)
    # - Session regeneration on login (prevents session fixation)
    # - SameSite cookie policy (Lax in dev, Strict in production)
    # - Strong password requirements (12+ chars with complexity)
    # - No debug information in error responses
    #
    # CSRF Protection Strategy for React SPA + REST API:
    # API endpoints are exempted from Flask-WTF's CSRF (designed for server-rendered forms)
    # CSRF protection is instead provided by SameSite cookies:
    # - SESSION_COOKIE_SAMESITE = 'Strict' (production) / 'Lax' (dev)
    # - Prevents browsers from sending cookies in cross-site requests
    # - More appropriate for React SPA + REST API architecture than token-based CSRF
    # - Combined with HTTPONLY + SECURE cookies in production
    csrf.exempt(api_bp)

    # Register Jinja template blueprints ONLY in debug mode
    # In production, React handles all UI routes
    if app.debug:
        app.register_blueprint(auth)
        app.register_blueprint(dashboard)
        app.register_blueprint(payments)
        app.register_blueprint(treasurer_bp, url_prefix="/treasurer")
        app.register_blueprint(invite_bp, url_prefix="/treasurer/invite")
        app.register_blueprint(reports_bp, url_prefix="/reports")
        app.register_blueprint(donations_bp)

    # React frontend serving (production)
    # Use absolute path for reliability across environments
    react_build_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'react-frontend', 'dist'))
    print(f"React build path: {react_build_path}")
    print(f"React build exists: {os.path.exists(react_build_path)}")
    if os.path.exists(react_build_path):
        print(f"React build contents: {os.listdir(react_build_path)}")

    @app.route('/')
    def serve_react_index():
        """Serve React app index or fallback to Jinja template"""
        index_path = os.path.join(react_build_path, 'index.html')
        if not app.debug and os.path.exists(index_path):
            return send_from_directory(react_build_path, 'index.html')
        # In production without React build, return error (don't use Jinja templates)
        if not app.debug:
            return f"React build not found at {react_build_path}. Contents: {os.listdir(os.path.dirname(react_build_path)) if os.path.exists(os.path.dirname(react_build_path)) else 'parent dir not found'}", 500
        return render_template("home.html")

    @app.route('/assets/<path:filename>')
    def serve_react_assets(filename):
        """Serve React static assets (JS, CSS, etc.)"""
        return send_from_directory(os.path.join(react_build_path, 'assets'), filename)

    # Client-side routes - serve React index.html for SPA routing
    react_routes = [
        '/login', '/register', '/dashboard', '/payments', '/profile',
        '/treasurer', '/treasurer/payments', '/members', '/reports',
        '/donations', '/invites', '/payment/success', '/payment/cancel'
    ]

    @app.route('/<path:path>')
    def serve_react_catchall(path):
        """Handle React Router client-side routes"""
        # In production, serve React for all routes
        if not app.debug:
            # Check if it's a static file in dist
            file_path = os.path.join(react_build_path, path)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                return send_from_directory(react_build_path, path)
            # For all other routes, serve React index.html (let React Router handle it)
            index_path = os.path.join(react_build_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(react_build_path, 'index.html')
            # React build not found
            return f"React build not found for path: {path}", 404
        # In debug mode, let it fall through to 404 (Jinja blueprints handle routes)
        return render_template("home.html"), 404

    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Error handler for rate limit exceeded
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        from flask import jsonify, request

        # For API requests, always return JSON
        if request.path.startswith('/api/'):
            return jsonify({
                "error": "Too many requests. Please try again later.",
                "retry_after": 900  # 15 minutes in seconds
            }), 429

        # For web requests in production, return JSON (templates not registered)
        if not app.debug:
            return jsonify({"error": "Too many requests", "retry_after": 900}), 429

        # For web requests in debug, return template
        return render_template('errors/429.html'), 429

    # Debug: Print all routes (only in development)
    if app.debug:
        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule.rule}")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)