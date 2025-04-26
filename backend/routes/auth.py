# backend/routes/auth.py
from flask import Blueprint, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import functools
from models import Usuario
from config import db, login_manager  # Importa db desde config

auth_bp = Blueprint('auth_bp', __name__)

@login_manager.user_loader
def load_user(user_id):
    """ Carga el usuario en la sesión """
    return Usuario.query.get(int(user_id))

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        required_fields = ['nombre', 'email', 'password', 'rol']
        
        # Validación de campos
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Faltan campos obligatorios"}), 400
        
        if len(data['password']) < 8:
            return jsonify({"error": "La contraseña debe tener al menos 8 caracteres"}), 400

        if Usuario.query.filter_by(email=data['email']).first():
            return jsonify({"error": "El email ya está registrado"}), 400

        # Validación de rol
        valid_roles = ['admin', 'supervisor', 'empleado']
        if data['rol'] not in valid_roles:
            return jsonify({"error": "Rol no válido"}), 400

        user = Usuario(
            nombre=data['nombre'],
            email=data['email'],
            rol=data['rol']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            "message": "Usuario registrado exitosamente",
            "user": {
                "id": user.id_usuario,
                "nombre": user.nombre,
                "email": user.email,
                "rol": user.rol
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ✅ 2️⃣ INICIO DE SESIÓN
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = Usuario.query.filter_by(email=data['email']).first()
    
    print(f"Debug - User type: {type(user)}")  # Debería ser <class 'models.Usuario'>
    print(f"Debug - User ID: {user.id_usuario if user else 'No user'}")  # Verifica el ID
    
    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify({"message": "Login exitoso", "rol": user.rol})
    
    return jsonify({"error": "Credenciales incorrectas"}), 401

# ✅ 3️⃣ CIERRE DE SESIÓN
@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()  # Cierra la sesión del usuario
    return jsonify({"message": "Sesión cerrada correctamente"})

# ✅ 4️⃣ VERIFICACIÓN DEL USUARIO AUTENTICADO
@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """ Retorna la información del usuario autenticado """
    return jsonify({
        "id_usuario": current_user.id_usuario,
        "nombre": current_user.nombre,
        "email": current_user.email,
        "rol": current_user.rol
    })

# ✅ 5️⃣ RESTRICCIÓN POR ROLES
def role_required(*roles):
    """ Decorador para restringir acceso según el rol """
    def wrapper(func):
        @functools.wraps(func)
        @login_required
        def wrapped_function(*args, **kwargs):
            if current_user.rol not in roles:
                return jsonify({"error": "Acceso no autorizado"}), 403
            return func(*args, **kwargs)
        return wrapped_function
    return wrapper

# ✅ EJEMPLO DE USO DEL DECORADOR DE ROLES (PROTEGER UNA RUTA)
@auth_bp.route('/admin-only', methods=['GET'])
@role_required('admin')
def admin_only():
    """ Solo los administradores pueden acceder a esta ruta """
    return jsonify({"message": "Bienvenido, administrador"})
