from flask import Blueprint, jsonify, request
from models import AreaTrabajo, Usuario, db

work_areas_bp = Blueprint('work_areas', __name__)

@work_areas_bp.route('/work_areas', methods=['GET'])
def get_work_areas():
    areas = AreaTrabajo.query.all()
    return jsonify([{
        'id_area': area.id_area,
        'nombre_area': area.nombre_area,
        'descripcion': area.descripcion,
        'responsable': area.responsable,
        'responsable_name': area.responsable_usuario.nombre if area.responsable_usuario else None
    } for area in areas])

@work_areas_bp.route('/work_areas', methods=['POST'])
def create_work_area():
    data = request.get_json()
    new_area = AreaTrabajo(
        nombre_area=data['nombre_area'],
        descripcion=data.get('descripcion'),
        responsable=data.get('responsable')
    )
    db.session.add(new_area)
    db.session.commit()
    return jsonify({'message': 'Work area created successfully'}), 201

@work_areas_bp.route('/work_areas/<int:id>', methods=['PUT'])
def update_work_area(id):
    area = AreaTrabajo.query.get_or_404(id)
    data = request.get_json()
    area.nombre_area = data.get('nombre_area', area.nombre_area)
    area.descripcion = data.get('descripcion', area.descripcion)
    area.responsable = data.get('responsable', area.responsable)
    db.session.commit()
    return jsonify({'message': 'Work area updated successfully'})

@work_areas_bp.route('/work_areas/<int:id>', methods=['DELETE'])
def delete_work_area(id):
    area = AreaTrabajo.query.get_or_404(id)
    db.session.delete(area)
    db.session.commit()
    return jsonify({'message': 'Work area deleted successfully'})