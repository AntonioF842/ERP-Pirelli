from flask import Blueprint, jsonify, request
from models import Incidente, AreaTrabajo, Empleado, db
from datetime import datetime

incidents_bp = Blueprint('incidents', __name__)

@incidents_bp.route('/incidents', methods=['GET'])
def get_incidents():
    incidents = Incidente.query.all()
    return jsonify([{
        'id_incidente': inc.id_incidente,
        'tipo': inc.tipo,
        'descripcion': inc.descripcion,
        'fecha': inc.fecha.isoformat(),
        'id_area': inc.id_area,
        'area_name': inc.area.nombre_area if inc.area else None,
        'id_empleado_reporta': inc.id_empleado_reporta,
        'empleado_name': f"{inc.empleado_reporta.nombre} {inc.empleado_reporta.apellidos}" if inc.empleado_reporta else None,
        'estado': inc.estado
    } for inc in incidents])

@incidents_bp.route('/incidents', methods=['POST'])
def create_incident():
    data = request.get_json()
    new_incident = Incidente(
        tipo=data['tipo'],
        descripcion=data['descripcion'],
        fecha=datetime.strptime(data['fecha'], '%Y-%m-%d').date(),
        id_area=data.get('id_area'),
        id_empleado_reporta=data.get('id_empleado_reporta'),
        estado=data.get('estado', 'reportado')
    )
    db.session.add(new_incident)
    db.session.commit()
    return jsonify({'message': 'Incident record created successfully'}), 201

@incidents_bp.route('/incidents/<int:id>', methods=['PUT'])
def update_incident(id):
    incident = Incidente.query.get_or_404(id)
    data = request.get_json()
    incident.tipo = data.get('tipo', incident.tipo)
    incident.descripcion = data.get('descripcion', incident.descripcion)
    if 'fecha' in data:
        incident.fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
    incident.id_area = data.get('id_area', incident.id_area)
    incident.id_empleado_reporta = data.get('id_empleado_reporta', incident.id_empleado_reporta)
    incident.estado = data.get('estado', incident.estado)
    db.session.commit()
    return jsonify({'message': 'Incident record updated successfully'})

@incidents_bp.route('/incidents/<int:id>', methods=['DELETE'])
def delete_incident(id):
    incident = Incidente.query.get_or_404(id)
    db.session.delete(incident)
    db.session.commit()
    return jsonify({'message': 'Incident record deleted successfully'})