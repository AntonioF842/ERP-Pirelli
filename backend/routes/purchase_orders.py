from flask import Blueprint, jsonify, request
from models import OrdenCompra, Proveedor, Usuario, DetalleOrdenCompra, db
from datetime import datetime

purchase_orders_bp = Blueprint('purchase_orders', __name__)

@purchase_orders_bp.route('/purchase_orders', methods=['GET'])
def get_purchase_orders():
    orders = OrdenCompra.query.all()
    return jsonify([{
        'id_orden_compra': order.id_orden_compra,
        'id_proveedor': order.id_proveedor,
        'proveedor_name': order.proveedor.nombre,
        'id_usuario': order.id_usuario,
        'usuario_name': order.usuario.nombre,
        'fecha': order.fecha.isoformat(),
        'fecha_entrega_esperada': order.fecha_entrega_esperada.isoformat() if order.fecha_entrega_esperada else None,
        'estado': order.estado,
        'total': float(order.total) if order.total else None,
        'detalles': [{
            'id_detalle': det.id_detalle,
            'id_material': det.id_material,
            'material_name': det.material.nombre,
            'cantidad': det.cantidad,
            'precio_unitario': float(det.precio_unitario) if det.precio_unitario else None,
            'subtotal': float(det.subtotal) if det.subtotal else None
        } for det in order.detalles]
    } for order in orders])

@purchase_orders_bp.route('/purchase_orders', methods=['POST'])
def create_purchase_order():
    data = request.get_json()
    new_order = OrdenCompra(
        id_proveedor=data['id_proveedor'],
        id_usuario=data['id_usuario'],
        fecha=datetime.strptime(data['fecha'], '%Y-%m-%d').date(),
        fecha_entrega_esperada=datetime.strptime(data['fecha_entrega_esperada'], '%Y-%m-%d').date() if 'fecha_entrega_esperada' in data else None,
        estado=data.get('estado', 'pendiente'),
        total=data.get('total')
    )
    db.session.add(new_order)
    db.session.commit()
    
    # Add order details if provided
    if 'detalles' in data:
        for detalle in data['detalles']:
            new_detalle = DetalleOrdenCompra(
                id_orden_compra=new_order.id_orden_compra,
                id_material=detalle['id_material'],
                cantidad=detalle['cantidad'],
                precio_unitario=detalle.get('precio_unitario'),
                subtotal=detalle.get('subtotal')
            )
            db.session.add(new_detalle)
        db.session.commit()
    
    return jsonify({'message': 'Purchase order created successfully', 'id_orden_compra': new_order.id_orden_compra}), 201

@purchase_orders_bp.route('/purchase_orders/<int:id>', methods=['PUT'])
def update_purchase_order(id):
    order = OrdenCompra.query.get_or_404(id)
    data = request.get_json()
    order.id_proveedor = data.get('id_proveedor', order.id_proveedor)
    order.id_usuario = data.get('id_usuario', order.id_usuario)
    if 'fecha' in data:
        order.fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
    if 'fecha_entrega_esperada' in data:
        order.fecha_entrega_esperada = datetime.strptime(data['fecha_entrega_esperada'], '%Y-%m-%d').date()
    order.estado = data.get('estado', order.estado)
    order.total = data.get('total', order.total)
    db.session.commit()
    return jsonify({'message': 'Purchase order updated successfully'})

@purchase_orders_bp.route('/purchase_orders/<int:id>', methods=['DELETE'])
def delete_purchase_order(id):
    order = OrdenCompra.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({'message': 'Purchase order deleted successfully'})