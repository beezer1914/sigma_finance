from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, NumberRange, Email

class DonationForm(FlaskForm):
    """Form for manual donation entry by treasurers/admins"""
    donor_name = StringField("Donor Name", validators=[DataRequired()])
    donor_email = StringField("Donor Email", validators=[DataRequired(), Email()])
    amount = DecimalField("Amount", validators=[DataRequired(), NumberRange(min=0.01)])
    method = SelectField("Payment Method", choices=[
        ("stripe", "Stripe Payment Link"),
        ("check", "Check"),
        ("cash", "Cash"),
        ("other", "Other")
    ])
    anonymous = BooleanField("Anonymous Donation")
    notes = StringField("Notes")
    submit = SubmitField("Record Donation")
