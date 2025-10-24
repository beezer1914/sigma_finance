import os
from flask import current_app, url_for
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sigma_finance.utils.sanitize import sanitize_for_email

# --- Send Email via SendGrid ---
def send_email(subject, to_email, plain_text, html_content=None, from_email=None):
    message = Mail(
        from_email=from_email or current_app.config["DEFAULT_FROM_EMAIL"],
        to_emails=to_email,
        subject=subject,
        plain_text_content=plain_text,
        html_content=html_content or plain_text
    )
    try:
        sg = SendGridAPIClient(current_app.config["SENDGRID_API_KEY"])
        response = sg.send(message)
        return response.status_code
    except Exception as e:
        import traceback
        print(f"SendGrid error: {e}")
        traceback.print_exc()
        return None
    

def send_password_reset_email(user):
    # Sanitize user input to prevent email header injection
    safe_name = sanitize_for_email(user.name)

    token = user.get_reset_token()
    reset_url = url_for('auth.reset_password', token=token, _external=True)

    subject = "Reset Your Sigma Finance Password"

    plain_text = f"""Hi {safe_name},

You requested a password reset. Click the link below to set a new password:
{reset_url}

If you didn't request this, you can safely ignore it.
"""

    html_content = f"""
        <p>Hi {safe_name},</p>
        <p>You requested a password reset. Click below to set a new password:</p>
        <p><a href="{reset_url}" style="color:#4F46E5;">Reset Password</a></p>
        <p>If you didn't request this, you can safely ignore it.</p>
    """

    return send_email(subject, user.email, plain_text, html_content)





