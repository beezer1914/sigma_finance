from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, SubmitField
from wtforms.validators import NumberRange

class InviteForm(FlaskForm):
    role = SelectField("Role", choices=[("member", "Member"), ("admin", "Admin"), ("treasurer", "Treasurer")])
    expires_in_days = IntegerField("Expires in (days)", default=7, validators=[NumberRange(min=1, max=365)])
    submit = SubmitField("Generate Invite Code")