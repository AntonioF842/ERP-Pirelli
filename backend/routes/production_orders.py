from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required
from datetime import datetime
from models import OrdenProduccion, db
from sqlalchemy.exc import SQLAlchemyError

production_orders_bp = Blueprint('production_orders', __name__)

@production_orders_bp.route('/ordenes_produccion', methods=['GET'])
@login_required
def get_production_orders():
    try:
        orders = OrdenProduccion.query.all()
        return jsonify([{
            'id_orden_produccion': order.id_orden_produccion,
            'id_producto': order.id_producto,
            'producto': {
                'id_producto': order.producto.id_producto if order.producto else None,
                'nombre': order.producto.nombre if order.producto else 'Producto no encontrado'
            },
            'cantidad': order.cantidad,
            'fecha_inicio': order.fecha_inicio.isoformat() if order.fecha_inicio else None,
            'fecha_fin': order.fecha_fin.isoformat() if order.fecha_fin else None,
            'estado': order.estado,
            'id_usuario': order.id_usuario,
            'usuario': {
                'id_usuario': order.usuario.id_usuario if order.usuario else None,
                'nombre': order.usuario.nombre if order.usuario else 'Usuario no encontrado'
            }
        } for order in orders])
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@production_orders_bp.route('/ordenes_produccion', methods=['POST'])
@login_required
def create_production_order():
    try:
        data = request.get_json()
        
        # Validación básica
        required_fields = ['id_producto', 'cantidad', 'fecha_inicio', 'id_usuario']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Faltan campos requeridos"}), 400
            
        # Parse dates safely
        try:
            fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date() if data['fecha_inicio'] else None
            fecha_fin = datetime.strptime(data['fecha_fin'], '%Y-%m-%d').date() if data.get('fecha_fin') else None
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido. Use YYYY-MM-DD"}), 400
            
        new_order = OrdenProduccion(
            id_producto=data['id_producto'],
            cantidad=data['cantidad'],
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado=data.get('estado', 'planificada'),
            id_usuario=data['id_usuario']
        )
        
        db.session.add(new_order)
        db.session.commit()
        
        return jsonify({
            'message': 'Orden de producción creada exitosamente',
            'id_orden_produccion': new_order.id_orden_produccion,
            'producto': {
                'id_producto': new_order.producto.id_producto if new_order.producto else None,
                'nombre': new_order.producto.nombre if new_order.producto else 'Producto no encontrado'
            },
            'usuario': {
                'id_usuario': new_order.usuario.id_usuario if new_order.usuario else None,
                'nombre': new_order.usuario.nombre if new_order.usuario else 'Usuario no encontrado'
            }
        }), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@production_orders_bp.route('/ordenes_produccion/<int:id>', methods=['PUT'])
@login_required
def update_production_order(id):
    """Endpoint para actualizar una orden de producción"""
    try:
        # Obtener la orden
        order = OrdenProduccion.query.get(id)
        if not order:
            return jsonify({"error": "Orden no encontrada"}), 404

        # Validar datos
        data = request.get_json()
        if not data:
            return jsonify({"error": "Datos no proporcionados"}), 400

        # Configurar logging si current_app no está disponible
        logger = current_app.logger if current_app else print

        # logger.info(f"Actualizando orden {id} con datos: {data}")

        # Campos actualizables y sus validaciones
        updatable_fields = {
            'estado': lambda x: x in ['planificada', 'en_proceso', 'completada', 'cancelada'],
            'cantidad': lambda x: isinstance(x, int) and x > 0,
            'fecha_inicio': lambda x: True,  # Validación se hace después
            'fecha_fin': lambda x: True,
            'id_producto': lambda x: isinstance(x, int),
            'id_usuario': lambda x: isinstance(x, int),
            'notas': lambda x: isinstance(x, str)
        }

        changes_made = False
        for field, validator in updatable_fields.items():
            if field in data:
                if not validator(data[field]):
                    return jsonify({"error": f"Valor inválido para {field}"}), 400
                
                # Manejo especial para fechas
                if field in ['fecha_inicio', 'fecha_fin']:
                    try:
                        if data[field]:
                            new_date = datetime.strptime(data[field], '%Y-%m-%d').date()
                            setattr(order, field, new_date)
                        else:
                            setattr(order, field, None)
                    except ValueError:
                        return jsonify({
                            "error": f"Formato de fecha inválido para {field}. Use YYYY-MM-DD"
                        }), 400
                else:
                    setattr(order, field, data[field])
                
                changes_made = True

        if not changes_made:
            return jsonify({"warning": "No se realizaron cambios"}), 200

        # Validación de negocio adicional
        if order.fecha_fin and order.fecha_inicio and order.fecha_fin < order.fecha_inicio:
            return jsonify({
                "error": "La fecha fin no puede ser anterior a la fecha inicio"
            }), 400

        # Guardar cambios
        db.session.commit()

        # logger.info(f"Orden {id} actualizada exitosamente")

        # Respuesta exitosa
        response_data = {
            "message": "Orden actualizada exitosamente",
            "orden": {
                "id": order.id_orden_produccion,
                "estado": order.estado,
                "producto": order.producto.nombre if order.producto else None,
                "usuario": order.usuario.nombre if order.usuario else None
            }
        }

        return jsonify(response_data), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        error_msg = f"Error de base de datos: {str(e)}"
        if current_app:
            current_app.logger.error(error_msg)
        else:
            print(error_msg)
        return jsonify({"error": "Error de base de datos"}), 500
        
    except Exception as e:
        error_msg = f"Error inesperado: {str(e)}"
        if current_app:
            current_app.logger.error(error_msg)
        else:
            print(error_msg)
        return jsonify({"error": "Error interno del servidor"}), 500

@production_orders_bp.route('/ordenes_produccion/<int:id>', methods=['DELETE'])
@login_required
def delete_production_order(id):
    try:
        order = OrdenProduccion.query.get_or_404(id)
        db.session.delete(order)
        db.session.commit()
        return jsonify({'message': 'Orden de producción eliminada exitosamente'})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500