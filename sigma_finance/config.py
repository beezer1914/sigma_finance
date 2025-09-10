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

    # Email
    SENDGRID_API_KEY = read_render_secret("SENDGRID_API_KEY")
    DEFAULT_FROM_EMAIL = read_render_secret("DEFAULT_FROM_EMAIL") or "no-reply@sds1914.com"

    # Stripe
    STRIPE_SECRET_KEY = read_render_secret("STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY = read_render_secret("STRIPE_PUBLISHABLE_KEY")
    STRIPE_WEBHOOK_SECRET = read_render_secret("STRIPE_WEBHOOK_SECRET")

class LocalConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    STRIPE_SECRET_KEY = ""
    STRIPE_PUBLISHABLE_KEY = ""
    STRIPE_WEBHOOK_SECRET = ""

class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False