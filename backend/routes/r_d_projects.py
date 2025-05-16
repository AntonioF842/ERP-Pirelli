from flask import Blueprint, request, jsonify
from flask_login import login_required
from models import ProyectoID, db
from datetime import datetime

r_d_projects_bp = Blueprint('r_d_projects', __name__)

@r_d_projects_bp.route('/r_d_projects', methods=['GET'])
@login_required
def get_r_d_projects():
    """Obtiene todos los proyectos de I+D"""
    projects = ProyectoID.query.all()
    projects_list = [{
        'id_proyecto': p.id_proyecto,
        'nombre': p.nombre,
        'descripcion': p.descripcion,
        'fecha_inicio': p.fecha_inicio.isoformat() if p.fecha_inicio else None,
        'fecha_fin_estimada': p.fecha_fin_estimada.isoformat() if p.fecha_fin_estimada else None,
        'presupuesto': float(p.presupuesto) if p.presupuesto else None,
        'estado': p.estado
    } for p in projects]
    return jsonify(projects_list)

@r_d_projects_bp.route('/r_d_projects/<int:id>', methods=['GET'])
@login_required
def get_r_d_project(id):
    """Obtiene un proyecto de I+D por su ID"""
    project = ProyectoID.query.get(id)
    if not project:
        return jsonify({"error": "Proyecto no encontrado"}), 404
    return jsonify({
        'id_proyecto': project.id_proyecto,
        'nombre': project.nombre,
        'descripcion': project.descripcion,
        'fecha_inicio': project.fecha_inicio.isoformat() if project.fecha_inicio else None,
        'fecha_fin_estimada': project.fecha_fin_estimada.isoformat() if project.fecha_fin_estimada else None,
        'presupuesto': float(project.presupuesto) if project.presupuesto else None,
        'estado': project.estado
    })

@r_d_projects_bp.route('/r_d_projects', methods=['POST'])
@login_required
def create_r_d_project():
    """Crea un nuevo proyecto de I+D"""
    data = request.json
    
    # Validación básica
    if not data.get('nombre'):
        return jsonify({"error": "El nombre es obligatorio"}), 400
        
    try:
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
        return jsonify({"message": "Proyecto creado exitosamente"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@r_d_projects_bp.route('/r_d_projects/<int:id>', methods=['PUT'])
@login_required
def update_r_d_project(id):
    """Actualiza un proyecto de I+D existente"""
    project = ProyectoID.query.get(id)
    if not project:
        return jsonify({"error": "Proyecto no encontrado"}), 404

    data = request.json
    
    try:
        project.nombre = data.get('nombre', project.nombre)
        project.descripcion = data.get('descripcion', project.descripcion)
        
        if 'fecha_inicio' in data:
            project.fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date()
        if 'fecha_fin_estimada' in data:
            project.fecha_fin_estimada = datetime.strptime(data['fecha_fin_estimada'], '%Y-%m-%d').date()
            
        project.presupuesto = data.get('presupuesto', project.presupuesto)
        project.estado = data.get('estado', project.estado)
        
        db.session.commit()
        return jsonify({"message": "Proyecto actualizado exitosamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@r_d_projects_bp.route('/r_d_projects/<int:id>', methods=['DELETE'])
@login_required
def delete_r_d_project(id):
    """Elimina un proyecto de I+D"""
    project = ProyectoID.query.get(id)
    if not project:
        return jsonify({"error": "Proyecto no encontrado"}), 404
        
    try:
        db.session.delete(project)
        db.session.commit()
        return jsonify({"message": "Proyecto eliminado exitosamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500