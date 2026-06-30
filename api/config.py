# Configuración general de la aplicación Flask
SECRET_KEY = 'tu_clave_secreta'  # Clave secreta para sesiones y CSRF
JWT_SECRET_KEY = 'your_jwt_secret_key'

# Configuración de la base de datos (si es necesario)
# SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'  # Ejemplo para SQLite

# Configuraciones adicionales según tus necesidades

# Configuración de CORS (si es necesario)
# CORS_HEADERS = 'Content-Type'

# Configuración para activar o desactivar el modo de depuración
DEBUG = True  # Cambiar a False en producción