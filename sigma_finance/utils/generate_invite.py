import secrets
from datetime import datetime, timedelta

def generate_invite_code(role="member", expires_in_days=7):
    code = secrets.token_urlsafe(8)
    return code, datetime.utcnow() + timedelta(days=expires_in_days), role