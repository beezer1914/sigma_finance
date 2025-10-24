import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sigma_finance.utils.sanitize import sanitize_for_email

def send_payment_reminder(to_email, name, due_date, amount):
    # Sanitize user input to prevent email header injection
    safe_name = sanitize_for_email(name)
    message = Mail(
        from_email='treasurer@sds1914.com',
        to_emails=to_email,
        subject='Payment Plan Reminder',
        html_content=f"""
        <p>Hi {safe_name},</p>
        <p>This is a reminder that your next payment of <strong>${amount}</strong> is due by <strong>{due_date.strftime('%B %d, %Y')}</strong>.</p>
        <p>Please log in to your dashboard to complete your payment.</p>
        <p>Thank you for staying financially active!</p>
        """
    )
    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        print(f"Email sent to {to_email}: {response.status_code}")
    except Exception as e:
        print(f"SendGrid error: {e}")