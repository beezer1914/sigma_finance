# sigma_finance/forms/register_form.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from sigma_finance.models import InviteCode
from datetime import datetime

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
        validators=[DataRequired(), Length(min=6)]
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