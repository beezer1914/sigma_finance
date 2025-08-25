import os

# Base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # SQLite database path (absolute)
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "../instance/site.db")

    # Disable modification tracking to save resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secret key for session management and CSRF protection
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-this")

    # Optional: Enable debugging features
    DEBUG = True