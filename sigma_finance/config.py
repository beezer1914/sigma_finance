import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def getenv_bool(name, default="false"):
    return os.getenv(name, default).strip().lower() in ("true", "1", "yes")

def read_render_secret(name):
    path = f"/etc/secrets/{name}"
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read().strip()
    return os.getenv(name)  # fallback for local dev

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'local.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-this")
    DEBUG = getenv_bool("FLASK_DEBUG")

    # ✅ Updated to read from Render secrets if available
    SENDGRID_API_KEY = read_render_secret("SENDGRID_API_KEY")
    DEFAULT_FROM_EMAIL = read_render_secret("DEFAULT_FROM_EMAIL") or "no-reply@sds1914.com"