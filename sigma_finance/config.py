import os

# Base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Use DATABASE_URL from environment, fallback to local SQLite for dev
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'local.db')}"
    )

    # Disable modification tracking to save resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secret key for session management and CSRF protection
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-this")

    # Optional: Enable debugging features
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"