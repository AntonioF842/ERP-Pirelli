from flask import Blueprint, jsonify, request
from models import Inventario, Material, db
from datetime import datetime

# El prefijo ahora será /api/inventario
inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('', methods=['GET'])
def get_inventory():
    inventory = Inventario.query.all()
    return jsonify([{
        'id_inventario': inv.id_inventario,
        'id_material': inv.id_material,
        'material_name': inv.material.nombre if inv.material else None,
        'cantidad': inv.cantidad,
        'ubicacion': inv.ubicacion,
        'lote': inv.lote,
        'fecha_ingreso': inv.fecha_ingreso.isoformat() if inv.fecha_ingreso else None
    } for inv in inventory])

@inventory_bp.route('/<int:id>', methods=['GET'])
def get_inventory_by_id(id):
    inv = Inventario.query.get_or_404(id)
    return jsonify({
        'id_inventario': inv.id_inventario,
        'id_material': inv.id_material,
        'material_name': inv.material.nombre if inv.material else None,
        'cantidad': inv.cantidad,
        'ubicacion': inv.ubicacion,
        'lote': inv.lote,
        'fecha_ingreso': inv.fecha_ingreso.isoformat() if inv.fecha_ingreso else None
    })

@inventory_bp.route('', methods=['POST'])
def create_inventory():
    data = request.get_json()
    # Input validation
    required_fields = ['id_material', 'cantidad']
    missing = [field for field in required_fields if field not in data]
    if missing:
        return jsonify({'error': f"Missing fields: {', '.join(missing)}"}), 400
    try:
        # Validate against material min/max stock levels
        material = Material.query.get_or_404(data['id_material'])
        cantidad = data['cantidad']
        
        if cantidad < material.stock_minimo:
            return jsonify({'error': f"La cantidad registrada ({cantidad}) es MENOR que el stock mínimo para este material ({material.stock_minimo})."}), 400
        if cantidad > material.stock_maximo:
            return jsonify({'error': f"La cantidad registrada ({cantidad}) es MAYOR que el stock máximo para este material ({material.stock_maximo})."}), 400
            
        new_inventory = Inventario(
            id_material=data['id_material'],
            cantidad=cantidad,
            ubicacion=data.get('ubicacion'),
            lote=data.get('lote'),
            fecha_ingreso=datetime.strptime(data['fecha_ingreso'], '%Y-%m-%d').date() if 'fecha_ingreso' in data else None
        )
        db.session.add(new_inventory)
        db.session.commit()
        return jsonify({'message': 'Inventory record created successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@inventory_bp.route('/<int:id>', methods=['PUT'])
def update_inventory(id):
    inventory = Inventario.query.get_or_404(id)
    data = request.get_json()
    
    # Get the material ID (either from request or existing inventory)
    id_material = data.get('id_material', inventory.id_material)
    cantidad = data.get('cantidad', inventory.cantidad)
    
    # Validate against material min/max stock levels
    material = Material.query.get_or_404(id_material)
    
    if cantidad < material.stock_minimo:
        return jsonify({'error': f"La cantidad registrada ({cantidad}) es MENOR que el stock mínimo para este material ({material.stock_minimo})."}), 400
    if cantidad > material.stock_maximo:
        return jsonify({'error': f"La cantidad registrada ({cantidad}) es MAYOR que el stock máximo para este material ({material.stock_maximo})."}), 400
    
    inventory.id_material = id_material
    inventory.cantidad = cantidad
    inventory.ubicacion = data.get('ubicacion', inventory.ubicacion)
    inventory.lote = data.get('lote', inventory.lote)
    if 'fecha_ingreso' in data:
        inventory.fecha_ingreso = datetime.strptime(data['fecha_ingreso'], '%Y-%m-%d').date()
    
    db.session.commit()
    return jsonify({'message': 'Inventory record updated successfully'})

@inventory_bp.route('/<int:id>', methods=['DELETE'])
def delete_inventory(id):
    inventory = Inventario.query.get_or_404(id)
    db.session.delete(inventory)
    db.session.commit()
    return jsonify({'message': 'Inventory record deleted successfully'})
