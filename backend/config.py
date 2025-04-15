# backend/config.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Antogarmex1@localhost/erp_pirelli'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'clave_secreta'

    # Inicialización de las extensiones
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_bp.login'  # Ruta de inicio de sesión

    return app
