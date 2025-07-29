from flask import Flask
from flask_cors import CORS
from app.config import get_config

def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    CORS(app)

    return app