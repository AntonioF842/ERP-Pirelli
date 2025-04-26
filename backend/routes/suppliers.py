from flask import Blueprint, jsonify, request
from models import Proveedor, db

suppliers_bp = Blueprint('suppliers', __name__)

@suppliers_bp.route('/suppliers', methods=['GET'])
def get_suppliers():
    suppliers = Proveedor.query.all()
    return jsonify([{
        'id_proveedor': sup.id_proveedor,
        'nombre': sup.nombre,
        'contacto': sup.contacto,
        'telefono': sup.telefono,
        'email': sup.email,
        'direccion': sup.direccion,
        'tipo_material': sup.tipo_material
    } for sup in suppliers])

@suppliers_bp.route('/suppliers', methods=['POST'])
def create_supplier():
    data = request.get_json()
    new_supplier = Proveedor(
        nombre=data['nombre'],
        contacto=data.get('contacto'),
        telefono=data.get('telefono'),
        email=data.get('email'),
        direccion=data.get('direccion'),
        tipo_material=data['tipo_material']
    )
    db.session.add(new_supplier)
    db.session.commit()
    return jsonify({'message': 'Supplier created successfully'}), 201

@suppliers_bp.route('/suppliers/<int:id>', methods=['PUT'])
def update_supplier(id):
    supplier = Proveedor.query.get_or_404(id)
    data = request.get_json()
    supplier.nombre = data.get('nombre', supplier.nombre)
    supplier.contacto = data.get('contacto', supplier.contacto)
    supplier.telefono = data.get('telefono', supplier.telefono)
    supplier.email = data.get('email', supplier.email)
    supplier.direccion = data.get('direccion', supplier.direccion)
    supplier.tipo_material = data.get('tipo_material', supplier.tipo_material)
    db.session.commit()
    return jsonify({'message': 'Supplier updated successfully'})

@suppliers_bp.route('/suppliers/<int:id>', methods=['DELETE'])
def delete_supplier(id):
    supplier = Proveedor.query.get_or_404(id)
    db.session.delete(supplier)
    db.session.commit()
    return jsonify({'message': 'Supplier deleted successfully'})