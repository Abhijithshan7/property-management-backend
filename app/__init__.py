from flask import Flask
from app.db import init_db
from app.routes import api_blueprint

def create_app():
    app = Flask(__name__)
    
    # Register Blueprints
    app.register_blueprint(api_blueprint)

    # Init DB (optional setup)
    init_db()

    return app
