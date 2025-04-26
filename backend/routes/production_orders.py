from flask import Blueprint, jsonify, request
from models import OrdenProduccion, Producto, Usuario, db
from datetime import datetime

production_orders_bp = Blueprint('production_orders', __name__)

@production_orders_bp.route('/production_orders', methods=['GET'])
def get_production_orders():
    orders = OrdenProduccion.query.all()
    return jsonify([{
        'id_orden_produccion': order.id_orden_produccion,
        'id_producto': order.id_producto,
        'producto_name': order.producto.nombre,
        'cantidad': order.cantidad,
        'fecha_inicio': order.fecha_inicio.isoformat(),
        'fecha_fin': order.fecha_fin.isoformat() if order.fecha_fin else None,
        'estado': order.estado,
        'id_usuario': order.id_usuario,
        'usuario_name': order.usuario.nombre
    } for order in orders])

@production_orders_bp.route('/production_orders', methods=['POST'])
def create_production_order():
    data = request.get_json()
    new_order = OrdenProduccion(
        id_producto=data['id_producto'],
        cantidad=data['cantidad'],
        fecha_inicio=datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date(),
        fecha_fin=datetime.strptime(data['fecha_fin'], '%Y-%m-%d').date() if 'fecha_fin' in data else None,
        estado=data.get('estado', 'planificada'),
        id_usuario=data['id_usuario']
    )
    db.session.add(new_order)
    db.session.commit()
    return jsonify({'message': 'Production order created successfully'}), 201

@production_orders_bp.route('/production_orders/<int:id>', methods=['PUT'])
def update_production_order(id):
    order = OrdenProduccion.query.get_or_404(id)
    data = request.get_json()
    order.id_producto = data.get('id_producto', order.id_producto)
    order.cantidad = data.get('cantidad', order.cantidad)
    if 'fecha_inicio' in data:
        order.fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date()
    if 'fecha_fin' in data:
        order.fecha_fin = datetime.strptime(data['fecha_fin'], '%Y-%m-%d').date()
    order.estado = data.get('estado', order.estado)
    order.id_usuario = data.get('id_usuario', order.id_usuario)
    db.session.commit()
    return jsonify({'message': 'Production order updated successfully'})

@production_orders_bp.route('/production_orders/<int:id>', methods=['DELETE'])
def delete_production_order(id):
    order = OrdenProduccion.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({'message': 'Production order deleted successfully'})