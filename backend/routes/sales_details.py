from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, DetalleVenta, Producto, Venta
from datetime import date

sales_details_bp = Blueprint('sales_details', __name__)

# Get all sales details (with optional filtering)
@sales_details_bp.route('/sales-details', methods=['GET'])
@login_required
def get_sales_details():
    try:
        # Get query parameters for filtering
        sale_id = request.args.get('sale_id')
        product_id = request.args.get('product_id')
        
        query = DetalleVenta.query
        
        if sale_id:
            query = query.filter_by(id_venta=sale_id)
        if product_id:
            query = query.filter_by(id_producto=product_id)
            
        details = query.all()
        
        details_json = []
        for det in details:
            producto = Producto.query.get(det.id_producto)
            venta = Venta.query.get(det.id_venta)
            
            details_json.append({
                'id_detalle': det.id_detalle,
                'id_venta': det.id_venta,
                'venta_fecha': venta.fecha.strftime('%Y-%m-%d') if venta else None,
                'id_producto': det.id_producto,
                'producto_nombre': producto.nombre if producto else None,
                'producto_codigo': producto.codigo if producto else None,
                'cantidad': det.cantidad,
                'precio_unitario': float(det.precio_unitario),
                'subtotal': float(det.subtotal)
            })
            
        return jsonify(details_json)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get a single sales detail
@sales_details_bp.route('/sales-details/<int:id_detalle>', methods=['GET'])
@login_required
def get_sales_detail(id_detalle):
    try:
        detalle = DetalleVenta.query.get(id_detalle)
        if not detalle:
            return jsonify({'error': 'Detalle de venta no encontrado'}), 404
            
        producto = Producto.query.get(detalle.id_producto)
        venta = Venta.query.get(detalle.id_venta)
        
        return jsonify({
            'id_detalle': detalle.id_detalle,
            'id_venta': detalle.id_venta,
            'venta_fecha': venta.fecha.strftime('%Y-%m-%d') if venta else None,
            'venta_estado': venta.estado if venta else None,
            'id_producto': detalle.id_producto,
            'producto_nombre': producto.nombre if producto else None,
            'producto_codigo': producto.codigo if producto else None,
            'producto_categoria': producto.categoria if producto else None,
            'cantidad': detalle.cantidad,
            'precio_unitario': float(detalle.precio_unitario),
            'subtotal': float(detalle.subtotal)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Create a new sales detail
@sales_details_bp.route('/sales-details', methods=['POST'])
@login_required
def create_sales_detail():
    if current_user.rol not in ['admin', 'supervisor']:
        return jsonify({'error': 'No autorizado'}), 403
        
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['id_venta', 'id_producto', 'cantidad', 'precio_unitario']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Faltan campos requeridos'}), 400
            
        # Calculate subtotal
        subtotal = float(data['cantidad']) * float(data['precio_unitario'])
        
        nuevo_detalle = DetalleVenta(
            id_venta=data['id_venta'],
            id_producto=data['id_producto'],
            cantidad=data['cantidad'],
            precio_unitario=float(data['precio_unitario']),
            subtotal=subtotal
        )
        
        db.session.add(nuevo_detalle)
        db.session.commit()
        
        # Update sale total
        venta = Venta.query.get(data['id_venta'])
        if venta:
            venta.total = sum(d.subtotal for d in venta.detalles)
            db.session.commit()
        
        return jsonify({
            'mensaje': 'Detalle de venta creado',
            'id_detalle': nuevo_detalle.id_detalle
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Update a sales detail
@sales_details_bp.route('/sales-details/<int:id_detalle>', methods=['PUT'])
@login_required
def update_sales_detail(id_detalle):
    if current_user.rol not in ['admin', 'supervisor']:
        return jsonify({'error': 'No autorizado'}), 403
        
    try:
        detalle = DetalleVenta.query.get(id_detalle)
        if not detalle:
            return jsonify({'error': 'Detalle de venta no encontrado'}), 404
            
        data = request.get_json()
        
        # Update fields if provided
        if 'id_producto' in data:
            detalle.id_producto = data['id_producto']
        if 'cantidad' in data:
            detalle.cantidad = data['cantidad']
        if 'precio_unitario' in data:
            detalle.precio_unitario = float(data['precio_unitario'])
            
        # Recalculate subtotal
        detalle.subtotal = detalle.cantidad * detalle.precio_unitario
        
        db.session.commit()
        
        # Update sale total
        venta = Venta.query.get(detalle.id_venta)
        if venta:
            venta.total = sum(d.subtotal for d in venta.detalles)
            db.session.commit()
        
        return jsonify({'mensaje': 'Detalle de venta actualizado'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Delete a sales detail
@sales_details_bp.route('/sales-details/<int:id_detalle>', methods=['DELETE'])
@login_required
def delete_sales_detail(id_detalle):
    if current_user.rol != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
        
    try:
        detalle = DetalleVenta.query.get(id_detalle)
        if not detalle:
            return jsonify({'error': 'Detalle de venta no encontrado'}), 404
            
        sale_id = detalle.id_venta
        db.session.delete(detalle)
        db.session.commit()
        
        # Update sale total
        venta = Venta.query.get(sale_id)
        if venta:
            venta.total = sum(d.subtotal for d in venta.detalles)
            db.session.commit()
        
        return jsonify({'mensaje': 'Detalle de venta eliminado'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500