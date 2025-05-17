from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from routes.auth import role_required
from models import OrdenCompra, Proveedor, Usuario, DetalleOrdenCompra, db
from datetime import datetime

purchase_orders_bp = Blueprint('purchase_orders', __name__)

def serialize_purchase_order(order):
    """
    Serializa una orden de compra para la respuesta JSON.
    Utiliza nombres de campo consistentes con el frontend.
    """
    return {
        'po_id': order.id_orden_compra,
        'supplier_id': order.id_proveedor,
        'supplier_name': order.proveedor.nombre if order.proveedor else None,
        'user_id': order.id_usuario,
        'user_name': order.usuario.nombre if order.usuario else None,
        'date': order.fecha.isoformat(),
        'delivery_date': order.fecha_entrega_esperada.isoformat() if order.fecha_entrega_esperada else None,
        'status': order.estado,
        'total': float(order.total) if order.total else None,
        'details': [
            {
                'detail_id': det.id_detalle,
                'material_id': det.id_material,
                'material_name': det.material.nombre if det.material else None,
                'quantity': det.cantidad,
                'unit_price': float(det.precio_unitario) if det.precio_unitario else None,
                'subtotal': float(det.subtotal) if det.subtotal else None
            }
            for det in order.detalles
        ]
    }

@purchase_orders_bp.route('', methods=['GET'])
@login_required
def get_purchase_orders():
    """
    Obtiene todas las órdenes de compra.
    Admin y Supervisor ven todas, Empleados ven solo las suyas.
    """
    if current_user.rol in ['admin', 'supervisor']:
        orders = OrdenCompra.query.all()
    elif current_user.rol == 'empleado':
        orders = OrdenCompra.query.filter_by(id_usuario=current_user.id_usuario).all()
    else:
        return jsonify({'error': 'No autorizado'}), 403

    return jsonify([serialize_purchase_order(order) for order in orders])

@purchase_orders_bp.route('', methods=['POST'])
@role_required('admin', 'supervisor')  # Solo admin y supervisor pueden crear
def create_purchase_order():
    """
    Crea una nueva orden de compra.
    """
    data = request.get_json()

    # Validaciones de campos obligatorios
    if 'supplier_id' not in data:
        return jsonify({'error': "Falta el campo: supplier_id"}), 400

    # Ignorar po_id si lo mandan
    data.pop('po_id', None)

    new_order = OrdenCompra(
        id_proveedor=data['supplier_id'],
        id_usuario=current_user.id_usuario,  # Usar el usuario actual
        fecha=datetime.strptime(data['date'], '%Y-%m-%d').date(),
        fecha_entrega_esperada=datetime.strptime(data['delivery_date'], '%Y-%m-%d').date() if data.get('delivery_date') else None,
        estado=data.get('status', 'pendiente'),
        total=data.get('total')
    )
    db.session.add(new_order)
    db.session.commit()

    # Agregar detalles si se enviaron
    if 'details' in data:
        for detalle in data['details']:
            new_detalle = DetalleOrdenCompra(
                id_orden_compra=new_order.id_orden_compra,
                id_material=detalle['material_id'],
                cantidad=detalle['quantity'],
                precio_unitario=detalle.get('unit_price'),
                subtotal=detalle.get('subtotal')
            )
            db.session.add(new_detalle)
        db.session.commit()

    return jsonify({
        'message': 'Orden de compra creada exitosamente',
        'po_id': new_order.id_orden_compra
    }), 201

@purchase_orders_bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_purchase_order(id):
    """
    Actualiza una orden de compra existente.
    Admin y Supervisor pueden actualizar cualquier orden.
    Empleados solo pueden actualizar las suyas.
    """
    order = OrdenCompra.query.get_or_404(id)
    
    # Verificar permisos
    if current_user.rol == 'empleado' and order.id_usuario != current_user.id_usuario:
        return jsonify({'error': 'No autorizado para modificar esta orden'}), 403

    data = request.get_json()

    # Solo admin/supervisor pueden cambiar proveedor
    if 'supplier_id' in data and current_user.rol in ['admin', 'supervisor']:
        order.id_proveedor = data['supplier_id']
    
    if 'date' in data:
        order.fecha = datetime.strptime(data['date'], '%Y-%m-%d').date()
    
    if 'delivery_date' in data:
        if data['delivery_date']:
            order.fecha_entrega_esperada = datetime.strptime(data['delivery_date'], '%Y-%m-%d').date()
        else:
            order.fecha_entrega_esperada = None

    # Solo admin/supervisor pueden cambiar estado
    if 'status' in data and current_user.rol in ['admin', 'supervisor']:
        order.estado = data['status']

    order.total = data.get('total', order.total)

    db.session.commit()

    return jsonify({'message': 'Orden de compra actualizada exitosamente'})

@purchase_orders_bp.route('/<int:id>', methods=['DELETE'])
@role_required('admin')  # Solo admin puede eliminar
def delete_purchase_order(id):
    """
    Elimina una orden de compra junto con sus detalles.
    Solo disponible para administradores.
    """
    order = OrdenCompra.query.get_or_404(id)

    # Verificar si la orden ya fue procesada
    if order.estado in ['aprobada', 'completada']:
        return jsonify({
            'error': 'No se puede eliminar una orden en estado aprobada o completada'
        }), 400

    # Primero eliminar detalles relacionados
    DetalleOrdenCompra.query.filter_by(id_orden_compra=id).delete()
    db.session.delete(order)
    db.session.commit()

    return jsonify({'message': 'Orden de compra eliminada exitosamente'})

@purchase_orders_bp.route('/<int:id>', methods=['GET'])
@login_required
def get_purchase_order(id):
    """
    Obtiene una orden de compra específica por ID.
    Admin y Supervisor ven cualquier orden, Empleados solo las suyas.
    """
    order = OrdenCompra.query.get_or_404(id)
    
    if current_user.rol == 'empleado' and order.id_usuario != current_user.id_usuario:
        return jsonify({'error': 'No autorizado para ver esta orden'}), 403

    return jsonify(serialize_purchase_order(order))