# users.py
from flask import Blueprint, request, jsonify
from flask_login import login_required
from models import Usuario, db

users_bp = Blueprint('users_bp', __name__)

@users_bp.route('/users', methods=['GET'])
@login_required
def get_users():
    users = Usuario.query.all()
    users_list = [{"id_usuario": u.id_usuario, "nombre": u.nombre, "email": u.email, "rol": u.rol, "fecha_registro": u.fecha_registro} for u in users]
    return jsonify(users_list)

@users_bp.route('/users/<int:id>', methods=['GET'])
@login_required
def get_user(id):
    user = Usuario.query.get(id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify({"id_usuario": user.id_usuario, "nombre": user.nombre, "email": user.email, "rol": user.rol, "fecha_registro": user.fecha_registro})

@users_bp.route('/users', methods=['POST'])
@login_required
def create_user():
    data = request.json
    new_user = Usuario(nombre=data['nombre'], email=data['email'], rol=data['rol'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Usuario creado exitosamente", "id_usuario": new_user.id_usuario})

@users_bp.route('/users/<int:id>', methods=['PUT'])
@login_required
def update_user(id):
    user = Usuario.query.get(id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    data = request.json
    user.nombre = data.get('nombre', user.nombre)
    user.email = data.get('email', user.email)
    user.rol = data.get('rol', user.rol)
    
    if 'password' in data and data['password']:
        user.set_password(data['password'])

    db.session.commit()
    return jsonify({"message": "Usuario actualizado"})

@users_bp.route('/users/<int:id>', methods=['DELETE'])
@login_required
def delete_user(id):
    user = Usuario.query.get(id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Usuario eliminado"})