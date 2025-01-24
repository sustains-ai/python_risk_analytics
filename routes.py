from flask import Blueprint, render_template, redirect, url_for, request, current_app,flash
from flask_login import login_user, login_required, logout_user, current_user
from create_app import mongo, login_manager, mail, s
from models import User, Portfolio,Stock
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm, PortfolioForm,StockForm
from bson import ObjectId  # For handling MongoDB ObjectId
from flask_mail import Message
from datetime import datetime


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
from bson import ObjectId

@bp.route('/dashboard')
@login_required
def dashboard():
    # Fetch all portfolios for the logged-in user
    portfolios = list(mongo.db.portfolios.find({"user_id": str(current_user.id)}))

    # Prepare portfolio data with associated stocks
    portfolio_data = []
    for portfolio in portfolios:
        portfolio["_id"] = str(portfolio["_id"])  # Convert portfolio `_id` to string

        # Convert portfolio ID to ObjectId for querying stocks
        stocks = list(mongo.db.stocks.find({"portfolio_id": ObjectId(portfolio["_id"])}))
        for stock in stocks:
            stock["_id"] = str(stock["_id"])  # Convert stock `_id` to string
            stock["portfolio_id"] = str(stock["portfolio_id"])  # Convert portfolio_id in stock to string
            if isinstance(stock["purchase_date"], datetime):
                stock["purchase_date"] = stock["purchase_date"].date()  # Convert datetime to date

        # Debugging
        print(f"Portfolio: {portfolio['name']} (ID: {portfolio['_id']})")
        print(f"Raw Stocks: {stocks}")
        portfolio_data.append({"portfolio": portfolio, "stocks": stocks})

    # Prepare data for charts (optional, if needed for analysis)
    categories = []
    amounts = []
    for data in portfolio_data:
        for stock in data["stocks"]:
            categories.append(stock["name"])
            amounts.append(stock["purchase_price"] * stock["quantity"])

    return render_template(
        "dashboard.html",
        portfolio_data=portfolio_data,
        categories=categories,
        amounts=amounts
    )


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
@bp.route('/stock/<stock_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_stock(stock_id):
    try:
        # Fetch the stock record to edit
        stock_data = mongo.db.stocks.find_one({"_id": ObjectId(stock_id)})
        if not stock_data:
            flash("Stock not found.", "danger")
            return redirect(url_for('main.dashboard'))

        # Check if the logged-in user owns the portfolio associated with the stock
        portfolio = mongo.db.portfolios.find_one({"_id": ObjectId(stock_data["portfolio_id"])})
        if not portfolio or portfolio.get("user_id") != str(current_user.id):
            flash("Unauthorized access to the stock.", "danger")
            return redirect(url_for('main.dashboard'))

        # Pre-fill the form with existing stock data
        form = StockForm(
            symbol=stock_data["symbol"],
            name=stock_data["name"],
            quantity=stock_data["quantity"],
            purchase_price=stock_data["purchase_price"],
            purchase_date=stock_data["purchase_date"],
            currency=stock_data["currency"],
            notes=stock_data["notes"]
        )

        # Update the stock record upon form submission
        if form.validate_on_submit():
            updated_stock = {
                "symbol": form.symbol.data,
                "name": form.name.data,
                "quantity": form.quantity.data,
                "purchase_price": form.purchase_price.data,
                "purchase_date": form.purchase_date.data,
                "currency": form.currency.data,
                "notes": form.notes.data,
            }
            mongo.db.stocks.update_one({"_id": ObjectId(stock_id)}, {"$set": updated_stock})
            flash("Stock updated successfully!", "success")
            return redirect(url_for('main.dashboard'))

        return render_template("edit_stock.html", form=form, stock_id=stock_id)

    except Exception as e:
        current_app.logger.error(f"Error in edit_stock route: {e}")
        flash("An error occurred while editing the stock.", "danger")
        return redirect(url_for('main.dashboard'))


@bp.route('/portfolio/<portfolio_id>/add_stock', methods=['GET', 'POST'])
@login_required
def add_stock(portfolio_id):
    form = StockForm()
    if form.validate_on_submit():
        new_stock = Stock(
            portfolio_id=portfolio_id,
            market = form.market.data,
            symbol=form.symbol.data,
            name=form.name.data,
            quantity=form.quantity.data,
            purchase_price=form.purchase_price.data,
            purchase_date=form.purchase_date.data,
            currency=form.currency.data,
            notes=form.notes.data
        )
        mongo.db.stocks.insert_one(new_stock.to_dict())
        flash("Stock added successfully!", "success")
        return redirect(url_for('main.dashboard'))
    return render_template('add_stock.html', form=form, portfolio_id=portfolio_id)
@bp.route('/add_portfolio', methods=['GET', 'POST'])
@login_required
def add_portfolio():
    form = PortfolioForm()
    if form.validate_on_submit():
        new_portfolio = {
            "user_id": str(current_user.id),
            "name": form.name.data,
            "description": form.description.data,
            "created_at": datetime.utcnow()
        }
        mongo.db.portfolios.insert_one(new_portfolio)
        flash("Portfolio added successfully!", "success")
        return redirect(url_for('main.dashboard'))

    return render_template('add_portfolio.html', form=form)
