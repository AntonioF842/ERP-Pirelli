from flask import Blueprint, request, jsonify
from models import Proveedor
from config import db

providers_bp = Blueprint('providers_bp', __name__)

@providers_bp.route('/providers', methods=['GET'])
def get_providers():
    proveedores = Proveedor.query.all()
    return jsonify([{
        'id': p.id_proveedor,
        'name': p.nombre,
        'contact': p.contacto,
        'phone': p.telefono,
        'email': p.email,
        'address': p.direccion,
        'material_type': p.tipo_material
    } for p in proveedores])

@providers_bp.route('/providers', methods=['POST'])
def create_provider():
    data = request.get_json()
    nuevo_proveedor = Proveedor(**data)
    db.session.add(nuevo_proveedor)
    db.session.commit()
    return jsonify({'message': 'Provider created successfully'}), 201

@providers_bp.route('/providers/<int:id>', methods=['PUT'])
def update_provider(id):
    proveedor = Proveedor.query.get_or_404(id)
    data = request.get_json()
    for key, value in data.items():
        setattr(proveedor, key, value)
    db.session.commit()
    return jsonify({'message': 'Provider updated successfully'})

@providers_bp.route('/providers/<int:id>', methods=['DELETE'])
def delete_provider(id):
    proveedor = Proveedor.query.get_or_404(id)
    db.session.delete(proveedor)
    db.session.commit()
    return jsonify({'message': 'Provider deleted successfully'})
