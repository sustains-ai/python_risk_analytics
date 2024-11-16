from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, DateField, SelectField, TextAreaField, PasswordField
from wtforms.validators import InputRequired, NumberRange, DataRequired, Email

class FinanceDataForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    category = SelectField(
        'Category',
        choices=[
            ('food', 'Food'),
            ('gifts', 'Gifts'),
            ('health_medical', 'Health/Medical'),
            ('home', 'Home'),
            ('transportation', 'Transportation'),
            ('personal', 'Personal'),
            ('pets', 'Pets'),
            ('utilities', 'Utilities'),
            ('travel', 'Travel'),
            ('debt', 'Debt'),
            ('other', 'Other'),
            ('custom_1', 'Custom Category 1'),
            ('custom_2', 'Custom Category 2'),
            ('custom_3', 'Custom Category 3'),
        ],
        validators=[InputRequired()]
    )
    amount = IntegerField('Amount (in currency)', validators=[InputRequired(), NumberRange(min=0)])
    currency = SelectField(
        'Currency',
        choices=[
            ('AED', 'AED (د.إ)'),
            ('INR', 'INR (₹)'),
            ('USD', 'USD ($)'),
            ('EUR', 'EUR (€)'),
            ('GBP', 'GBP (£)'),
            ('Other', 'Other')
        ],
        validators=[InputRequired()],
        default='AED'
    )
    notes = TextAreaField('Notes', validators=[DataRequired()])
    submit = SubmitField('Add Expense')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired()])
    submit = SubmitField('Register')
