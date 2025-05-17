from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from routes.auth import role_required
from models import ProyectoID, db
from datetime import datetime

r_d_projects_bp = Blueprint('r_d_projects', __name__)

@r_d_projects_bp.route('/r_d_projects', methods=['GET'])
@login_required
def get_r_d_projects():
    """Obtiene todos los proyectos de I+D"""
    # Admin ve todos los proyectos
    if current_user.rol == 'admin':
        projects = ProyectoID.query.all()
    # Supervisor solo ve proyectos activos
    elif current_user.rol == 'supervisor':
        projects = ProyectoID.query.filter(ProyectoID.estado.in_(['activo', 'planificacion'])).all()
    # Empleado solo ve proyectos activos donde está asignado (requeriría relación muchos-a-muchos)
    elif current_user.rol == 'empleado':
        projects = ProyectoID.query.filter_by(estado='activo').all()  # Simplificado
    else:
        return jsonify({"error": "No autorizado"}), 403

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
    project = ProyectoID.query.get_or_404(id)
    
    # Restricciones por rol
    if current_user.rol == 'supervisor' and project.estado not in ['activo', 'planificacion']:
        return jsonify({"error": "No autorizado"}), 403
    elif current_user.rol == 'empleado' and project.estado != 'activo':
        return jsonify({"error": "No autorizado"}), 403
        
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
@role_required('admin', 'supervisor')  # Solo admin y supervisor pueden crear
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
        return jsonify({
            "message": "Proyecto creado exitosamente",
            "id_proyecto": new_project.id_proyecto
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@r_d_projects_bp.route('/r_d_projects/<int:id>', methods=['PUT'])
@login_required
def update_r_d_project(id):
    """Actualiza un proyecto de I+D existente"""
    project = ProyectoID.query.get_or_404(id)
    
    # Restricciones por rol
    if current_user.rol == 'empleado':
        return jsonify({"error": "No autorizado"}), 403
    elif current_user.rol == 'supervisor' and project.estado == 'completado':
        return jsonify({"error": "No puede modificar proyectos completados"}), 403

    data = request.json
    
    try:
        project.nombre = data.get('nombre', project.nombre)
        project.descripcion = data.get('descripcion', project.descripcion)
        
        if 'fecha_inicio' in data:
            project.fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date()
        if 'fecha_fin_estimada' in data:
            project.fecha_fin_estimada = datetime.strptime(data['fecha_fin_estimada'], '%Y-%m-%d').date()
            
        project.presupuesto = data.get('presupuesto', project.presupuesto)
        
        # Solo admin puede cambiar el estado a 'completado'
        if 'estado' in data and data['estado'] == 'completado':
            if current_user.rol != 'admin':
                return jsonify({"error": "Solo admin puede completar proyectos"}), 403
            project.estado = data['estado']
        elif 'estado' in data:
            project.estado = data['estado']
        
        db.session.commit()
        return jsonify({"message": "Proyecto actualizado exitosamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@r_d_projects_bp.route('/r_d_projects/<int:id>', methods=['DELETE'])
@role_required('admin')  # Solo admin puede eliminar
def delete_r_d_project(id):
    """Elimina un proyecto de I+D"""
    project = ProyectoID.query.get_or_404(id)
    
    # Validar que el proyecto no tenga dependencias
    # (asumiendo que hay relaciones con otras tablas)
    if hasattr(project, 'tareas') and len(project.tareas) > 0:
        return jsonify({"error": "No se puede eliminar, tiene tareas asociadas"}), 400
        
    try:
        db.session.delete(project)
        db.session.commit()
        return jsonify({"message": "Proyecto eliminado exitosamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500