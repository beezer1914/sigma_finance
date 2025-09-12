from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class PaymentForm(FlaskForm):
    amount = DecimalField("Amount", validators=[DataRequired(), NumberRange(min=0)])
    method = SelectField("Payment Method", choices=[("cash", "Cash"), ("Online Payment", "Online Payment")])
    type = SelectField("Payment Type", choices=[("one-time", "One-Time")])
    notes = StringField("Notes")
    submit = SubmitField("Submit Payment")
   