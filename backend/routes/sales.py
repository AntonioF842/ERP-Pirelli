from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Venta, DetalleVenta, Producto, Inventario
from datetime import date

ventas_bp = Blueprint('ventas', __name__)

# Crear una venta
@ventas_bp.route('/ventas', methods=['POST'])
@login_required
def crear_venta():
    if current_user.rol not in ['admin', 'supervisor']:
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    detalles = data.get("detalles", [])
    total_venta = 0
    detalles_creados = []

    nueva_venta = Venta(
        id_cliente=data['id_cliente'],
        fecha=date.today(),
        total=0.0,  # se actualizará después
        estado=data.get('estado', 'pendiente'),
        id_usuario=current_user.id_usuario
    )
    db.session.add(nueva_venta)
    db.session.flush()  # Para obtener el id_venta antes de hacer commit

    # Procesar detalles
    for det in detalles:
        id_producto = det.get("id_producto")
        cantidad = det.get("cantidad")
        precio_unitario = float(det.get("precio_unitario"))
        subtotal = float(det.get("subtotal", cantidad * precio_unitario))

        detalle = DetalleVenta(
            id_venta=nueva_venta.id_venta,
            id_producto=id_producto,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            subtotal=subtotal
        )
        db.session.add(detalle)
        detalles_creados.append({
            "id_producto": id_producto,
            "cantidad": cantidad,
            "precio_unitario": precio_unitario,
            "subtotal": subtotal
        })
        total_venta += subtotal

    nueva_venta.total = total_venta
    db.session.commit()

    return jsonify({
        'mensaje': 'Venta creada',
        'id_venta': nueva_venta.id_venta,
        'total': float(nueva_venta.total),
        'detalles': detalles_creados
    }), 201

# Obtener todas las ventas
@ventas_bp.route('/ventas', methods=['GET'])
@login_required
def obtener_ventas():
    ventas = Venta.query.all()
    ventas_json = []
    for v in ventas:
        # Armar detalles enriquecidos
        detalles = []
        for det in v.detalles:
            producto = Producto.query.get(det.id_producto)
            detalles.append({
                'id_detalle': det.id_detalle,
                'id_venta': det.id_venta,
                'id_producto': det.id_producto,
                'cantidad': det.cantidad,
                'precio_unitario': float(det.precio_unitario),
                'subtotal': float(det.subtotal),
                'producto': {
                    'id_producto': producto.id_producto,
                    'codigo': producto.codigo,
                    'nombre': producto.nombre,
                    'precio': float(producto.precio),
                    'categoria': producto.categoria
                } if producto else None
            })
        cliente = v.cliente
        usuario = v.usuario
        ventas_json.append({
            'id_venta': v.id_venta,
            'id_cliente': v.id_cliente,
            'fecha': v.fecha.strftime('%Y-%m-%d'),
            'total': float(v.total),
            'estado': v.estado,
            'id_usuario': v.id_usuario,
            'cliente': {
                'id_cliente': cliente.id_cliente,
                'nombre': cliente.nombre
            } if cliente else None,
            'usuario': {
                'id_usuario': usuario.id_usuario,
                'nombre': usuario.nombre
            } if usuario else None,
            'detalles': detalles
        })
    return jsonify(ventas_json)

# Obtener una venta por ID
@ventas_bp.route('/ventas/<int:id_venta>', methods=['GET'])
@login_required
def obtener_venta(id_venta):
    venta = Venta.query.get(id_venta)
    if not venta:
        return jsonify({'error': 'Venta no encontrada'}), 404

    detalles = []
    for det in venta.detalles:
        producto = Producto.query.get(det.id_producto)
        detalles.append({
            'id_detalle': det.id_detalle,
            'id_venta': det.id_venta,
            'id_producto': det.id_producto,
            'cantidad': det.cantidad,
            'precio_unitario': float(det.precio_unitario),
            'subtotal': float(det.subtotal),
            'producto': {
                'id_producto': producto.id_producto,
                'codigo': producto.codigo,
                'nombre': producto.nombre,
                'precio': float(producto.precio),
                'categoria': producto.categoria
            } if producto else None
        })

    # Opcional: incluir datos extendidos de cliente y usuario
    cliente = venta.cliente
    usuario = venta.usuario
    venta_json = {
        'id_venta': venta.id_venta,
        'id_cliente': venta.id_cliente,
        'fecha': venta.fecha.strftime('%Y-%m-%d'),
        'total': float(venta.total),
        'estado': venta.estado,
        'id_usuario': venta.id_usuario,
        'cliente': {
            'id_cliente': cliente.id_cliente,
            'nombre': cliente.nombre
        } if cliente else None,
        'usuario': {
            'id_usuario': usuario.id_usuario,
            'nombre': usuario.nombre
        } if usuario else None,
        'detalles': detalles
    }
    return jsonify(venta_json)

# Actualizar una venta
@ventas_bp.route('/ventas/<int:id_venta>', methods=['PUT'])
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
@ventas_bp.route('/ventas/<int:id_venta>', methods=['DELETE'])
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
