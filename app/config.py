import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración base para la aplicación Flask"""
    
    # Configuración de Flask
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = os.getenv('DEBUG').lower() == 'true'
    TESTING = False
    
    # Configuración del servidor
    HOST = os.getenv('HOST')
    PORT = int(os.getenv('PORT'))
    
    # Configuración de Odoo
    ODOO_URL = os.getenv('ODOO_URL')
    ODOO_DB = os.getenv('ODOO_DB')
    ODOO_USERNAME = os.getenv('ODOO_USERNAME')
    ODOO_PASSWORD = os.getenv('ODOO_PASSWORD')
    
    # Configuración de CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
    
    # Configuración de logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # Configuración de seguridad
    SESSION_COOKIE_SECURE = False  # True en producción con HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configuración de API
    API_TITLE = "Odoo API"
    API_VERSION = "v1"
    API_DESCRIPTION = "API REST para integración con Odoo"


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False
    
    # Configuración específica para desarrollo
    ODOO_URL = os.getenv('ODOO_URL_DEV', Config.ODOO_URL)
    ODOO_DB = os.getenv('ODOO_DB_DEV', Config.ODOO_DB)
    
    # Logging más detallado en desarrollo
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    DEBUG = True
    
    # Usar base de datos de testing
    DATABASE_URL = 'sqlite:///:memory:'
    
    # Configuración de Odoo para testing (mock)
    ODOO_URL = 'https://test.odoo.com/'
    ODOO_DB = 'test_db'
    ODOO_USERNAME = 'test_user'
    ODOO_PASSWORD = 'test_password'


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    
    # Configuración de seguridad para producción
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Logging menos detallado en producción
    LOG_LEVEL = 'WARNING'
    
    # Configuración de rate limiting más estricta
    RATELIMIT_DEFAULT = "1000 per day;100 per hour;20 per minute"


# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Obtener configuración basada en variable de entorno"""
    config_name = os.getenv('FLASK_ENV', 'development')
    return config.get(config_name, config['default'])
