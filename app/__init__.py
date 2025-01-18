from flask import Flask
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    CORS(app)

    # Import and register the blueprint
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
