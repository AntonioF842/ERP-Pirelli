from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Venta, DetalleVenta, Producto, Inventario, Cliente
from datetime import date
from routes.auth import role_required

ventas_bp = Blueprint('ventas', __name__)

# Crear una venta
@ventas_bp.route('/ventas', methods=['POST'])
@login_required
def crear_venta():
    # Solo admin, supervisor y empleados de ventas pueden crear
    if current_user.rol not in ['admin', 'supervisor', 'empleado']:
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    
    # Validar cliente
    cliente = Cliente.query.get(data['id_cliente'])
    if not cliente:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    
    # Empleados solo pueden vender a clientes minoristas
    if current_user.rol == 'empleado' and cliente.tipo != 'minorista':
        return jsonify({'error': 'Solo puede vender a clientes minoristas'}), 403
    
    detalles = data.get("detalles", [])
    if not detalles:
        return jsonify({'error': 'Debe incluir al menos un producto'}), 400
    
    total_venta = 0
    detalles_creados = []

    nueva_venta = Venta(
        id_cliente=data['id_cliente'],
        fecha=date.today(),
        total=0.0,
        estado='pendiente',
        id_usuario=current_user.id_usuario
    )
    db.session.add(nueva_venta)
    db.session.flush()

    # Procesar detalles y validar inventario
    for det in detalles:
        producto = Producto.query.get(det.get("id_producto"))
        if not producto:
            db.session.rollback()
            return jsonify({'error': f'Producto {det.get("id_producto")} no encontrado'}), 404
        
        cantidad = det.get("cantidad")
        if cantidad <= 0:
            db.session.rollback()
            return jsonify({'error': 'Cantidad debe ser mayor a 0'}), 400
        
        # Verificar inventario (solo para empleados)
        if current_user.rol == 'empleado':
            inventario = Inventario.query.filter_by(id_producto=producto.id_producto).first()
            if not inventario or inventario.cantidad < cantidad:
                db.session.rollback()
                return jsonify({'error': f'No hay suficiente stock para {producto.nombre}'}), 400

        precio_unitario = float(det.get("precio_unitario", producto.precio))
        subtotal = cantidad * precio_unitario

        detalle = DetalleVenta(
            id_venta=nueva_venta.id_venta,
            id_producto=producto.id_producto,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            subtotal=subtotal
        )
        db.session.add(detalle)
        detalles_creados.append({
            "id_producto": producto.id_producto,
            "nombre_producto": producto.nombre,
            "cantidad": cantidad,
            "precio_unitario": precio_unitario,
            "subtotal": subtotal
        })
        total_venta += subtotal

        # Actualizar inventario (solo para empleados)
        if current_user.rol == 'empleado':
            inventario.cantidad -= cantidad

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
    # Admin ve todo, supervisor ve las de su área, empleados solo las propias
    if current_user.rol == 'admin':
        ventas = Venta.query.all()
    elif current_user.rol == 'supervisor':
        ventas = Venta.query.join(Cliente).filter(
            Cliente.tipo.in_(['minorista', 'distribuidor'])
        ).all()
    else:  # empleado
        ventas = Venta.query.filter_by(id_usuario=current_user.id_usuario).all()

    ventas_json = []
    for v in ventas:
        detalles = []
        for det in v.detalles:
            producto = Producto.query.get(det.id_producto)
            detalles.append({
                'id_detalle': det.id_detalle,
                'id_producto': det.id_producto,
                'nombre_producto': producto.nombre if producto else 'Desconocido',
                'cantidad': det.cantidad,
                'precio_unitario': float(det.precio_unitario),
                'subtotal': float(det.subtotal)
            })

        ventas_json.append({
            'id_venta': v.id_venta,
            'fecha': v.fecha.strftime('%Y-%m-%d'),
            'total': float(v.total),
            'estado': v.estado,
            'cliente': {
                'id_cliente': v.cliente.id_cliente,
                'nombre': v.cliente.nombre,
                'tipo': v.cliente.tipo
            } if v.cliente else None,
            'detalles': detalles
        })
    return jsonify(ventas_json)

# Obtener una venta por ID
@ventas_bp.route('/ventas/<int:id_venta>', methods=['GET'])
@login_required
def obtener_venta(id_venta):
    venta = Venta.query.get_or_404(id_venta)
    
    # Control de acceso
    if current_user.rol == 'empleado' and venta.id_usuario != current_user.id_usuario:
        return jsonify({'error': 'No autorizado'}), 403
    elif current_user.rol == 'supervisor' and venta.cliente.tipo not in ['minorista', 'distribuidor']:
        return jsonify({'error': 'No autorizado'}), 403

    detalles = []
    for det in venta.detalles:
        producto = Producto.query.get(det.id_producto)
        detalles.append({
            'id_detalle': det.id_detalle,
            'id_producto': det.id_producto,
            'nombre_producto': producto.nombre if producto else 'Desconocido',
            'cantidad': det.cantidad,
            'precio_unitario': float(det.precio_unitario),
            'subtotal': float(det.subtotal)
        })

    venta_json = {
        'id_venta': venta.id_venta,
        'fecha': venta.fecha.strftime('%Y-%m-%d'),
        'total': float(venta.total),
        'estado': venta.estado,
        'cliente': {
            'id_cliente': venta.cliente.id_cliente,
            'nombre': venta.cliente.nombre,
            'tipo': venta.cliente.tipo
        } if venta.cliente else None,
        'vendedor': venta.usuario.nombre if venta.usuario else 'Desconocido',
        'detalles': detalles
    }
    return jsonify(venta_json)

# Actualizar estado de una venta
@ventas_bp.route('/ventas/<int:id_venta>', methods=['PUT'])
@role_required('admin', 'supervisor')  # Solo admin y supervisor pueden actualizar
def actualizar_venta(id_venta):
    venta = Venta.query.get_or_404(id_venta)
    data = request.get_json()
    
    # Validar nuevo estado
    nuevo_estado = data.get('estado')
    if nuevo_estado not in ['pendiente', 'completada', 'cancelada']:
        return jsonify({'error': 'Estado no válido'}), 400
    
    # Solo admin puede cancelar ventas
    if nuevo_estado == 'cancelada' and current_user.rol != 'admin':
        return jsonify({'error': 'Solo administradores pueden cancelar ventas'}), 403
    
    venta.estado = nuevo_estado
    
    # Si se cancela, devolver productos al inventario
    if nuevo_estado == 'cancelada':
        for detalle in venta.detalles:
            inventario = Inventario.query.filter_by(id_producto=detalle.id_producto).first()
            if inventario:
                inventario.cantidad += detalle.cantidad
    
    db.session.commit()
    return jsonify({'mensaje': 'Estado de venta actualizado'})

# Eliminar una venta
@ventas_bp.route('/ventas/<int:id_venta>', methods=['DELETE'])
@role_required('admin')  # Solo admin puede eliminar
def eliminar_venta(id_venta):
    venta = Venta.query.get_or_404(id_venta)
    
    # Solo se pueden eliminar ventas canceladas o pendientes
    if venta.estado == 'completada':
        return jsonify({'error': 'No se puede eliminar una venta completada'}), 400
    
    # Devolver productos al inventario si estaba pendiente
    if venta.estado == 'pendiente':
        for detalle in venta.detalles:
            inventario = Inventario.query.filter_by(id_producto=detalle.id_producto).first()
            if inventario:
                inventario.cantidad += detalle.cantidad
    
    db.session.delete(venta)
    db.session.commit()
    return jsonify({'mensaje': 'Venta eliminada permanentemente'})