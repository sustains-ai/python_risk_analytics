import os
from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager

mongo = PyMongo()  # Initialize MongoDB
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = 'your_secret_key'

    app.config['MONGO_URI'] = os.getenv(
        'MONGO_URI',
        'mongodb+srv://arjuncrevathi:Arjun_1987@serverlessinstance0.ppr5qpz.mongodb.net/wealth_ledger?retryWrites=true&w=majority&appName=ServerlessInstance0'
    )

    # Initialize extensions
    mongo.init_app(app)
    login_manager.init_app(app)

    # Set login view
    login_manager.login_view = "main.login"

    # Register blueprints
    from routes import bp
    app.register_blueprint(bp)

    return app
