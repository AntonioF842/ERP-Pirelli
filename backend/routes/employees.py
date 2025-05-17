from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from models import Empleado, AreaTrabajo, db
from datetime import datetime
from routes.auth import role_required

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/employees', methods=['GET'])
@login_required
def get_employees():
    # Admin puede ver todos los empleados
    if current_user.rol == 'admin':
        employees = Empleado.query.all()
    # Supervisor solo ve empleados de su área
    elif current_user.rol == 'supervisor':
        # Asumiendo que current_user.id_empleado existe y está relacionado con un Empleado
        supervisor = Empleado.query.get(current_user.id_empleado)
        if supervisor and supervisor.id_area:
            employees = Empleado.query.filter_by(id_area=supervisor.id_area).all()
        else:
            employees = []
    # Empleado solo puede ver su propia información
    elif current_user.rol == 'empleado':
        employees = [Empleado.query.get(current_user.id_empleado)] if current_user.id_empleado else []
    else:
        return jsonify({"error": "No autorizado"}), 403

    return jsonify([{
        'id_empleado': emp.id_empleado,
        'nombre': emp.nombre,
        'apellidos': emp.apellidos,
        'id_area': emp.id_area,
        'area_name': emp.area.nombre_area if emp.area else None,
        'puesto': emp.puesto,
        # Ocultar salario para empleados que no son admin
        'salario': float(emp.salario) if emp.salario and current_user.rol == 'admin' else None,
        'fecha_contratacion': emp.fecha_contratacion.isoformat() if emp.fecha_contratacion else None,
        'activo': emp.activo
    } for emp in employees if emp is not None])

@employees_bp.route('/employees/me', methods=['GET'])
@login_required
def get_my_profile():
    """Endpoint especial para que cualquier empleado vea su propio perfil"""
    if not current_user.id_empleado:
        return jsonify({"error": "Perfil no encontrado"}), 404
    
    employee = Empleado.query.get(current_user.id_empleado)
    if not employee:
        return jsonify({"error": "Perfil no encontrado"}), 404
        
    return jsonify({
        'id_empleado': employee.id_empleado,
        'nombre': employee.nombre,
        'apellidos': employee.apellidos,
        'id_area': employee.id_area,
        'area_name': employee.area.nombre_area if employee.area else None,
        'puesto': employee.puesto,
        'fecha_contratacion': employee.fecha_contratacion.isoformat() if employee.fecha_contratacion else None,
        'activo': employee.activo
        # No incluir salario en el propio perfil a menos que sea necesario
    })

@employees_bp.route('/employees', methods=['POST'])
@role_required('admin')  # Solo admin puede crear nuevos empleados
def create_employee():
    data = request.get_json()
    
    # Validaciones básicas
    required_fields = ['nombre', 'apellidos']
    missing = [field for field in required_fields if field not in data]
    if missing:
        return jsonify({"error": f"Faltan campos obligatorios: {', '.join(missing)}"}), 400

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
    return jsonify({
        'message': 'Empleado creado exitosamente',
        'id_empleado': new_employee.id_empleado
    }), 201

@employees_bp.route('/employees/<int:id>', methods=['PUT'])
@login_required
def update_employee(id):
    employee = Empleado.query.get_or_404(id)
    
    # Solo admin puede editar cualquier empleado
    # Supervisor solo puede editar empleados de su área
    # Empleado no puede editar información de otros
    if current_user.rol == 'supervisor':
        supervisor = Empleado.query.get(current_user.id_empleado)
        if not supervisor or employee.id_area != supervisor.id_area:
            return jsonify({"error": "No autorizado"}), 403
    elif current_user.rol == 'empleado':
        if employee.id_empleado != current_user.id_empleado:
            return jsonify({"error": "No autorizado"}), 403

    data = request.get_json()
    
    # Restringir qué campos pueden editar según el rol
    if current_user.rol == 'admin':
        employee.nombre = data.get('nombre', employee.nombre)
        employee.apellidos = data.get('apellidos', employee.apellidos)
        employee.id_area = data.get('id_area', employee.id_area)
        employee.puesto = data.get('puesto', employee.puesto)
        employee.salario = data.get('salario', employee.salario)
        if 'fecha_contratacion' in data:
            employee.fecha_contratacion = datetime.strptime(data['fecha_contratacion'], '%Y-%m-%d')
        employee.activo = data.get('activo', employee.activo)
    elif current_user.rol == 'supervisor':
        # Supervisor solo puede actualizar ciertos campos
        employee.puesto = data.get('puesto', employee.puesto)
        if 'activo' in data:
            employee.activo = data['activo']
    elif current_user.rol == 'empleado':
        # Empleado solo puede actualizar su información básica
        employee.nombre = data.get('nombre', employee.nombre)
        employee.apellidos = data.get('apellidos', employee.apellidos)

    db.session.commit()
    return jsonify({'message': 'Empleado actualizado exitosamente'})

@employees_bp.route('/employees/<int:id>', methods=['DELETE'])
@role_required('admin')  # Solo admin puede eliminar empleados
def delete_employee(id):
    employee = Empleado.query.get_or_404(id)
    
    # Verificar si el empleado tiene registros asociados
    # (asistencias, incidentes, etc.) antes de eliminar
    # Esto dependerá de tu modelo de datos
    
    db.session.delete(employee)
    db.session.commit()
    return jsonify({'message': 'Empleado eliminado exitosamente'})

@employees_bp.route('/employees/<int:id>', methods=['GET'])
@login_required
def get_employee(id):
    employee = Empleado.query.get_or_404(id)
    
    # Control de acceso para ver perfiles
    if current_user.rol == 'supervisor':
        supervisor = Empleado.query.get(current_user.id_empleado)
        if not supervisor or employee.id_area != supervisor.id_area:
            return jsonify({"error": "No autorizado"}), 403
    elif current_user.rol == 'empleado':
        if employee.id_empleado != current_user.id_empleado:
            return jsonify({"error": "No autorizado"}), 403

    return jsonify({
        'id_empleado': employee.id_empleado,
        'nombre': employee.nombre,
        'apellidos': employee.apellidos,
        'id_area': employee.id_area,
        'area_name': employee.area.nombre_area if employee.area else None,
        'puesto': employee.puesto,
        'salario': float(employee.salario) if employee.salario and current_user.rol == 'admin' else None,
        'fecha_contratacion': employee.fecha_contratacion.isoformat() if employee.fecha_contratacion else None,
        'activo': employee.activo
    })