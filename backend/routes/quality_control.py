from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from routes.auth import role_required
from models import ControlCalidad, OrdenProduccion, Usuario, db
from datetime import datetime

quality_control_bp = Blueprint('quality_control_bp', __name__)

@quality_control_bp.route('/quality_control', methods=['GET'])
@login_required
def get_quality_controls():
    # Admin puede ver todos los controles
    if current_user.rol == 'admin':
        controls = ControlCalidad.query.all()
    # Supervisor ve los controles de su área
    elif current_user.rol == 'supervisor':
        controls = ControlCalidad.query.join(OrdenProduccion).filter(
            OrdenProduccion.id_area == current_user.id_area
        ).all()
    # Empleados solo ven los controles que ellos realizaron
    elif current_user.rol == 'empleado':
        controls = ControlCalidad.query.filter_by(id_usuario=current_user.id_usuario).all()
    else:
        return jsonify({'error': 'No autorizado'}), 403

    return jsonify([{
        'id_control': control.id_control,
        'id_orden_produccion': control.id_orden_produccion,
        'orden_produccion': control.orden_produccion.id_orden_produccion,
        'fecha': control.fecha.isoformat(),
        'resultado': control.resultado,
        'observaciones': control.observaciones,
        'id_usuario': control.id_usuario,
        'usuario_name': control.usuario.nombre
    } for control in controls])

@quality_control_bp.route('/quality_control', methods=['POST'])
@role_required('admin', 'supervisor', 'empleado')  # Todos los roles pueden crear
def create_quality_control():
    data = request.get_json()
    
    # Validaciones básicas
    if not data.get('id_orden_produccion'):
        return jsonify({'error': 'ID de orden de producción es requerido'}), 400
    if not data.get('resultado'):
        return jsonify({'error': 'Resultado es requerido'}), 400
        
    # Empleados solo pueden registrarse a sí mismos
    if current_user.rol == 'empleado':
        data['id_usuario'] = current_user.id_usuario

    new_control = ControlCalidad(
        id_orden_produccion=data['id_orden_produccion'],
        fecha=datetime.strptime(data['fecha'], '%Y-%m-%d').date(),
        resultado=data['resultado'],
        observaciones=data.get('observaciones'),
        id_usuario=data['id_usuario']
    )
    
    db.session.add(new_control)
    db.session.commit()
    return jsonify({
        'message': 'Registro de control de calidad creado exitosamente',
        'id_control': new_control.id_control
    }), 201

@quality_control_bp.route('/quality_control/<int:id>', methods=['PUT'])
@login_required
def update_quality_control(id):
    control = ControlCalidad.query.get_or_404(id)
    
    # Verificar permisos
    if current_user.rol == 'empleado' and control.id_usuario != current_user.id_usuario:
        return jsonify({'error': 'Solo puede modificar sus propios registros'}), 403
    if current_user.rol == 'supervisor':
        # Verificar que la orden de producción pertenezca a su área
        orden = OrdenProduccion.query.get(control.id_orden_produccion)
        if not orden or orden.id_area != current_user.id_area:
            return jsonify({'error': 'No autorizado para modificar este registro'}), 403

    data = request.get_json()
    control.id_orden_produccion = data.get('id_orden_produccion', control.id_orden_produccion)
    if 'fecha' in data:
        control.fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
    control.resultado = data.get('resultado', control.resultado)
    control.observaciones = data.get('observaciones', control.observaciones)
    
    # Solo admin puede cambiar el usuario asociado
    if 'id_usuario' in data and current_user.rol == 'admin':
        control.id_usuario = data['id_usuario']
    
    db.session.commit()
    return jsonify({'message': 'Registro de control de calidad actualizado exitosamente'})

@quality_control_bp.route('/quality_control/<int:id>', methods=['DELETE'])
@role_required('admin', 'supervisor')  # Solo admin y supervisor pueden eliminar
def delete_quality_control(id):
    control = ControlCalidad.query.get_or_404(id)
    
    # Supervisor solo puede eliminar registros de su área
    if current_user.rol == 'supervisor':
        orden = OrdenProduccion.query.get(control.id_orden_produccion)
        if not orden or orden.id_area != current_user.id_area:
            return jsonify({'error': 'No autorizado para eliminar este registro'}), 403

    db.session.delete(control)
    db.session.commit()
    return jsonify({'message': 'Registro de control de calidad eliminado exitosamente'})