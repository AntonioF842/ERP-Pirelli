from flask import Blueprint, jsonify, request
from models import Mantenimiento, ActivoProduccion, Empleado, db
from datetime import datetime

maintenance_bp = Blueprint('maintenance', __name__)

@maintenance_bp.route('/maintenance', methods=['GET'])
def get_maintenance():
    maintenance_records = Mantenimiento.query.all()
    return jsonify([{
        'id_mantenimiento': maint.id_mantenimiento,
        'id_activo': maint.id_activo,
        'activo_name': maint.activo.nombre,
        'tipo': maint.tipo,
        'fecha': maint.fecha.isoformat(),
        'descripcion': maint.descripcion,
        'costo': float(maint.costo) if maint.costo else None,
        'id_empleado': maint.id_empleado,
        'empleado_name': f"{maint.empleado.nombre} {maint.empleado.apellidos}" if maint.empleado else None
    } for maint in maintenance_records])

@maintenance_bp.route('/maintenance', methods=['POST'])
def create_maintenance():
    data = request.get_json()
    new_maintenance = Mantenimiento(
        id_activo=data['id_activo'],
        tipo=data['tipo'],
        fecha=datetime.strptime(data['fecha'], '%Y-%m-%d').date(),
        descripcion=data.get('descripcion'),
        costo=data.get('costo'),
        id_empleado=data.get('id_empleado')
    )
    db.session.add(new_maintenance)
    db.session.commit()
    return jsonify({'message': 'Maintenance record created successfully'}), 201

@maintenance_bp.route('/maintenance/<int:id>', methods=['PUT'])
def update_maintenance(id):
    maintenance = Mantenimiento.query.get_or_404(id)
    data = request.get_json()
    maintenance.id_activo = data.get('id_activo', maintenance.id_activo)
    maintenance.tipo = data.get('tipo', maintenance.tipo)
    if 'fecha' in data:
        maintenance.fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
    maintenance.descripcion = data.get('descripcion', maintenance.descripcion)
    maintenance.costo = data.get('costo', maintenance.costo)
    maintenance.id_empleado = data.get('id_empleado', maintenance.id_empleado)
    db.session.commit()
    return jsonify({'message': 'Maintenance record updated successfully'})

@maintenance_bp.route('/maintenance/<int:id>', methods=['DELETE'])
def delete_maintenance(id):
    maintenance = Mantenimiento.query.get_or_404(id)
    db.session.delete(maintenance)
    db.session.commit()
    return jsonify({'message': 'Maintenance record deleted successfully'})