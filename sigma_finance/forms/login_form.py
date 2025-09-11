from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo


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
        render_kw={
            "class": "mr-2"
        }
    )

    submit = SubmitField(
        "Login",
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
        validators=[DataRequired()],
        render_kw={
            "placeholder": "Enter new password",
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