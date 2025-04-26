from flask import Blueprint, jsonify, request
from models import Empleado, AreaTrabajo, db
from datetime import datetime
from routes.auth import role_required

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/employees', methods=['GET'])
@role_required('admin', 'supervisor')
def get_employees():
    employees = Empleado.query.all()
    return jsonify([{
        'id_empleado': emp.id_empleado,
        'nombre': emp.nombre,
        'apellidos': emp.apellidos,
        'id_area': emp.id_area,
        'area_name': emp.area.nombre_area if emp.area else None,
        'puesto': emp.puesto,
        'salario': float(emp.salario) if emp.salario else None,
        'fecha_contratacion': emp.fecha_contratacion.isoformat() if emp.fecha_contratacion else None,
        'activo': emp.activo
    } for emp in employees])

@employees_bp.route('/employees', methods=['POST'])
@role_required('admin', 'supervisor')
def create_employee():
    data = request.get_json()
    new_employee = Empleado(
        nombre=data['nombre'],
        apellidos=data['apellidos'],
        id_area=data.get('id_area'),
        puesto=data.get('puesto'),
        salario=data.get('salario'),
        fecha_contratacion=datetime.strptime(data['fecha_contratacion'], '%Y-%m-%d') if 'fecha_contratacion' in data else None,
        activo=data.get('activo', True)
    )
    db.session.add(new_employee)
    db.session.commit()
    return jsonify({'message': 'Employee created successfully'}), 201

@employees_bp.route('/employees/<int:id>', methods=['PUT'])
@role_required('admin', 'supervisor')
def update_employee(id):
    employee = Empleado.query.get_or_404(id)
    data = request.get_json()
    employee.nombre = data.get('nombre', employee.nombre)
    employee.apellidos = data.get('apellidos', employee.apellidos)
    employee.id_area = data.get('id_area', employee.id_area)
    employee.puesto = data.get('puesto', employee.puesto)
    employee.salario = data.get('salario', employee.salario)
    if 'fecha_contratacion' in data:
        employee.fecha_contratacion = datetime.strptime(data['fecha_contratacion'], '%Y-%m-%d')
    employee.activo = data.get('activo', employee.activo)
    db.session.commit()
    return jsonify({'message': 'Employee updated successfully'})

@employees_bp.route('/employees/<int:id>', methods=['DELETE'])
@role_required('admin', 'supervisor')
def delete_employee(id):
    employee = Empleado.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    return jsonify({'message': 'Employee deleted successfully'})

@employees_bp.route('/employees/<int:id>', methods=['GET'])
@role_required('admin', 'supervisor')
def get_employee(id):
    employee = Empleado.query.get_or_404(id)
    return jsonify({
        'id_empleado': employee.id_empleado,
        'nombre': employee.nombre,
        'apellidos': employee.apellidos,
        'id_area': employee.id_area,
        'area_name': employee.area.nombre_area if employee.area else None,
        'puesto': employee.puesto,
        'salario': float(employee.salario) if employee.salario else None,
        'fecha_contratacion': employee.fecha_contratacion.isoformat() if employee.fecha_contratacion else None,
        'activo': employee.activo
    })
