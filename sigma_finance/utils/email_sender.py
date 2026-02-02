import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Category
from sigma_finance.utils.sanitize import sanitize_for_email

def send_payment_reminder(to_email, name, due_date, amount, frequency='monthly'):
    # Sanitize user input to prevent email header injection
    safe_name = sanitize_for_email(name)

    # Customize subject and message based on frequency
    frequency_text = {
        'weekly': 'Weekly',
        'monthly': 'Monthly',
        'quarterly': 'Quarterly'
    }.get(frequency, 'Payment')

    message = Mail(
        from_email='treasurer@sds1914.com',
        to_emails=to_email,
        subject=f'{frequency_text} Dues Reminder - Sigma Delta Sigma',
        html_content=f"""
        <p>Hi {safe_name},</p>
        <p>This is your <strong>{frequency}</strong> reminder that your dues payment of <strong>${amount}</strong> is due by <strong>{due_date.strftime('%B %d, %Y')}</strong>.</p>
        <p>Please log in to your dashboard to complete your payment: <a href="https://sigma-finance-63gn.onrender.com/login">https://sigma-finance-63gn.onrender.com/login</a></p>
        <p>Thank you for staying financially active with Sigma Delta Sigma!</p>
        <p style="margin-top: 20px; font-size: 12px; color: #666;">
        Questions? Contact the treasurer at treasurer@sds1914.com
        </p>
        """
    )

    # Add category for tracking in SendGrid webhooks
    message.category = Category(f'payment_reminder_{frequency}')
    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        print(f"Email sent to {to_email}: {response.status_code}")
    except Exception as e:
        print(f"SendGrid error: {e}")