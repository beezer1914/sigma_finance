from wtforms import DecimalField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf import FlaskForm
from wtforms import HiddenField

class InstallmentPaymentForm(FlaskForm):
    amount = DecimalField("Total Amount", validators=[DataRequired(), NumberRange(min=0)])

    method = SelectField(
        "Payment Method",
        choices=[
            ("cash", "Cash"),
            ("zelle", "Zelle"),
            ("paypal", "PayPal"),
            ("card", "Credit/Debit Card"),
            ("other", "Other")
        ],
        validators=[DataRequired()]
    )
    type = HiddenField(default="installment")

    submit = SubmitField("Submit Payment")
    