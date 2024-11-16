from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_user, login_required, logout_user, current_user
from models import User, FinanceData, db  # Don't forget to import db from models
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, FinanceDataForm

bp = Blueprint('main', __name__)

# Flask-Login user_loader function
from create_app import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home Route
@bp.route('/')
def index():
    return render_template('index.html')

# Form Route
@bp.route('/form', methods=['GET', 'POST'])
@login_required
def form():
    form = FinanceDataForm()
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
        return redirect(url_for('main.dashboard'))  # Correct usage with blueprint
    return render_template('form.html', form=form)

# Register Route
@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = LoginForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('main.login'))  # Correct usage with blueprint
    return render_template('register.html', form=form)

# Login Route
@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))  # Correct usage with blueprint
        return 'Invalid credentials'
    return render_template('login.html', form=form)

# Dashboard Route
@bp.route('/dashboard')
@login_required
def dashboard():
    all_data = FinanceData.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', all_data=all_data)

# Logout Route
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))  # Correct usage with blueprint

# Unauthorized Access Route
@bp.route('/unauthorized')
def unauthorized():
    return render_template('unauthorized.html'), 401
