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
from routes.purchase_orders_details import purchase_orders_details_bp
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

# Registrar blueprints mediante una lista para mejor organización
blueprints = [
    (auth_bp, '/api'),
    (products_bp, '/api'),
    (ventas_bp, '/api'),
    (clients_bp, '/api'),
    (employees_bp, '/api'),
    (attendance_bp, '/api'),
    (providers_bp, '/api'),
    (materials_bp, '/api/materiales'),
    (inventory_bp, '/api/inventario'),
    (purchase_orders_bp, '/api/ordenes_compra'),
    (purchase_orders_details_bp, '/api/ordenes_compra_detalle'),
    (production_orders_bp, '/api'),
    (production_recipes_bp, '/api'),
    (work_areas_bp, '/api'),
    (suppliers_bp, '/api/proveedores'),
    (quality_control_bp, '/api'),
    (payroll_bp, '/api'),
    (r_d_projects_bp, '/api'),
    (legal_regulations_bp, '/api'),
    (incidents_bp, '/api'),
    (production_assets_bp, '/api'),
    (maintenance_bp, '/api'),
    (system_configuration_bp, '/api'),
    (users_bp, '/api'),
    (dashboard_bp, '/api')
]

# Registrar cada blueprint con su prefijo correspondiente
for blueprint, prefix in blueprints:
    app.register_blueprint(blueprint, url_prefix=prefix)

# Crear tablas en la base de datos
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
