from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Venta, DetalleVenta, Producto, Inventario
from datetime import date

ventas_bp = Blueprint('ventas', __name__)

# Crear una venta
@ventas_bp.route('/api/ventas', methods=['POST'])
@login_required
def crear_venta():
    if current_user.rol not in ['admin', 'supervisor']:
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    nueva_venta = Venta(
        id_cliente=data['id_cliente'],
        fecha=date.today(),
        total=0.0,
        estado='pendiente',
        id_usuario=current_user.id
    )
    db.session.add(nueva_venta)
    db.session.commit()
    return jsonify({'mensaje': 'Venta creada', 'id_venta': nueva_venta.id_venta}), 201

# Obtener todas las ventas
@ventas_bp.route('/api/ventas', methods=['GET'])
@login_required
def obtener_ventas():
    ventas = Venta.query.all()
    ventas_json = [{
        'id_venta': v.id_venta,
        'id_cliente': v.id_cliente,
        'fecha': v.fecha.strftime('%Y-%m-%d'),
        'total': v.total,
        'estado': v.estado,
        'id_usuario': v.id_usuario
    } for v in ventas]
    return jsonify(ventas_json)

# Obtener una venta por ID
@ventas_bp.route('/api/ventas/<int:id_venta>', methods=['GET'])
@login_required
def obtener_venta(id_venta):
    venta = Venta.query.get(id_venta)
    if not venta:
        return jsonify({'error': 'Venta no encontrada'}), 404
    return jsonify({
        'id_venta': venta.id_venta,
        'id_cliente': venta.id_cliente,
        'fecha': venta.fecha.strftime('%Y-%m-%d'),
        'total': venta.total,
        'estado': venta.estado,
        'id_usuario': venta.id_usuario
    })

# Actualizar una venta
@ventas_bp.route('/api/ventas/<int:id_venta>', methods=['PUT'])
@login_required
def actualizar_venta(id_venta):
    if current_user.rol not in ['admin', 'supervisor']:
        return jsonify({'error': 'No autorizado'}), 403
    
    venta = Venta.query.get(id_venta)
    if not venta:
        return jsonify({'error': 'Venta no encontrada'}), 404
    
    data = request.get_json()
    venta.estado = data.get('estado', venta.estado)
    db.session.commit()
    return jsonify({'mensaje': 'Venta actualizada'})

# Eliminar una venta
@ventas_bp.route('/api/ventas/<int:id_venta>', methods=['DELETE'])
@login_required
def eliminar_venta(id_venta):
    if current_user.rol != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    venta = Venta.query.get(id_venta)
    if not venta:
        return jsonify({'error': 'Venta no encontrada'}), 404
    
    db.session.delete(venta)
    db.session.commit()
    return jsonify({'mensaje': 'Venta eliminada'})
