from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
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


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Email()],
        render_kw={
            "placeholder": "you@example.com",
            "autocomplete": "email",
            "aria-label": "Email address",
            "class": (
                "mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm "
                "focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            )
        }
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired()],
        render_kw={
            "placeholder": "Enter your password",
            "autocomplete": "current-password",
            "aria-label": "Password",
            "class": (
                "mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm "
                "focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            )
        }
    )

    remember_me = BooleanField(
        "Remember Me",
        render_kw={"class": "mr-2"}
    )

    submit = SubmitField(
        "Login",  # Visible text on the button
        render_kw={
            "class": (
                "w-full bg-indigo-600 text-white py-2 px-4 rounded hover:bg-indigo-700 "
                "transition duration-200 ease-in-out"
            )
        }
    )





class ForgotPasswordForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Email()],
        render_kw={
            "placeholder": "you@example.com",
            "autocomplete": "email",
            "class": (
                "mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm "
                "focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            )
        }
    )
    submit = SubmitField(
        "Send Reset Link",
        render_kw={
            "class": (
                "w-full bg-indigo-600 text-white py-2 px-4 rounded hover:bg-indigo-700 "
                "transition duration-200 ease-in-out"
            )
        }
    )


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "New Password",
        validators=[DataRequired(), Length(min=12, message="Password must be at least 12 characters long."), validate_password_complexity],
        render_kw={
            "placeholder": "Enter new password (min 12 chars)",
            "autocomplete": "new-password",
            "class": (
                "mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm "
                "focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            )
        }
    )
    confirm = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo('password')],
        render_kw={
            "placeholder": "Confirm new password",
            "autocomplete": "new-password",
            "class": (
                "mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm "
                "focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            )
        }
    )
    submit = SubmitField(
        "Reset Password",
        render_kw={
            "class": (
                "w-full bg-indigo-600 text-white py-2 px-4 rounded hover:bg-indigo-700 "
                "transition duration-200 ease-in-out"
            )
        }
    )