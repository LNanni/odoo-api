from flask import Flask
from flask_cors import CORS
from app.config import get_config

def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    CORS(app)

    register_blueprints(app)

    return app

def register_blueprints(app):
    # Importar blueprints
    from app.routes.partners_routes import bp as partners_bp
    
    # Registrar blueprints
    app.register_blueprint(partners_bp)