from wtforms import DecimalField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf import FlaskForm

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

    submit = SubmitField("Submit Payment")