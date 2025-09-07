from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, DecimalField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Optional
from datetime import date

class PaymentPlanForm(FlaskForm):
    # Enrollment fields
    frequency = SelectField(
        "Payment Frequency",
        choices=[ ("quarterly", "Quarterly")],
        validators=[Optional()]  # Optional for installment mode
    )
    start_date = DateField("Start Date", default=date.today, validators=[Optional()])
    amount = DecimalField("Total Amount", default=200.00, places=2, render_kw={"readonly": True}, validators=[Optional()])

    # Installment payment field
    installment_amount = DecimalField("Installment Amount", places=2, validators=[Optional()])

    # Mode flag (optional, for template logic)
    mode = HiddenField("Mode")

    submit = SubmitField("Submit")