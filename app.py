import os
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import FinanceDataForm, LoginForm  # Assuming these forms are in forms.py

# Initialize the app and configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Define User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    default_currency = db.Column(db.String(10), default='AED')

    def __repr__(self):
        return f'<User {self.email}>'


# Define FinanceData model
class FinanceData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False, default='AED')
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<FinanceData {self.id}>'


# Flask-Login user_loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Home Route
@app.route('/')
def index():
    some_data = "Welcome to Sustains.ai!"  # Example static data, replace with dynamic data as needed
    return render_template('index.html', data=some_data)  # Pass 'some_data' to the template


# Form Route
@app.route('/form', methods=['GET', 'POST'])
@login_required
def form():
    form = FinanceDataForm()  # Assuming you're using FinanceDataForm for finance data entry
    if form.validate_on_submit():
        new_data = FinanceData(
            user_id=current_user.id,
            date=form.date.data,
            category=form.category.data,
            amount=form.amount.data,
            currency=form.currency.data,
            notes=form.notes.data
        )
        db.session.add(new_data)
        db.session.commit()
        return redirect(url_for('dashboard'))  # Redirect to the dashboard after submitting
    return render_template('form.html', form=form)  # Render the form page


# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = LoginForm()  # Assuming you're using the LoginForm for registration
    if form.validate_on_submit():
        # Hash the password and create a new user
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(email=form.email.data, password=hashed_password)

        # Check if the user already exists
        if User.query.filter_by(email=form.email.data).first():
            return 'User already exists'  # You can redirect to an error page here

        # Add the new user to the database and commit the transaction
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))  # After registration, redirect to login page

    return render_template('register.html', form=form)  # Render the registration page with the form


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        return 'Invalid credentials'
    return render_template('login.html', form=form)


# Dashboard Route (protected by login)
@app.route('/dashboard')
@login_required
def dashboard():
    # Fetch finance data for the logged-in user
    all_data = FinanceData.query.filter_by(user_id=current_user.id).all()

    # Check if there's any finance data
    if not all_data:
        all_data = []  # Make sure 'all_data' is not None, but an empty list if no data found

    # Prepare data for the template
    dates = [data.date.strftime("%Y-%m-%d") for data in all_data]
    categories = [data.category for data in all_data]
    amounts = [data.amount for data in all_data]
    currencies = [data.currency for data in all_data]
    notes = [data.notes for data in all_data]

    # Pass variables to the template
    return render_template(
        'dashboard.html',
        dates=dates,
        categories=categories,
        amounts=amounts,
        currencies=currencies,
        notes=notes,
        all_data=all_data  # Pass 'all_data' to the template
    )


# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
