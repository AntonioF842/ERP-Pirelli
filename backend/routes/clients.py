from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from routes.auth import role_required
from models import Cliente, db

clients_bp = Blueprint('clients_bp', __name__)

@clients_bp.route('/clientes', methods=['GET'])
@login_required
def get_clients():
    # Admin y Supervisor tienen acceso completo
    if current_user.rol in ['admin', 'supervisor']:
        clientes = Cliente.query.all()
    # Empleados solo ven clientes de su área o tipo específico
    elif current_user.rol == 'empleado':
        # Aquí puedes agregar lógica para filtrar clientes según el área del empleado
        # Por ejemplo, si los empleados solo ven clientes de tipo 'minorista'
        clientes = Cliente.query.filter_by(tipo='minorista').all()
    else:
        return jsonify({"error": "No autorizado"}), 403

    clientes_list = [{
        "id_cliente": c.id_cliente,
        "nombre": c.nombre,
        "contacto": c.contacto if c.contacto else "",
        "telefono": c.telefono if c.telefono else "",
        "email": c.email,
        "direccion": c.direccion if c.direccion else "",
        "tipo": c.tipo
    } for c in clientes]
    return jsonify(clientes_list)

@clients_bp.route('/clientes/<int:id>', methods=['GET'])
@login_required
def get_client(id):
    cliente = Cliente.query.get_or_404(id)
    
    # Empleados solo pueden ver clientes de tipo 'minorista'
    if current_user.rol == 'empleado' and cliente.tipo != 'minorista':
        return jsonify({"error": "No autorizado"}), 403
        
    return jsonify({
        "id_cliente": cliente.id_cliente,
        "nombre": cliente.nombre,
        "contacto": cliente.contacto if cliente.contacto else "",
        "telefono": cliente.telefono if cliente.telefono else "",
        "email": cliente.email,
        "direccion": cliente.direccion if cliente.direccion else "",
        "tipo": cliente.tipo
    })

@clients_bp.route('/clientes', methods=['POST'])
@role_required('admin', 'supervisor')  # Solo admin y supervisor pueden crear
def create_client():
    data = request.json
    
    # Validaciones básicas
    if not data.get('nombre'):
        return jsonify({"error": "El nombre es obligatorio"}), 400
    if not data.get('email'):
        return jsonify({"error": "El email es obligatorio"}), 400
    
    nuevo_cliente = Cliente(
        nombre=data['nombre'],
        contacto=data.get('contacto', ''),
        telefono=data.get('telefono', ''),
        email=data['email'],
        direccion=data.get('direccion', ''),
        tipo=data.get('tipo', 'distribuidor')
    )
    
    db.session.add(nuevo_cliente)
    db.session.commit()
    return jsonify({"message": "Cliente creado exitosamente", "id_cliente": nuevo_cliente.id_cliente}), 201

@clients_bp.route('/clientes/<int:id>', methods=['PUT'])
@role_required('admin', 'supervisor')  # Solo admin y supervisor pueden actualizar
def update_client(id):
    cliente = Cliente.query.get_or_404(id)
    data = request.json
    
    # Validaciones básicas
    if 'email' in data and not data['email']:
        return jsonify({"error": "El email no puede estar vacío"}), 400
    
    cliente.nombre = data.get('nombre', cliente.nombre)
    cliente.contacto = data.get('contacto', cliente.contacto)
    cliente.telefono = data.get('telefono', cliente.telefono)
    cliente.email = data.get('email', cliente.email)
    cliente.direccion = data.get('direccion', cliente.direccion)
    cliente.tipo = data.get('tipo', cliente.tipo)

    db.session.commit()
    return jsonify({"message": "Cliente actualizado"})

@clients_bp.route('/clientes/<int:id>', methods=['DELETE'])
@role_required('admin')  # Solo admin puede eliminar
def delete_client(id):
    cliente = Cliente.query.get_or_404(id)
    
    # Verificar si el cliente tiene órdenes de venta asociadas
    if hasattr(cliente, 'ventas') and len(cliente.ventas) > 0:
        return jsonify({"error": "No se puede eliminar el cliente porque tiene ventas asociadas"}), 400

    db.session.delete(cliente)
    db.session.commit()
    return jsonify({"message": "Cliente eliminado"})