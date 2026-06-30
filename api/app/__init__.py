from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.routes import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')
    jwt = JWTManager(app)
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173/*"}}) #http://127.0.0.1:5000

    # Registrar blueprints
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
'''
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.routes import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')
    jwt = JWTManager(app)
    
    # Inicializa Flask-CORS y permite todas las solicitudes sin restricciones
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Registrar blueprints
    app.register_blueprint(api_bp, url_prefix='/api')

    return app


'''