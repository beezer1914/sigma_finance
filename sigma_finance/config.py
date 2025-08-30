import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def getenv_bool(name, default="false"):
    return os.getenv(name, default).strip().lower() in ("true","1","yes")

class Config:
    SQLALCHEMY_DATABASE_URI    = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'local.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY                 = os.getenv("SECRET_KEY", "dev-key-change-this")
    DEBUG                      = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    MAIL_SERVER     = os.getenv("MAIL_SERVER", "mail.sds1914.com")
    MAIL_PORT       = int(os.getenv("MAIL_PORT", 465))
    MAIL_USE_TLS    = getenv_bool("MAIL_USE_TLS", "false")
    MAIL_USE_SSL    = getenv_bool("MAIL_USE_SSL", "true")
    if MAIL_USE_TLS and MAIL_USE_SSL:
        raise RuntimeError("MAIL_USE_TLS and MAIL_USE_SSL both enabled")
    MAIL_USERNAME   = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD   = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)