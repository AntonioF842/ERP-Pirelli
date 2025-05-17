from flask import Blueprint, request, jsonify
from flask_login import login_required
from models import Producto, db
from werkzeug.exceptions import BadRequest
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
products_bp = Blueprint('products_bp', __name__)

@products_bp.route('/products', methods=['GET'])
@login_required
def get_products():
    """Obtiene todos los productos con filtrado opcional"""
    try:
        # Obtener parámetros de filtrado
        categoria = request.args.get('categoria')
        estado = request.args.get('estado')
        search = request.args.get('search')
        
        query = Producto.query
        
        # Aplicar filtros
        if categoria:
            query = query.filter_by(categoria=categoria)
        if estado:
            query = query.filter_by(estado=estado)
        if search:
            query = query.filter(
                (Producto.nombre.ilike(f'%{search}%')) | 
                (Producto.codigo.ilike(f'%{search}%'))
            )
        
        products = query.order_by(Producto.nombre.asc()).all()
        
        # Formatear respuesta
        products_list = [{
            "id_producto": p.id_producto,
            "codigo": p.codigo,
            "nombre": p.nombre,
            "descripcion": p.descripcion if p.descripcion else None,
            "precio": float(p.precio),
            "categoria": p.categoria,
            "estado": p.estado if hasattr(p, 'estado') else 'activo',
            "fecha_creacion": p.fecha_creacion.isoformat() if hasattr(p, 'fecha_creacion') else None,
            "fecha_actualizacion": p.fecha_actualizacion.isoformat() if hasattr(p, 'fecha_actualizacion') else None
        } for p in products]
        
        return jsonify(products_list)
        
    except Exception as e:
        logger.error(f"Error al obtener productos: {str(e)}")
        return jsonify({"error": "Error interno al obtener productos"}), 500

@products_bp.route('/products/<int:id>', methods=['GET'])
@login_required
def get_product(id):
    """Obtiene un producto específico por ID"""
    try:
        product = Producto.query.get_or_404(id)
        
        return jsonify({
            "id_producto": product.id_producto,
            "codigo": product.codigo,
            "nombre": product.nombre,
            "descripcion": product.descripcion if product.descripcion else None,
            "precio": float(product.precio),
            "categoria": product.categoria,
            "estado": product.estado if hasattr(product, 'estado') else 'activo',
            "fecha_creacion": product.fecha_creacion.isoformat() if hasattr(product, 'fecha_creacion') else None,
            "fecha_actualizacion": product.fecha_actualizacion.isoformat() if hasattr(product, 'fecha_actualizacion') else None
        })
        
    except Exception as e:
        logger.error(f"Error al obtener producto {id}: {str(e)}")
        return jsonify({"error": "Producto no encontrado"}), 404

@products_bp.route('/products', methods=['POST'])
@login_required
def create_product():
    """Crea un nuevo producto"""
    try:
        data = request.get_json()
        
        # Validación básica
        if not data:
            raise BadRequest("Datos del producto no proporcionados")
        if not data.get('codigo'):
            raise BadRequest("El código es obligatorio")
        if not data.get('nombre'):
            raise BadRequest("El nombre es obligatorio")
        if not data.get('precio') or float(data.get('precio', 0)) <= 0:
            raise BadRequest("El precio debe ser mayor que cero")
        
        # Verificar si el código ya existe
        if Producto.query.filter_by(codigo=data['codigo']).first():
            return jsonify({"error": "El código de producto ya existe"}), 400
        
        # Crear nuevo producto
        new_product = Producto(
            codigo=data['codigo'],
            nombre=data['nombre'],
            descripcion=data.get('descripcion'),
            precio=data['precio'],
            categoria=data.get('categoria', 'automovil'),
            estado=data.get('estado', 'activo')
        )
        
        # Establecer fechas
        if hasattr(new_product, 'fecha_creacion'):
            new_product.fecha_creacion = datetime.utcnow()
        if hasattr(new_product, 'fecha_actualizacion'):
            new_product.fecha_actualizacion = datetime.utcnow()
        
        db.session.add(new_product)
        db.session.commit()
        
        return jsonify({
            "message": "Producto creado exitosamente",
            "id_producto": new_product.id_producto,
            "codigo": new_product.codigo
        }), 201
        
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear producto: {str(e)}")
        return jsonify({"error": "Error interno al crear producto"}), 500

@products_bp.route('/products/<int:id>', methods=['PUT'])
@login_required
def update_product(id):
    """Actualiza un producto existente"""
    try:
        product = Producto.query.get_or_404(id)
        data = request.get_json()
        
        # Validación básica
        if not data:
            raise BadRequest("Datos de actualización no proporcionados")
            
        # Actualizar campos
        if 'codigo' in data and data['codigo'] != product.codigo:
            # Verificar si el nuevo código ya existe
            if Producto.query.filter(Producto.codigo == data['codigo'], Producto.id_producto != id).first():
                return jsonify({"error": "El código de producto ya está en uso"}), 400
            product.codigo = data['codigo']
            
        if 'nombre' in data:
            product.nombre = data['nombre']
        if 'descripcion' in data:
            product.descripcion = data['descripcion']
        if 'precio' in data:
            product.precio = data['precio']
        if 'categoria' in data:
            product.categoria = data['categoria']
        if 'estado' in data:
            product.estado = data['estado']
            
        # Actualizar fecha de modificación
        if hasattr(product, 'fecha_actualizacion'):
            product.fecha_actualizacion = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "message": "Producto actualizado exitosamente",
            "id_producto": product.id_producto
        })
        
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al actualizar producto {id}: {str(e)}")
        return jsonify({"error": "Error interno al actualizar producto"}), 500

@products_bp.route('/products/<int:id>', methods=['DELETE'])
@login_required
def delete_product(id):
    """Elimina un producto"""
    try:
        product = Producto.query.get_or_404(id)
        
        # Verificar si el producto está siendo usado en otras tablas
        # (Implementar según tu modelo de datos)
        
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({
            "message": "Producto eliminado exitosamente",
            "id_producto": id
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al eliminar producto {id}: {str(e)}")
        return jsonify({"error": "Error interno al eliminar producto"}), 500