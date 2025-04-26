from flask import Blueprint, jsonify, request
from models import Inventario, Material, db
from datetime import datetime

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/inventory', methods=['GET'])
def get_inventory():
    inventory = Inventario.query.all()
    return jsonify([{
        'id_inventario': inv.id_inventario,
        'id_material': inv.id_material,
        'material_name': inv.material.nombre,
        'cantidad': inv.cantidad,
        'ubicacion': inv.ubicacion,
        'lote': inv.lote,
        'fecha_ingreso': inv.fecha_ingreso.isoformat() if inv.fecha_ingreso else None
    } for inv in inventory])

@inventory_bp.route('/inventory', methods=['POST'])
def create_inventory():
    data = request.get_json()
    new_inventory = Inventario(
        id_material=data['id_material'],
        cantidad=data['cantidad'],
        ubicacion=data.get('ubicacion'),
        lote=data.get('lote'),
        fecha_ingreso=datetime.strptime(data['fecha_ingreso'], '%Y-%m-%d').date() if 'fecha_ingreso' in data else None
    )
    db.session.add(new_inventory)
    db.session.commit()
    return jsonify({'message': 'Inventory record created successfully'}), 201

@inventory_bp.route('/inventory/<int:id>', methods=['PUT'])
def update_inventory(id):
    inventory = Inventario.query.get_or_404(id)
    data = request.get_json()
    inventory.id_material = data.get('id_material', inventory.id_material)
    inventory.cantidad = data.get('cantidad', inventory.cantidad)
    inventory.ubicacion = data.get('ubicacion', inventory.ubicacion)
    inventory.lote = data.get('lote', inventory.lote)
    if 'fecha_ingreso' in data:
        inventory.fecha_ingreso = datetime.strptime(data['fecha_ingreso'], '%Y-%m-%d').date()
    db.session.commit()
    return jsonify({'message': 'Inventory record updated successfully'})

@inventory_bp.route('/inventory/<int:id>', methods=['DELETE'])
def delete_inventory(id):
    inventory = Inventario.query.get_or_404(id)
    db.session.delete(inventory)
    db.session.commit()
    return jsonify({'message': 'Inventory record deleted successfully'})