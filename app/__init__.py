from flask import Flask
from flask_cors import CORS
from app.db import init_db
from app.routes import api_blueprint

def create_app():
    app = Flask(__name__)
    
    # Configure CORS to allow requests from both localhost and 127.0.0.1
    cors_options = {
        'origins': ['http://localhost:3000', 'http://127.0.0.1:3000'],
        'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        'allow_headers': ['Content-Type', 'Authorization', 'X-Requested-With'],
        'supports_credentials': True,
        'max_age': 600
    }
    CORS(app, **cors_options)
    
    # Register Blueprints
    app.register_blueprint(api_blueprint)

    # Init DB (optional setup)
    init_db()

    return app
