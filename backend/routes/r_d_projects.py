from flask import Blueprint, jsonify, request
from models import ProyectoID, db
from datetime import datetime

r_d_projects_bp = Blueprint('r_d_projects', __name__)

@r_d_projects_bp.route('/r_d_projects', methods=['GET'])
def get_r_d_projects():
    projects = ProyectoID.query.all()
    return jsonify([{
        'id_proyecto': project.id_proyecto,
        'nombre': project.nombre,
        'descripcion': project.descripcion,
        'fecha_inicio': project.fecha_inicio.isoformat() if project.fecha_inicio else None,
        'fecha_fin_estimada': project.fecha_fin_estimada.isoformat() if project.fecha_fin_estimada else None,
        'presupuesto': float(project.presupuesto) if project.presupuesto else None,
        'estado': project.estado
    } for project in projects])

@r_d_projects_bp.route('/r_d_projects', methods=['POST'])
def create_r_d_project():
    data = request.get_json()
    new_project = ProyectoID(
        nombre=data['nombre'],
        descripcion=data.get('descripcion'),
        fecha_inicio=datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date() if 'fecha_inicio' in data else None,
        fecha_fin_estimada=datetime.strptime(data['fecha_fin_estimada'], '%Y-%m-%d').date() if 'fecha_fin_estimada' in data else None,
        presupuesto=data.get('presupuesto'),
        estado=data.get('estado', 'planificacion')
    )
    db.session.add(new_project)
    db.session.commit()
    return jsonify({'message': 'R&D project created successfully'}), 201

@r_d_projects_bp.route('/r_d_projects/<int:id>', methods=['PUT'])
def update_r_d_project(id):
    project = ProyectoID.query.get_or_404(id)
    data = request.get_json()
    project.nombre = data.get('nombre', project.nombre)
    project.descripcion = data.get('descripcion', project.descripcion)
    if 'fecha_inicio' in data:
        project.fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date()
    if 'fecha_fin_estimada' in data:
        project.fecha_fin_estimada = datetime.strptime(data['fecha_fin_estimada'], '%Y-%m-%d').date()
    project.presupuesto = data.get('presupuesto', project.presupuesto)
    project.estado = data.get('estado', project.estado)
    db.session.commit()
    return jsonify({'message': 'R&D project updated successfully'})

@r_d_projects_bp.route('/r_d_projects/<int:id>', methods=['DELETE'])
def delete_r_d_project(id):
    project = ProyectoID.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    return jsonify({'message': 'R&D project deleted successfully'})