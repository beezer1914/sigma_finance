from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, SubmitField, StringField
from wtforms.validators import NumberRange, DataRequired, Email

class InviteForm(FlaskForm):
    email = StringField("Invitee Email", validators=[DataRequired(), Email(message="Enter a valid email address")])
    role = SelectField("Role", choices=[
        ("member", "Member"),
        ("treasurer", "Treasurer"),
        ("admin", "Admin"),
        ("president", "President"),
        ("vice_1", "1st Vice President"),
        ("vice_2", "2nd Vice President"),
        ("secretary", "Secretary")
    ])
    expires_in_days = IntegerField("Expires in (days)", default=7, validators=[NumberRange(min=1, max=365)])
    submit = SubmitField("Generate Invite Code")