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

from flask import current_app


def send_account_setup_email(user, setup_url):
    """Send a welcome + account setup email to a newly imported member."""
    safe_name = sanitize_for_email(user.name)

    subject = "Welcome to Sigma Finance — Set Up Your Account"

    plain_text = f"""Hi {safe_name},

You have been added to Sigma Delta Sigma's dues portal, Sigma Finance.

Click the link below to set up your password and get started:
{setup_url}

This link will expire in 7 days.

Once you're in, you can view your dues balance and make payments directly through the portal.

Questions? Reach out to the treasurer at treasurer@sds1914.com
"""

    html_content = f"""
        <div style="font-family:sans-serif;max-width:600px;margin:0 auto;">
          <h2 style="color:#1e40af;">Welcome to Sigma Finance</h2>
          <p>Hi {safe_name},</p>
          <p>You have been added to <strong>Sigma Delta Sigma's</strong> dues portal.</p>
          <p>Click below to set up your password and access your account:</p>
          <p style="margin:24px 0;">
            <a href="{setup_url}"
               style="display:inline-block;padding:12px 24px;background-color:#1d4ed8;color:white;
                      text-decoration:none;border-radius:6px;font-weight:600;">
              Set Up My Account
            </a>
          </p>
          <p style="color:#6b7280;font-size:14px;">This link will expire in 7 days.</p>
          <p>Once you are in, you can view your dues balance and make payments directly through the portal.</p>
          <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;" />
          <p style="color:#6b7280;font-size:12px;">
            Questions? Contact the treasurer at
            <a href="mailto:treasurer@sds1914.com" style="color:#1d4ed8;">treasurer@sds1914.com</a>
          </p>
        </div>
    """

    message = Mail(
        from_email='treasurer@sds1914.com',
        to_emails=user.email,
        subject=subject,
        plain_text_content=plain_text,
        html_content=html_content
    )
    message.category = Category('account_setup')

    try:
        sg = SendGridAPIClient(current_app.config.get("SENDGRID_API_KEY") or os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        return response.status_code
    except Exception as e:
        import traceback
        print(f"SendGrid error (setup email): {e}")
        traceback.print_exc()
        return None


def send_invoice_email(user, amount_owed):
    """Send a dues invoice email to a member with an outstanding balance."""
    safe_name = sanitize_for_email(user.name)
    amount_str = f"{float(amount_owed):.2f}"
    login_url = current_app.config.get('FRONTEND_URL', 'https://sigma-finance-63gn.onrender.com') + '/dashboard'

    subject = "Dues Invoice — Sigma Delta Sigma"

    plain_text = f"""Hi {safe_name},

This is a reminder that you have an outstanding dues balance of ${amount_str} with Sigma Delta Sigma.

Please log in to your account to view your balance and complete your payment:
{login_url}

If you have questions or believe this is an error, please contact the treasurer at treasurer@sds1914.com.

Thank you,
Sigma Delta Sigma Treasurer
"""

    html_content = f"""
        <div style="font-family:sans-serif;max-width:600px;margin:0 auto;">
          <h2 style="color:#1e40af;">Dues Invoice</h2>
          <p>Hi {safe_name},</p>
          <p>This is a reminder that you have an outstanding dues balance with <strong>Sigma Delta Sigma</strong>.</p>
          <table style="width:100%;border-collapse:collapse;margin:20px 0;">
            <tr style="background:#f3f4f6;">
              <td style="padding:12px 16px;font-weight:600;border:1px solid #e5e7eb;">Amount Due</td>
              <td style="padding:12px 16px;font-size:20px;font-weight:700;color:#dc2626;border:1px solid #e5e7eb;">
                ${amount_str}
              </td>
            </tr>
          </table>
          <p style="margin:24px 0;">
            <a href="{login_url}"
               style="display:inline-block;padding:12px 24px;background-color:#1d4ed8;color:white;
                      text-decoration:none;border-radius:6px;font-weight:600;">
              Pay Now
            </a>
          </p>
          <p style="color:#6b7280;font-size:14px;">
            Questions? Contact the treasurer at
            <a href="mailto:treasurer@sds1914.com" style="color:#1d4ed8;">treasurer@sds1914.com</a>
          </p>
        </div>
    """

    message = Mail(
        from_email='treasurer@sds1914.com',
        to_emails=user.email,
        subject=subject,
        plain_text_content=plain_text,
        html_content=html_content
    )
    message.category = Category('invoice')

    try:
        sg = SendGridAPIClient(current_app.config.get("SENDGRID_API_KEY") or os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        return response.status_code
    except Exception as e:
        import traceback
        print(f"SendGrid error (invoice email): {e}")
        traceback.print_exc()
        return None
