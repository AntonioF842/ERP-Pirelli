# backend/main.py
from config import create_app, db
from routes.auth import auth_bp
from routes.products import products_bp
from routes.sales import ventas_bp
from routes.clients import clients_bp
from routes.employees import employees_bp
from routes.attendance import attendance_bp
from routes.providers import providers_bp
from routes.materials import materials_bp
from routes.inventory import inventory_bp
from routes.purchase_orders import purchase_orders_bp
from routes.production_orders import production_orders_bp
from routes.production_recipes import production_recipes_bp
from routes.work_areas import work_areas_bp
from routes.suppliers import suppliers_bp
from routes.quality_control import quality_control_bp
from routes.payroll import payroll_bp
from routes.r_d_projects import r_d_projects_bp
from routes.legal_regulations import legal_regulations_bp
from routes.incidents import incidents_bp
from routes.production_assets import production_assets_bp
from routes.maintenance import maintenance_bp
from routes.system_configuration import system_configuration_bp
from routes.users import users_bp
from routes.dashboard import dashboard_bp
from flask_cors import CORS

app = create_app()
CORS(app)

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(products_bp, url_prefix='/api')
app.register_blueprint(ventas_bp, url_prefix='/api')
app.register_blueprint(clients_bp, url_prefix='/api')
app.register_blueprint(employees_bp, url_prefix='/api')
app.register_blueprint(attendance_bp, url_prefix='/api')
app.register_blueprint(providers_bp, url_prefix='/api')
app.register_blueprint(materials_bp, url_prefix='/api')
app.register_blueprint(inventory_bp, url_prefix='/api')
app.register_blueprint(purchase_orders_bp, url_prefix='/api')
app.register_blueprint(production_orders_bp, url_prefix='/api')
app.register_blueprint(production_recipes_bp, url_prefix='/api')
app.register_blueprint(work_areas_bp, url_prefix='/api')
app.register_blueprint(suppliers_bp, url_prefix='/api')
app.register_blueprint(quality_control_bp, url_prefix='/api')
app.register_blueprint(payroll_bp, url_prefix='/api')
app.register_blueprint(r_d_projects_bp, url_prefix='/api')
app.register_blueprint(legal_regulations_bp, url_prefix='/api')
app.register_blueprint(incidents_bp, url_prefix='/api')
app.register_blueprint(production_assets_bp, url_prefix='/api')
app.register_blueprint(maintenance_bp, url_prefix='/api')
app.register_blueprint(system_configuration_bp, url_prefix='/api')
app.register_blueprint(users_bp, url_prefix='/api')
app.register_blueprint(dashboard_bp, url_prefix='/api')

# Crear tablas en la base de datos
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
