import os
from dotenv import load_dotenv
from app import create_app

# Cargar variables de entorno desde .env
load_dotenv()

def main():
    # Crear la aplicación Flask
    app = create_app()
    # Configuración del servidor
    host = os.getenv('HOST')
    port = int(os.getenv('PORT'))
    debug = os.getenv('DEBUG').lower() == 'true'
    
    print(f"Iniciando servidor Flask Odoo API...")
    print(f"Host: {host}")
    print(f"Puerto: {port}")
    print(f"Debug: {debug}")
    print(f"URL: http://{host}:{port}")
    
    try:
        # Ejecutar la aplicación
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=False  # Deshabilitar reloader para evitar problemas de threading
        )
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario")
    except Exception as e:
        print(f"Error al iniciar el servidor: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main()) 