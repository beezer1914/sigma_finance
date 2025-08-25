import secrets

def generate_invite_code(length=16):
    return secrets.token_urlsafe(length)[:length]