from flask import Flask
from flask_mail import Mail
from flask_pymongo import PyMongo
from flask_login import LoginManager
import os
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv

mongo = PyMongo()  # Initialize MongoDB
login_manager = LoginManager()

# Initialize Flask-Mail
mail = Mail()
s = URLSafeTimedSerializer(os.environ.get("SECRET_KEY", "your_secret_key"))  # Ensure SECRET_KEY is stored securely


def create_app():
    app = Flask(__name__)


    app.config['MAIL_USERNAME'] = os.getenv('SES_SMTP_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('SES_SMTP_PASSWORD')

    # Confirm they are set (for debugging, remove in production)
    print(f"SES SMTP Username: {os.environ.get('SES_SMTP_USERNAME')}")
    print(f"SES SMTP Password: {'*' * len(os.environ.get('SES_SMTP_PASSWORD', ''))}")
    # App Secret Key
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "your_secret_key")

    # MongoDB URI Configuration
    app.config['MONGO_URI'] = os.getenv(
        'MONGO_URI',
        'mongodb+srv://arjuncrevathi:Arjun_1987@serverlessinstance0.ppr5qpz.mongodb.net/wealth_ledger?retryWrites=true&w=majority&appName=ServerlessInstance0'
    )

    # Amazon SES SMTP configuration
    app.config['MAIL_SERVER'] = 'email-smtp.ap-southeast-2.amazonaws.com'  # Correct region
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('SES_SMTP_USERNAME')  # SMTP username from environment variable
    app.config['MAIL_PASSWORD'] = os.getenv('SES_SMTP_PASSWORD')  # SMTP password from environment variable
    app.config['MAIL_DEFAULT_SENDER'] = 'arjun@sustains.ai'  # Use verified email address

    # Initialize extensions
    mongo.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Set login view
    login_manager.login_view = "main.login"

    # Register blueprints
    from routes import bp
    app.register_blueprint(bp)

    return app
