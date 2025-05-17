from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from routes.auth import role_required
from models import Proveedor, db

suppliers_bp = Blueprint('suppliers', __name__)

@suppliers_bp.route('', methods=['GET'])
@login_required
def get_suppliers():
    # Admin y Supervisor ven todos los proveedores
    if current_user.rol in ['admin', 'supervisor']:
        suppliers = Proveedor.query.all()
    # Empleados solo ven proveedores activos
    elif current_user.rol == 'empleado':
        suppliers = Proveedor.query.filter_by(activo=True).all()
    else:
        return jsonify({"error": "No autorizado"}), 403

    return jsonify([{
        'id_proveedor': sup.id_proveedor,
        'nombre': sup.nombre,
        'contacto': sup.contacto,
        'telefono': sup.telefono,
        'email': sup.email,
        'direccion': sup.direccion,
        'tipo_material': sup.tipo_material,
        'activo': sup.activo if hasattr(sup, 'activo') else True
    } for sup in suppliers])

@suppliers_bp.route('', methods=['POST'])
@role_required('admin', 'supervisor')  # Solo admin y supervisor pueden crear
def create_supplier():
    data = request.get_json()
    
    # Validaciones básicas
    if not data.get('nombre'):
        return jsonify({'error': 'El nombre es obligatorio'}), 400
    if not data.get('tipo_material'):
        return jsonify({'error': 'El tipo de material es obligatorio'}), 400

    new_supplier = Proveedor(
        nombre=data['nombre'],
        contacto=data.get('contacto'),
        telefono=data.get('telefono'),
        email=data.get('email'),
        direccion=data.get('direccion'),
        tipo_material=data['tipo_material'],
        activo=data.get('activo', True)
    )
    
    db.session.add(new_supplier)
    db.session.commit()
    return jsonify({
        'message': 'Proveedor creado exitosamente',
        'id_proveedor': new_supplier.id_proveedor
    }), 201

@suppliers_bp.route('/<int:id>', methods=['PUT'])
@role_required('admin', 'supervisor')  # Solo admin y supervisor pueden actualizar
def update_supplier(id):
    supplier = Proveedor.query.get_or_404(id)
    data = request.get_json()
    
    # Validaciones
    if 'nombre' in data and not data['nombre']:
        return jsonify({'error': 'El nombre no puede estar vacío'}), 400
    if 'tipo_material' in data and not data['tipo_material']:
        return jsonify({'error': 'El tipo de material no puede estar vacío'}), 400

    supplier.nombre = data.get('nombre', supplier.nombre)
    supplier.contacto = data.get('contacto', supplier.contacto)
    supplier.telefono = data.get('telefono', supplier.telefono)
    supplier.email = data.get('email', supplier.email)
    supplier.direccion = data.get('direccion', supplier.direccion)
    supplier.tipo_material = data.get('tipo_material', supplier.tipo_material)
    
    if 'activo' in data:
        supplier.activo = data['activo']
    
    db.session.commit()
    return jsonify({'message': 'Proveedor actualizado exitosamente'})

@suppliers_bp.route('/<int:id>', methods=['DELETE'])
@role_required('admin')  # Solo admin puede eliminar
def delete_supplier(id):
    supplier = Proveedor.query.get_or_404(id)
    
    # Verificar si el proveedor tiene materiales asociados
    if hasattr(supplier, 'materiales') and len(supplier.materiales) > 0:
        return jsonify({
            'error': 'No se puede eliminar el proveedor porque tiene materiales asociados',
            'suggestion': 'Desactívelo en lugar de eliminarlo'
        }), 400

    db.session.delete(supplier)
    db.session.commit()
    return jsonify({'message': 'Proveedor eliminado exitosamente'})

@suppliers_bp.route('/<int:id>/toggle-status', methods=['PUT'])
@role_required('admin', 'supervisor')  # Solo admin y supervisor pueden cambiar estado
def toggle_supplier_status(id):
    supplier = Proveedor.query.get_or_404(id)
    supplier.activo = not supplier.activo
    db.session.commit()
    return jsonify({
        'message': 'Estado del proveedor actualizado',
        'activo': supplier.activo
    })