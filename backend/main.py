# backend/main.py
from config import create_app, db
from routes.auth import auth_bp
from routes.products import products_bp
from routes.sales import ventas_bp
from routes.users import users_bp
from flask_cors import CORS

app = create_app()
CORS(app)

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(products_bp, url_prefix='/api')
app.register_blueprint(ventas_bp, url_prefix='/api')
app.register_blueprint(users_bp, url_prefix='/api')

# Crear tablas en la base de datos
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)