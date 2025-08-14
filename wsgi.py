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
    host = os.getenv('HOST')
    port = int(os.getenv('PORT'))
    
    app.run(
        host=host,
        port=port,
        debug=False
    ) 