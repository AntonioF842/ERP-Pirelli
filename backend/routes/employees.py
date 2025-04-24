from flask import Blueprint, request, jsonify
from backend.models import Empleado, AreaTrabajo
from config import db

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/employees', methods=['GET'])
def get_employees():
    employees = Empleado.query.all()
    return jsonify([{
        'id': e.id_empleado,
        'nombre': e.nombre,
        'apellidos': e.apellidos,
        'area': e.area.nombre_area if e.area else None,
        'puesto': e.puesto,
        'salario': float(e.salario) if e.salario else None,
        'fecha_contratacion': e.fecha_contratacion.isoformat() if e.fecha_contratacion else None,
        'activo': e.activo
    } for e in employees])

@employees_bp.route('/employees/<int:id>', methods=['GET'])
def get_employee(id):
    e = Empleado.query.get_or_404(id)
    return jsonify({
        'id': e.id_empleado,
        'nombre': e.nombre,
        'apellidos': e.apellidos,
        'area': e.area.nombre_area if e.area else None,
        'puesto': e.puesto,
        'salario': float(e.salario) if e.salario else None,
        'fecha_contratacion': e.fecha_contratacion.isoformat() if e.fecha_contratacion else None,
        'activo': e.activo
    })

@employees_bp.route('/employees', methods=['POST'])
def create_employee():
    data = request.json
    new_employee = Empleado(
        nombre=data['nombre'],
        apellidos=data['apellidos'],
        id_area=data.get('id_area'),
        puesto=data.get('puesto'),
        salario=data.get('salario'),
        fecha_contratacion=data.get('fecha_contratacion'),
        activo=data.get('activo', True)
    )
    db.session.add(new_employee)
    db.session.commit()
    return jsonify({'message': 'Employee created', 'id': new_employee.id_empleado}), 201

@employees_bp.route('/employees/<int:id>', methods=['PUT'])
def update_employee(id):
    e = Empleado.query.get_or_404(id)
    data = request.json
    e.nombre = data.get('nombre', e.nombre)
    e.apellidos = data.get('apellidos', e.apellidos)
    e.id_area = data.get('id_area', e.id_area)
    e.puesto = data.get('puesto', e.puesto)
    e.salario = data.get('salario', e.salario)
    e.fecha_contratacion = data.get('fecha_contratacion', e.fecha_contratacion)
    e.activo = data.get('activo', e.activo)
    db.session.commit()
    return jsonify({'message': 'Employee updated'})

@employees_bp.route('/employees/<int:id>', methods=['DELETE'])
def delete_employee(id):
    e = Empleado.query.get_or_404(id)
    db.session.delete(e)
    db.session.commit()
    return jsonify({'message': 'Employee deleted'})