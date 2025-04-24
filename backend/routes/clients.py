from flask import Blueprint, jsonify
from flask_login import login_required
from models import Cliente

clients_bp = Blueprint('clients_bp', __name__)

@clients_bp.route('/clientes', methods=['GET'])
@login_required
def get_clients():
    clientes = Cliente.query.all()
    clientes_list = []
    for c in clientes:
        clientes_list.append({
            "id_cliente": c.id_cliente,
            "nombre": c.nombre,
            "contacto": c.contacto,
            "telefono": c.telefono,
            "email": c.email,
            "direccion": c.direccion,
            "tipo": c.tipo
        })
    return jsonify(clientes_list)