from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Email()],
        render_kw={
            "class": "mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        }
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired()],
        render_kw={
            "class": "mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        }
    )

    submit = SubmitField(
        "Login",
        render_kw={
            "class": "w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition"
        }
    )