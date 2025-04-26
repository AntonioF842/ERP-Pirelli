from flask import Blueprint, jsonify, request
from models import Asistencia, Empleado, db
from datetime import datetime, time

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendance', methods=['GET'])
def get_attendance():
    attendance_records = Asistencia.query.all()
    return jsonify([{
        'id_asistencia': record.id_asistencia,
        'id_empleado': record.id_empleado,
        'empleado_name': f"{record.empleado.nombre} {record.empleado.apellidos}",
        'fecha': record.fecha.isoformat(),
        'hora_entrada': record.hora_entrada.isoformat() if record.hora_entrada else None,
        'hora_salida': record.hora_salida.isoformat() if record.hora_salida else None,
        'estado': record.estado
    } for record in attendance_records])

@attendance_bp.route('/attendance/<int:id>', methods=['GET'])
def get_attendance_by_id(id):
    record = Asistencia.query.get_or_404(id)
    return jsonify({
        'id_asistencia': record.id_asistencia,
        'id_empleado': record.id_empleado,
        'empleado_name': f"{record.empleado.nombre} {record.empleado.apellidos}",
        'fecha': record.fecha.isoformat(),
        'hora_entrada': record.hora_entrada.isoformat() if record.hora_entrada else None,
        'hora_salida': record.hora_salida.isoformat() if record.hora_salida else None,
        'estado': record.estado
    })

@attendance_bp.route('/attendance', methods=['POST'])
def create_attendance():
    data = request.get_json()
    new_attendance = Asistencia(
        id_empleado=data['id_empleado'],
        fecha=datetime.strptime(data['fecha'], '%Y-%m-%d').date(),
        hora_entrada=datetime.strptime(data['hora_entrada'], '%H:%M:%S').time() if 'hora_entrada' in data else None,
        hora_salida=datetime.strptime(data['hora_salida'], '%H:%M:%S').time() if 'hora_salida' in data else None,
        estado=data.get('estado', 'presente')
    )
    db.session.add(new_attendance)
    db.session.commit()
    return jsonify({'message': 'Attendance record created successfully'}), 201

@attendance_bp.route('/attendance/<int:id>', methods=['PUT'])
def update_attendance(id):
    attendance = Asistencia.query.get_or_404(id)
    data = request.get_json()
    attendance.id_empleado = data.get('id_empleado', attendance.id_empleado)
    if 'fecha' in data:
        attendance.fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
    if 'hora_entrada' in data:
        attendance.hora_entrada = datetime.strptime(data['hora_entrada'], '%H:%M:%S').time()
    if 'hora_salida' in data:
        attendance.hora_salida = datetime.strptime(data['hora_salida'], '%H:%M:%S').time()
    attendance.estado = data.get('estado', attendance.estado)
    db.session.commit()
    return jsonify({'message': 'Attendance record updated successfully'})

@attendance_bp.route('/attendance/<int:id>', methods=['DELETE'])
def delete_attendance(id):
    attendance = Asistencia.query.get_or_404(id)
    db.session.delete(attendance)
    db.session.commit()
    return jsonify({'message': 'Attendance record deleted successfully'})