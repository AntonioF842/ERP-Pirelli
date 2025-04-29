from flask import Blueprint, jsonify, request
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
def get_purchase_orders():
    """
    Obtiene todas las órdenes de compra.
    """
    orders = OrdenCompra.query.all()
    return jsonify([serialize_purchase_order(order) for order in orders])

@purchase_orders_bp.route('', methods=['POST'])
def create_purchase_order():
    """
    Crea una nueva orden de compra.
    """
    data = request.get_json()

    # Validaciones de campos obligatorios
    if 'supplier_id' not in data:
        return jsonify({'error': "Missing field: supplier_id"}), 400

    if 'user_id' not in data:
        return jsonify({'error': "Missing field: user_id"}), 400

    # Ignorar po_id si lo mandan
    data.pop('po_id', None)

    new_order = OrdenCompra(
        id_proveedor=data['supplier_id'],
        id_usuario=data['user_id'],
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

    return jsonify({'message': 'Purchase order created successfully', 'po_id': new_order.id_orden_compra}), 201

@purchase_orders_bp.route('/<int:id>', methods=['PUT'])
def update_purchase_order(id):
    """
    Actualiza una orden de compra existente.
    """
    order = OrdenCompra.query.get_or_404(id)
    data = request.get_json()

    order.id_proveedor = data.get('supplier_id', order.id_proveedor)
    order.id_usuario = data.get('user_id', order.id_usuario)
    
    if 'date' in data:
        order.fecha = datetime.strptime(data['date'], '%Y-%m-%d').date()
    
    if 'delivery_date' in data:
        if data['delivery_date']:
            order.fecha_entrega_esperada = datetime.strptime(data['delivery_date'], '%Y-%m-%d').date()
        else:
            order.fecha_entrega_esperada = None

    order.estado = data.get('status', order.estado)
    order.total = data.get('total', order.total)

    db.session.commit()

    # TODO: Implementar actualización de detalles si se desea

    return jsonify({'message': 'Purchase order updated successfully'})

@purchase_orders_bp.route('/<int:id>', methods=['DELETE'])
def delete_purchase_order(id):
    """
    Elimina una orden de compra junto con sus detalles.
    """
    order = OrdenCompra.query.get_or_404(id)

    # Primero eliminar detalles relacionados
    DetalleOrdenCompra.query.filter_by(id_orden_compra=id).delete()
    db.session.delete(order)
    db.session.commit()

    return jsonify({'message': 'Purchase order deleted successfully'})

@purchase_orders_bp.route('/<int:id>', methods=['GET'])
def get_purchase_order(id):
    """
    Obtiene una orden de compra específica por ID.
    """
    order = OrdenCompra.query.get_or_404(id)
    return jsonify(serialize_purchase_order(order))
