from flask import Blueprint, jsonify, request
from models import ControlCalidad, OrdenProduccion, Usuario, db
from datetime import datetime

quality_control_bp = Blueprint('quality_control', __name__)

@quality_control_bp.route('/quality_control', methods=['GET'])
def get_quality_controls():
    controls = ControlCalidad.query.all()
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
def create_quality_control():
    data = request.get_json()
    new_control = ControlCalidad(
        id_orden_produccion=data['id_orden_produccion'],
        fecha=datetime.strptime(data['fecha'], '%Y-%m-%d').date(),
        resultado=data['resultado'],
        observaciones=data.get('observaciones'),
        id_usuario=data['id_usuario']
    )
    db.session.add(new_control)
    db.session.commit()
    return jsonify({'message': 'Quality control record created successfully'}), 201

@quality_control_bp.route('/quality_control/<int:id>', methods=['PUT'])
def update_quality_control(id):
    control = ControlCalidad.query.get_or_404(id)
    data = request.get_json()
    control.id_orden_produccion = data.get('id_orden_produccion', control.id_orden_produccion)
    if 'fecha' in data:
        control.fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
    control.resultado = data.get('resultado', control.resultado)
    control.observaciones = data.get('observaciones', control.observaciones)
    control.id_usuario = data.get('id_usuario', control.id_usuario)
    db.session.commit()
    return jsonify({'message': 'Quality control record updated successfully'})

@quality_control_bp.route('/quality_control/<int:id>', methods=['DELETE'])
def delete_quality_control(id):
    control = ControlCalidad.query.get_or_404(id)
    db.session.delete(control)
    db.session.commit()
    return jsonify({'message': 'Quality control record deleted successfully'})