# users.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from routes.auth import role_required
from models import Usuario, db

users_bp = Blueprint('users_bp', __name__)

# Roles permitidos para cada acción
ADMIN_ONLY = ['admin']
ADMIN_SUPERVISOR = ['admin', 'supervisor']
VALID_ROLES = ['admin', 'supervisor', 'empleado']

@users_bp.route('/users', methods=['GET'])
@role_required('admin', 'supervisor')  # Solo admin y supervisor pueden listar usuarios
def get_users():
    # Admin ve todos los usuarios
    if current_user.rol == 'admin':
        users = Usuario.query.all()
    # Supervisor ve solo empleados (no otros supervisores ni admins)
    else:
        users = Usuario.query.filter_by(rol='empleado').all()
    
    users_list = [{
        "id_usuario": u.id_usuario, 
        "nombre": u.nombre, 
        "email": u.email, 
        "rol": u.rol, 
        "fecha_registro": u.fecha_registro
    } for u in users]
    
    return jsonify(users_list)

@users_bp.route('/users/<int:id>', methods=['GET'])
@login_required
def get_user(id):
    user = Usuario.query.get_or_404(id)
    
    # Reglas de acceso:
    # 1. Admin puede ver cualquier usuario
    # 2. Supervisor solo puede ver empleados
    # 3. Empleados solo pueden verse a sí mismos
    if current_user.rol == 'supervisor' and user.rol != 'empleado':
        return jsonify({"error": "No autorizado"}), 403
    elif current_user.rol == 'empleado' and user.id_usuario != current_user.id_usuario:
        return jsonify({"error": "No autorizado"}), 403
    
    return jsonify({
        "id_usuario": user.id_usuario,
        "nombre": user.nombre,
        "email": user.email,
        "rol": user.rol,
        "fecha_registro": user.fecha_registro
    })

@users_bp.route('/users', methods=['POST'])
@role_required('admin')  # Solo admin puede crear usuarios
def create_user():
    data = request.json
    
    # Validaciones
    if not all(field in data for field in ['nombre', 'email', 'password', 'rol']):
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    
    if data['rol'] not in VALID_ROLES:
        return jsonify({"error": "Rol no válido"}), 400
    
    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({"error": "El email ya está registrado"}), 400
    
    new_user = Usuario(
        nombre=data['nombre'],
        email=data['email'],
        rol=data['rol']
    )
    new_user.set_password(data['password'])
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        "message": "Usuario creado exitosamente",
        "id_usuario": new_user.id_usuario
    }), 201

@users_bp.route('/users/<int:id>', methods=['PUT'])
@login_required
def update_user(id):
    user = Usuario.query.get_or_404(id)
    data = request.json
    
    # Reglas de acceso:
    # 1. Admin puede editar cualquier usuario
    # 2. Supervisor solo puede editar empleados
    # 3. Empleados solo pueden editar su propia información (excepto rol)
    if current_user.rol == 'supervisor' and user.rol != 'empleado':
        return jsonify({"error": "No autorizado"}), 403
    elif current_user.rol == 'empleado' and user.id_usuario != current_user.id_usuario:
        return jsonify({"error": "No autorizado"}), 403
    
    # Validaciones
    if 'email' in data and Usuario.query.filter(Usuario.email == data['email'], Usuario.id_usuario != id).first():
        return jsonify({"error": "El email ya está en uso"}), 400
    
    # Empleados no pueden cambiar su rol
    if current_user.rol == 'empleado' and 'rol' in data:
        return jsonify({"error": "No puedes cambiar tu rol"}), 403
    
    # Supervisores no pueden cambiar roles a admin
    if current_user.rol == 'supervisor' and 'rol' in data and data['rol'] == 'admin':
        return jsonify({"error": "No autorizado para asignar este rol"}), 403
    
    user.nombre = data.get('nombre', user.nombre)
    user.email = data.get('email', user.email)
    
    if 'rol' in data and current_user.rol == 'admin':
        user.rol = data['rol']
    
    if 'password' in data and data['password']:
        user.set_password(data['password'])
    
    db.session.commit()
    return jsonify({"message": "Usuario actualizado"})

@users_bp.route('/users/<int:id>', methods=['DELETE'])
@role_required('admin')  # Solo admin puede eliminar usuarios
def delete_user(id):
    user = Usuario.query.get_or_404(id)
    
    # No permitir eliminarse a sí mismo
    if user.id_usuario == current_user.id_usuario:
        return jsonify({"error": "No puedes eliminarte a ti mismo"}), 400
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Usuario eliminado"})