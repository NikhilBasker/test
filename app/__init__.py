from flask import Flask
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'my$up3r$3cur3K3y')
    CORS(app)

    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
