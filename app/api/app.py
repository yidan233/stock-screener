from flask import Flask
from flask_cors import CORS
import logging

def create_app():
    app = Flask(__name__)
    CORS(app)
    logging.basicConfig(level=logging.INFO)
    
    # Register routes
    from app.api.routes import register_routes
    register_routes(app)
    
    return app

app = create_app()