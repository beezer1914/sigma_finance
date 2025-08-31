import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def getenv_bool(name, default="false"):
    return os.getenv(name, default).strip().lower() in ("true","1","yes")

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'local.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-this")
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    # 👇 Add this line
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")