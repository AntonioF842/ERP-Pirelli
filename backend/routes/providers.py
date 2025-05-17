from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from routes.auth import role_required
from models import Proveedor, db

providers_bp = Blueprint('providers_bp', __name__)

@providers_bp.route('/providers', methods=['GET'])
@login_required
def get_providers():
    # Admin y Supervisor ven todos los proveedores
    if current_user.rol in ['admin', 'supervisor']:
        proveedores = Proveedor.query.all()
    # Empleados solo ven proveedores activos
    elif current_user.rol == 'empleado':
        proveedores = Proveedor.query.filter_by(activo=True).all()
    else:
        return jsonify({'error': 'No autorizado'}), 403

    return jsonify([{
        'id': p.id_proveedor,
        'name': p.nombre,
        'contact': p.contacto,
        'phone': p.telefono,
        'email': p.email,
        'address': p.direccion,
        'material_type': p.tipo_material,
        'active': p.activo  # Asegúrate de que tu modelo tenga este campo
    } for p in proveedores])

@providers_bp.route('/providers', methods=['POST'])
@role_required('admin', 'supervisor')  # Solo admin y supervisor pueden crear
def create_provider():
    data = request.get_json()
    
    # Validaciones básicas
    required_fields = ['nombre', 'email', 'tipo_material']
    missing = [field for field in required_fields if field not in data]
    if missing:
        return jsonify({'error': f'Faltan campos obligatorios: {", ".join(missing)}'}), 400

    nuevo_proveedor = Proveedor(
        nombre=data['nombre'],
        contacto=data.get('contacto', ''),
        telefono=data.get('telefono', ''),
        email=data['email'],
        direccion=data.get('direccion', ''),
        tipo_material=data['tipo_material'],
        activo=data.get('activo', True)
    )
    
    db.session.add(nuevo_proveedor)
    db.session.commit()
    return jsonify({
        'message': 'Proveedor creado exitosamente',
        'id': nuevo_proveedor.id_proveedor
    }), 201

@providers_bp.route('/providers/<int:id>', methods=['PUT'])
@role_required('admin', 'supervisor')  # Solo admin y supervisor pueden actualizar
def update_provider(id):
    proveedor = Proveedor.query.get_or_404(id)
    data = request.get_json()
    
    # Campos que no deberían ser modificables
    protected_fields = ['id_proveedor']
    for field in protected_fields:
        if field in data:
            return jsonify({'error': f'No se puede modificar el campo {field}'}), 400

    # Actualizar campos permitidos
    update_fields = ['nombre', 'contacto', 'telefono', 'email', 'direccion', 'tipo_material', 'activo']
    for key in update_fields:
        if key in data:
            setattr(proveedor, key, data[key])

    db.session.commit()
    return jsonify({'message': 'Proveedor actualizado exitosamente'})

@providers_bp.route('/providers/<int:id>', methods=['DELETE'])
@role_required('admin')  # Solo admin puede eliminar
def delete_provider(id):
    proveedor = Proveedor.query.get_or_404(id)
    
    # Verificar si el proveedor tiene materiales asociados
    if hasattr(proveedor, 'materiales') and len(proveedor.materiales) > 0:
        return jsonify({
            'error': 'No se puede eliminar el proveedor porque tiene materiales asociados',
            'solution': 'Desactívelo en lugar de eliminarlo'
        }), 400

    db.session.delete(proveedor)
    db.session.commit()
    return jsonify({'message': 'Proveedor eliminado exitosamente'})

@providers_bp.route('/providers/<int:id>/toggle-active', methods=['PATCH'])
@role_required('admin', 'supervisor')  # Solo admin y supervisor pueden desactivar
def toggle_active_provider(id):
    proveedor = Proveedor.query.get_or_404(id)
    proveedor.activo = not proveedor.activo
    db.session.commit()
    return jsonify({
        'message': 'Estado del proveedor actualizado',
        'active': proveedor.activo
    })