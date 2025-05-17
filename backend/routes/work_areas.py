from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from routes.auth import role_required
from models import AreaTrabajo, Usuario, db

work_areas_bp = Blueprint('work_areas', __name__)

@work_areas_bp.route('/work_areas', methods=['GET'])
@login_required
def get_work_areas():
    # Admin y Supervisor ven todas las áreas
    if current_user.rol in ['admin', 'supervisor']:
        areas = AreaTrabajo.query.all()
    # Empleados solo ven su área de trabajo
    elif current_user.rol == 'empleado':
        # Asumiendo que el empleado tiene un campo 'id_area' en su modelo
        areas = AreaTrabajo.query.filter_by(id_area=current_user.id_area).all()
    else:
        return jsonify({'error': 'No autorizado'}), 403

    return jsonify([{
        'id_area': area.id_area,
        'nombre_area': area.nombre_area,
        'descripcion': area.descripcion,
        'responsable': area.responsable,
        'responsable_name': area.responsable_usuario.nombre if area.responsable_usuario else None
    } for area in areas])

@work_areas_bp.route('/work_areas', methods=['POST'])
@role_required('admin')  # Solo admin puede crear áreas
def create_work_area():
    data = request.get_json()
    
    # Validación básica
    if not data.get('nombre_area'):
        return jsonify({'error': 'El nombre del área es obligatorio'}), 400

    new_area = AreaTrabajo(
        nombre_area=data['nombre_area'],
        descripcion=data.get('descripcion'),
        responsable=data.get('responsable')
    )
    
    try:
        db.session.add(new_area)
        db.session.commit()
        return jsonify({
            'message': 'Área de trabajo creada exitosamente',
            'id_area': new_area.id_area
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@work_areas_bp.route('/work_areas/<int:id>', methods=['PUT'])
@role_required('admin', 'supervisor')  # Admin y supervisor pueden actualizar
def update_work_area(id):
    area = AreaTrabajo.query.get_or_404(id)
    data = request.get_json()
    
    # Validación básica
    if 'nombre_area' in data and not data['nombre_area']:
        return jsonify({'error': 'El nombre del área no puede estar vacío'}), 400

    area.nombre_area = data.get('nombre_area', area.nombre_area)
    area.descripcion = data.get('descripcion', area.descripcion)
    area.responsable = data.get('responsable', area.responsable)
    
    try:
        db.session.commit()
        return jsonify({'message': 'Área de trabajo actualizada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@work_areas_bp.route('/work_areas/<int:id>', methods=['DELETE'])
@role_required('admin')  # Solo admin puede eliminar áreas
def delete_work_area(id):
    area = AreaTrabajo.query.get_or_404(id)
    
    # Verificar si el área tiene empleados asignados
    if area.empleados and len(area.empleados) > 0:
        return jsonify({
            'error': 'No se puede eliminar el área porque tiene empleados asignados'
        }), 400
    
    try:
        db.session.delete(area)
        db.session.commit()
        return jsonify({'message': 'Área de trabajo eliminada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500