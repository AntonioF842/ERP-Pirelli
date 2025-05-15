from flask import Blueprint, request, jsonify
from flask_login import login_required
from models import Mantenimiento, ActivoProduccion, Empleado, db
from datetime import datetime

maintenance_bp = Blueprint('maintenance', __name__)

@maintenance_bp.route('/maintenance', methods=['GET'])
@login_required
def get_maintenance():
    """Obtiene todos los registros de mantenimiento"""
    maintenance_records = Mantenimiento.query.all()
    return jsonify([{
        'id_mantenimiento': maint.id_mantenimiento,
        'id_activo': maint.id_activo,
        'activo_name': maint.activo.nombre if maint.activo else None,
        'tipo': maint.tipo,
        'fecha': maint.fecha.isoformat() if maint.fecha else None,
        'descripcion': maint.descripcion,
        'costo': float(maint.costo) if maint.costo else None,
        'id_empleado': maint.id_empleado,
        'empleado_name': f"{maint.empleado.nombre} {maint.empleado.apellidos}" if maint.empleado else None
    } for maint in maintenance_records])

@maintenance_bp.route('/maintenance/<int:id>', methods=['GET'])
@login_required
def get_maintenance_record(id):
    """Obtiene un registro de mantenimiento específico"""
    maint = Mantenimiento.query.get_or_404(id)
    return jsonify({
        'id_mantenimiento': maint.id_mantenimiento,
        'id_activo': maint.id_activo,
        'activo_name': maint.activo.nombre if maint.activo else None,
        'tipo': maint.tipo,
        'fecha': maint.fecha.isoformat() if maint.fecha else None,
        'descripcion': maint.descripcion,
        'costo': float(maint.costo) if maint.costo else None,
        'id_empleado': maint.id_empleado,
        'empleado_name': f"{maint.empleado.nombre} {maint.empleado.apellidos}" if maint.empleado else None
    })

@maintenance_bp.route('/maintenance', methods=['POST'])
@login_required
def create_maintenance():
    """Crea un nuevo registro de mantenimiento"""
    data = request.get_json()
    
    # Validación básica
    if not data.get('id_activo'):
        return jsonify({'error': 'Se requiere un activo'}), 400
    if not data.get('tipo') or data['tipo'] not in ['preventivo', 'correctivo']:
        return jsonify({'error': 'Tipo de mantenimiento inválido'}), 400
    
    try:
        new_maintenance = Mantenimiento(
            id_activo=data['id_activo'],
            tipo=data['tipo'],
            fecha=datetime.strptime(data['fecha'], '%Y-%m-%d').date() if data.get('fecha') else None,
            descripcion=data.get('descripcion'),
            costo=data.get('costo'),
            id_empleado=data.get('id_empleado')
        )
        db.session.add(new_maintenance)
        db.session.commit()
        
        return jsonify({
            'message': 'Registro de mantenimiento creado exitosamente',
            'id_mantenimiento': new_maintenance.id_mantenimiento
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@maintenance_bp.route('/maintenance/<int:id>', methods=['PUT'])
@login_required
def update_maintenance(id):
    """Actualiza un registro de mantenimiento existente"""
    maint = Mantenimiento.query.get_or_404(id)
    data = request.get_json()
    
    try:
        maint.id_activo = data.get('id_activo', maint.id_activo)
        maint.tipo = data.get('tipo', maint.tipo)
        if 'fecha' in data:
            maint.fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
        maint.descripcion = data.get('descripcion', maint.descripcion)
        maint.costo = data.get('costo', maint.costo)
        maint.id_empleado = data.get('id_empleado', maint.id_empleado)
        
        db.session.commit()
        return jsonify({'message': 'Registro de mantenimiento actualizado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@maintenance_bp.route('/maintenance/<int:id>', methods=['DELETE'])
@login_required
def delete_maintenance(id):
    """Elimina un registro de mantenimiento"""
    maint = Mantenimiento.query.get_or_404(id)
    
    try:
        db.session.delete(maint)
        db.session.commit()
        return jsonify({'message': 'Registro de mantenimiento eliminado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500