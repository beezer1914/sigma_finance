from flask_mail import Message
from flask import url_for
from app import mail

def send_invite_email(recipient_email, invite_code):
    link = url_for("auth.register", code=invite_code, _external=True)
    msg = Message(
        subject="Welcome to the new SDS Dues app!",
        recipients=[recipient_email],
        body=f"""
     Use the link below to create your account:

{link}

This code expires soon, so don’t wait!
""",
    )
    mail.send(msg)