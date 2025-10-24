"""
Email and input sanitization utilities to prevent injection attacks.
"""
import html
import re


def sanitize_for_email(text):
    """
    Sanitize text for safe use in email content.

    Prevents email header injection by:
    1. Removing newline characters (\r\n) that could inject headers
    2. HTML-escaping to prevent XSS in HTML emails
    3. Stripping extra whitespace

    Args:
        text: User-provided text (name, etc.)

    Returns:
        Sanitized string safe for email content
    """
    if not text:
        return ""

    # Convert to string and remove all newlines/carriage returns
    text = re.sub(r'[\r\n]+', ' ', str(text))

    # HTML escape for safety in HTML emails
    text = html.escape(text)

    # Strip leading/trailing whitespace
    return text.strip()


def sanitize_email_address(email):
    """
    Basic email address validation and sanitization.

    Args:
        email: Email address string

    Returns:
        Sanitized email address or None if invalid
    """
    if not email:
        return None

    # Remove whitespace
    email = str(email).strip().lower()

    # Basic email format validation (simple regex)
    # Note: WTForms Email validator should be used for comprehensive validation
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return None

    return email


def sanitize_for_html(text):
    """
    Sanitize text for safe display in HTML templates.

    Note: Jinja2 auto-escapes by default, but use this for extra safety
    or when rendering in non-Jinja contexts.

    Args:
        text: User-provided text

    Returns:
        HTML-escaped string
    """
    if not text:
        return ""

    return html.escape(str(text))
