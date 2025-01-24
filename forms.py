from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, DateField, SelectField, TextAreaField, PasswordField,FloatField
from wtforms.validators import InputRequired, NumberRange, DataRequired, Email, EqualTo, Optional, Length

class PortfolioForm(FlaskForm):
    name = StringField('Portfolio Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Portfolio Description', validators=[Length(max=500)])
    submit = SubmitField('Create Portfolio')


class StockForm(FlaskForm):
    market = SelectField(
        'Market/Country',
        choices=[
            ('US', 'United States'),
            ('IN', 'India'),
            ('AE', 'United Arab Emirates'),
            ('EU', 'European Union'),
            ('UK', 'United Kingdom'),
            ('JP', 'Japan'),
            ('CN', 'China'),
            ('Other', 'Other')
        ],
        validators=[DataRequired()],
        default='US'
    )
    symbol = StringField('Stock Symbol', validators=[DataRequired(), Length(max=10)])
    name = StringField('Stock Name', validators=[DataRequired(), Length(max=100)])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    purchase_price = FloatField('Purchase Price', validators=[DataRequired(), NumberRange(min=0)])
    purchase_date = DateField('Purchase Date', format='%Y-%m-%d', validators=[DataRequired()])
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
        validators=[DataRequired()],
        default='USD'
    )
    notes = TextAreaField('Notes', validators=[Length(max=200)])
    submit = SubmitField('Add Stock')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')


class EditProfileForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password', message='Passwords must match')])
    default_currency = SelectField(
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
    submit = SubmitField('Update Profile')
