from flask import Blueprint, render_template, redirect, url_for, request, current_app,flash
from flask_login import login_user, login_required, logout_user, current_user
from create_app import mongo, login_manager, mail, s
from models import User, FinanceData
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm, FinanceDataForm
from bson import ObjectId  # For handling MongoDB ObjectId
from flask_mail import Message

bp = Blueprint('main', __name__)


# Flask-Login user_loader function
@login_manager.user_loader
def load_user(user_id):
    try:
        user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        return User.from_dict(user_data) if user_data else None
    except Exception as e:
        current_app.logger.error(f"Error loading user: {e}")
        return None


# Home Route
@bp.route('/')
def index():
    return render_template('index.html')


# Register Route
@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if email is already registered
        existing_user = mongo.db.users.find_one({"email": form.email.data})
        if existing_user:
            return "Email already registered. Please log in or use a different email.", 400

        # Check if the passwords match
        if form.password.data != form.confirm_password.data:
            return "Passwords do not match.", 400

        # Save the new user to the database
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = {
            "email": form.email.data,
            "password": hashed_password,
            "default_currency": "AED",
            "confirmed": False  # Add a "confirmed" field to track email confirmation status
        }
        mongo.db.users.insert_one(new_user)

        # Send the confirmation email
        send_confirmation_email(form.email.data)

        # Redirect the user to login page after sending the email
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)


# Login Route
@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        current_app.logger.debug(f"Attempting login for email: {email}")

        # Fetch user data from MongoDB
        user_data = mongo.db.users.find_one({"email": email})
        if user_data:
            current_app.logger.debug(f"User found: {user_data}")

            # Check if the password is correct
            if check_password_hash(user_data["password"], password):

                # Check if email is confirmed
                if not user_data.get('confirmed', False):
                    current_app.logger.warning("Email not confirmed")
                    flash("Please confirm your email address first.", "warning")
                    return redirect(url_for('main.login'))

                # Log in the user
                user = User.from_dict(user_data)
                user.id = str(user_data["_id"])  # Assign ObjectId to the user
                login_user(user)
                flash("Login successful!", "success")
                return redirect(url_for('main.dashboard'))

            # Invalid password
            current_app.logger.warning("Invalid password")
            flash("Invalid email or password. Please try again.", "danger")
        else:
            # User not found
            current_app.logger.warning("User not found")
            flash("Invalid email or password. Please try again.", "danger")
        return redirect(url_for('main.login'))

    # Render login form
    return render_template('login.html', form=form)


# Email Confirmation Route
@bp.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        # Load the email from the token, which expires in 1 hour
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except Exception as e:
        # Token is invalid or expired
        return "The confirmation link is invalid or has expired.", 400

    # Find the user in the database by their email
    user = mongo.db.users.find_one({"email": email})
    if user and not user.get('confirmed', False):
        # Mark the user as confirmed in the database
        mongo.db.users.update_one({"email": email}, {"$set": {"confirmed": True}})
        return redirect(url_for('main.login'))  # Redirect to the login page
    return "Account already confirmed or invalid user.", 400


# Function to send the confirmation email
def send_confirmation_email(user_email):
    # Generate a confirmation token
    token = s.dumps(user_email, salt='email-confirm')  # Create a token with a salt
    msg = Message('Confirm Your Email', recipients=[user_email])  # Create the email message
    link = url_for('main.confirm_email', token=token, _external=True)  # Generate the confirmation URL

    # Email content
    msg.body = f'Please confirm your email address by clicking on the following link: {link}'
    try:
        # Send the email using Flask-Mail (SES)
        mail.send(msg)
        current_app.logger.info(f"Confirmation email sent to {user_email}")
    except Exception as e:
        current_app.logger.error(f"Failed to send confirmation email: {str(e)}")


# Dashboard Route
@bp.route('/dashboard')
@login_required
def dashboard():
    all_data = list(mongo.db.finance_data.find({"user_id": str(current_user.id)}))
    categories = [data["category"] for data in all_data] if all_data else []
    amounts = [data["amount"] for data in all_data] if all_data else []

    return render_template('dashboard.html', all_data=all_data, categories=categories, amounts=amounts)


# Logout Route
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


# Unauthorized Access Route
@bp.route('/unauthorized')
def unauthorized():
    return render_template('unauthorized.html'), 401


# Debug Route
@bp.route('/debug')
def debug():
    data = list(mongo.db.finance_data.find())
    if not data:
        return "No data found in FinanceData collection."
    return "<br>".join(
        [f"{d['_id']}, {d['user_id']}, {d['date']}, {d['category']}, {d['amount']}, {d['currency']}, {d['notes']}" for d
         in data])


# Edit Route for FinanceData
@bp.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    # Fetch the expense record to edit
    expense_data = mongo.db.finance_data.find_one({"_id": ObjectId(id)})
    if not expense_data:
        return "Record not found", 404

    # Check if the logged-in user is the owner of this record
    if expense_data["user_id"] != str(current_user.id):
        return redirect(url_for('main.dashboard'))

    # Create the form and pre-fill it with existing data
    expense = FinanceData.from_dict(expense_data)
    form = FinanceDataForm(obj=expense)

    if form.validate_on_submit():
        updated_data = {
            "date": form.date.data,
            "category": form.category.data,
            "amount": form.amount.data,
            "currency": form.currency.data,
            "notes": form.notes.data
        }
        mongo.db.finance_data.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
        return redirect(url_for('main.dashboard'))

    return render_template('form.html', form=form)
@bp.route('/form', methods=['GET', 'POST'])
@login_required
def form():
    form = FinanceDataForm()
    if form.validate_on_submit():
        new_data = FinanceData(
            user_id=str(current_user.id),
            date=form.date.data,
            category=form.category.data,
            amount=form.amount.data,
            currency=form.currency.data,
            notes=form.notes.data
        )
        mongo.db.finance_data.insert_one(new_data.to_dict())
        return redirect(url_for('main.dashboard'))
    return render_template('form.html', form=form)
