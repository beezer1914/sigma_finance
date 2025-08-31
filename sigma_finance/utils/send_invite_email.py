from flask import current_app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(subject, to_email, plain_text, html_content=None, from_email=None):
    message = Mail(
        from_email = from_email or current_app.config["DEFAULT_FROM_EMAIL"],
        to_emails  = to_email,
        subject    = subject,
        plain_text_content = plain_text,
        html_content       = html_content or plain_text
    )
    try:
        sg = SendGridAPIClient(current_app.config["SENDGRID_API_KEY"])
        response = sg.send(message)
        return response.status_code
    except Exception as e:
        print(f"SendGrid error: {e}")
        return None