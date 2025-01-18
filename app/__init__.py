from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Add the SQLite Cloud connection string
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlitecloud://cnwui0evhz.g5.sqlite.cloud:8860/my-database?apikey=ee6Lm9tAV07WnebyuftsY4g5dMYDCVxWLaneQoWScww'
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600  # Recycle connections after 3600 seconds
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Avoid tracking modifications
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'my$up3r$3cur3K3y')  # Use environment variable for the secret key

    # Initialize the database with the app
    db.init_app(app)

    # Import routes (assumes you have api_bp set up in `routes.py`)
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
