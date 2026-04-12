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

    subject = "Sigma Delta Sigma — Dues Portal Invitation"

    plain_text = f"""Greetings brother {safe_name},

Our records indicate you're still a member of the Sigma Delta Sigma chapter of Phi Beta Sigma Fraternity Inc. We invite you to setup your account in our dues portal where you can easily view your current owed dues, make payments, or setup a payment plan.

Click the link below to get started:
{setup_url}

This link will expire in 7 days.

If we've reached you in error and you have moved on from the Sigma Delta Sigma chapter, please feel free to reach out to me at treasurer@sds1914.com and I will ensure our records are updated.

Fraternally,
Brandon Holiday, Treasurer
Sigma Delta Sigma Chapter
Phi Beta Sigma Fraternity, Inc.
"""

    html_content = f"""
        <div style="font-family:sans-serif;max-width:600px;margin:0 auto;color:#1f2937;">
          <p>Greetings brother {safe_name},</p>
          <p>
            Our records indicate you're still a member of the Sigma Delta Sigma chapter of
            <strong>Phi Beta Sigma Fraternity Inc.</strong> We invite you to setup your account
            in our dues portal where you can easily view your current owed dues, make payments,
            or setup a payment plan.
          </p>
          <p style="margin:24px 0;">
            <a href="{setup_url}"
               style="display:inline-block;padding:12px 24px;background-color:#1d4ed8;color:white;
                      text-decoration:none;border-radius:6px;font-weight:600;">
              Set Up My Account
            </a>
          </p>
          <p style="color:#6b7280;font-size:14px;">This link will expire in 7 days.</p>
          <p>
            If we've reached you in error and you have moved on from the Sigma Delta Sigma chapter,
            please feel free to reach out to me at
            <a href="mailto:treasurer@sds1914.com" style="color:#1d4ed8;">treasurer@sds1914.com</a>
            and I will ensure our records are updated.
          </p>
          <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;" />
          <p style="margin:0;">Fraternally,</p>
          <p style="margin:4px 0 0;font-weight:600;">Brandon Holiday, Treasurer</p>
          <p style="margin:2px 0;color:#6b7280;font-size:14px;">Sigma Delta Sigma Chapter</p>
          <p style="margin:2px 0;color:#6b7280;font-size:14px;">Phi Beta Sigma Fraternity, Inc.</p>
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

    subject = "Chapter Dues — Sigma Delta Sigma"

    plain_text = f"""Dear {safe_name},

A gentle reminder that chapter dues are now able to be paid online via the dues portal. Your current balance is ${amount_str}.

Log in to the dues portal to make a payment or set up a payment plan:
{login_url}

If this email has reached you in error and you're no longer a member of the Sigma Delta Sigma chapter, please reach out to me at treasurer@sds1914.com and I will ensure our records are updated.

Fraternally,
Brandon Holiday, Treasurer
Sigma Delta Sigma Chapter
Phi Beta Sigma Fraternity, Inc.
"""

    html_content = f"""
        <div style="font-family:sans-serif;max-width:600px;margin:0 auto;color:#1f2937;">
          <p>Dear {safe_name},</p>
          <p>
            A gentle reminder that chapter dues are now able to be paid online via the dues portal.
            Your current balance is <strong>${amount_str}</strong>.
          </p>
          <p style="margin:24px 0;">
            <a href="{login_url}"
               style="display:inline-block;padding:12px 24px;background-color:#1d4ed8;color:white;
                      text-decoration:none;border-radius:6px;font-weight:600;">
              Pay Dues Online
            </a>
          </p>
          <p>
            If this email has reached you in error and you're no longer a member of the Sigma Delta Sigma
            chapter, please reach out to me at
            <a href="mailto:treasurer@sds1914.com" style="color:#1d4ed8;">treasurer@sds1914.com</a>
            and I will ensure our records are updated.
          </p>
          <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;" />
          <p style="margin:0;">Fraternally,</p>
          <p style="margin:4px 0 0;font-weight:600;">Brandon Holiday, Treasurer</p>
          <p style="margin:2px 0;color:#6b7280;font-size:14px;">Sigma Delta Sigma Chapter</p>
          <p style="margin:2px 0;color:#6b7280;font-size:14px;">Phi Beta Sigma Fraternity, Inc.</p>
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
