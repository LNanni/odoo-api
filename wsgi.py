#!/usr/bin/env python3
"""
WSGI entry point para despliegue en producción
"""
import os
from dotenv import load_dotenv
from app import create_app

# Cargar variables de entorno
load_dotenv()

# Crear la aplicación Flask
app = create_app()

if __name__ == '__main__':
    # Configuración para producción
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    app.run(
        host=host,
        port=port,
        debug=False
    ) 