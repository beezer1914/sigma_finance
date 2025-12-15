# sigma_finance/forms/register_form.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Regexp
from sigma_finance.models import InviteCode
from datetime import datetime
import re

def validate_password_complexity(form, field):
    """
    Validate password complexity requirements:
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    password = field.data
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter.')
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter.')
    if not re.search(r'\d', password):
        raise ValidationError('Password must contain at least one digit.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>).')

class RegisterForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired(), Length(min=2, max=100)]
    )
    email = StringField(
        "Email",
        validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=12, message="Password must be at least 12 characters long."), validate_password_complexity]
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match.")
        ]
    )

    # ——— Add this field ———
    invite_code = StringField(
        "Invite Code",
        validators=[DataRequired(), Length(min=4, max=32)]
    )

    submit = SubmitField("Register")

    # ——— And this hook ———
    def validate_invite_code(self, field):
        code = field.data.strip()
        invite = InviteCode.query.filter_by(code=code).first()
        if not invite:
            raise ValidationError("That invite code does not exist.")
        if invite.used:
            raise ValidationError("This invite code has already been claimed.")
        if invite.expires_at and invite.expires_at < datetime.utcnow():
            raise ValidationError("This invite code has expired.")