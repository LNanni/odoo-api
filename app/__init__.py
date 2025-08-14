from flask import Flask, request
from flask_cors import CORS
from app.config import get_config
import logging


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    CORS(app)

    register_blueprints(app)

    # Configuración de logs
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    @app.before_request
    def log_request_info():
        logging.info(
            f"Request: {request.remote_addr} {request.method} {request.path}"
        )

    @app.after_request
    def log_response_info(response):
        logging.info(
            f"Response: {request.method} {request.path} -> {response.status}"
        )
        return response

    return app

def register_blueprints(app):
    # Importar blueprints
    from app.routes.partnersController import bp as partners_bp
    from app.routes.invoicesController import bp as invoices_bp
    from app.routes.transactionController import bp as transaction_bp
    
    # Registrar blueprints
    app.register_blueprint(partners_bp)
    app.register_blueprint(invoices_bp)
    app.register_blueprint(transaction_bp)