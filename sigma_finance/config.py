import os

# Root-level instance folder
INSTANCE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'instance')

def getenv_bool(name, default="false"):
    return os.getenv(name, default).strip().lower() in ("true", "1", "yes")

def read_render_secret(name):
    path = f"/etc/secrets/{name}"
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read().strip()
    return os.getenv(name)  # fallback for local dev

class BaseConfig:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(INSTANCE_DIR, 'sigma.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-key-change-this")
    DEBUG = getenv_bool("FLASK_DEBUG")

    # Frontend URL for Stripe redirects (override in subclasses)
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

    # Email
    SENDGRID_API_KEY = read_render_secret("SENDGRID_API_KEY")
    DEFAULT_FROM_EMAIL = read_render_secret("DEFAULT_FROM_EMAIL") or "no-reply@sds1914.com"

    # Stripe (Dues Account)
    STRIPE_SECRET_KEY = read_render_secret("STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY = read_render_secret("STRIPE_PUBLISHABLE_KEY")
    STRIPE_WEBHOOK_SECRET = read_render_secret("STRIPE_WEBHOOK_SECRET")

    # Stripe (Donations Account - Separate)
    DONATION_STRIPE_WEBHOOK_SECRET = read_render_secret("DONATION_STRIPE_WEBHOOK_SECRET")
    DONATION_STRIPE_LINK = read_render_secret("DONATION_STRIPE_LINK") or "https://donate.stripe.com/aFa9ATdI3gL572jcuMbQY00"
    
    # Cache Configuration - ADD THIS SECTION
    CACHE_TYPE = "SimpleCache"  # Default for local development
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes

class LocalConfig(BaseConfig):
    DEBUG = True
    TESTING = True

    # Frontend URL for redirects (Vite dev server)
    FRONTEND_URL = "http://localhost:5173"

    # SendGrid (set SENDGRID_API_KEY in your environment for local dev)
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")

    # Stripe test keys (set these in your environment for local dev)
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    # Donations (local dev defaults)
    DONATION_STRIPE_WEBHOOK_SECRET = ""
    DONATION_STRIPE_LINK = "https://donate.stripe.com/test_4gM5kDauR0AZbLvcW79sk00"

    # Use simple in-memory cache for local dev
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300

class LocalProductionConfig(LocalConfig):
    """Test production React serving locally (DEBUG=False but local DB/cache)"""
    DEBUG = False
    TESTING = False
    # Use localhost since React is served by Flask, not Vite
    FRONTEND_URL = "http://localhost:5000"

class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False

    # Frontend URL (same domain in production since React is served by Flask)
    FRONTEND_URL = read_render_secret("FRONTEND_URL") or "https://sds1914.com"

    # Use Redis for production caching - ADD THIS SECTION
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = read_render_secret("REDIS_URL") or "redis://localhost:6379/0"
    CACHE_DEFAULT_TIMEOUT = 600  # 10 minutes in production
    CACHE_KEY_PREFIX = "sigma_finance_"  # Prefix all cache keys

    # Secure session cookies
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Rate Limiting with Redis
    RATELIMIT_STORAGE_URL = read_render_secret("REDIS_URL") or "redis://localhost:6379/0"

    @classmethod
    def validate(cls):
        """
        Validate all required environment variables are set in production.
        Raises ValueError if any required variables are missing.
        """
        required_vars = {
            'FLASK_SECRET_KEY': cls.SECRET_KEY,
            'DATABASE_URL': cls.SQLALCHEMY_DATABASE_URI,
            'REDIS_URL': read_render_secret("REDIS_URL"),
            'STRIPE_SECRET_KEY': cls.STRIPE_SECRET_KEY,
            'STRIPE_PUBLISHABLE_KEY': cls.STRIPE_PUBLISHABLE_KEY,
            'STRIPE_WEBHOOK_SECRET': cls.STRIPE_WEBHOOK_SECRET,
            'DONATION_STRIPE_WEBHOOK_SECRET': cls.DONATION_STRIPE_WEBHOOK_SECRET,
            'SENDGRID_API_KEY': cls.SENDGRID_API_KEY,
            'DEFAULT_FROM_EMAIL': cls.DEFAULT_FROM_EMAIL
        }

        missing = []
        invalid = []

        for var_name, var_value in required_vars.items():
            if not var_value:
                missing.append(var_name)
            # Check for default/placeholder values
            elif var_name == 'FLASK_SECRET_KEY' and var_value == "dev-key-change-this":
                invalid.append(f"{var_name} (using insecure default)")
            elif var_name == 'DATABASE_URL' and 'sqlite' in str(var_value).lower():
                invalid.append(f"{var_name} (using SQLite instead of PostgreSQL)")

        if missing or invalid:
            error_msg = "Production configuration validation failed!\n"
            if missing:
                error_msg += f"\n❌ Missing required variables in Render dashboard:\n"
                for var in missing:
                    error_msg += f"   - {var}\n"
            if invalid:
                error_msg += f"\n⚠️  Invalid configuration values:\n"
                for var in invalid:
                    error_msg += f"   - {var}\n"
            error_msg += "\nPlease set these in your Render dashboard under Environment."
            raise ValueError(error_msg)

        return True