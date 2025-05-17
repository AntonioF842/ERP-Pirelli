from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from routes.auth import role_required
from models import ConfiguracionSistema, db

system_configuration_bp = Blueprint('system_configuration', __name__)

@system_configuration_bp.route('/system_configuration', methods=['GET'])
@login_required
def get_system_configurations():
    # Solo Admin puede ver todas las configuraciones
    if current_user.rol != 'admin':
        return jsonify({"error": "Acceso no autorizado"}), 403
    
    configs = ConfiguracionSistema.query.all()
    return jsonify([{
        'id_config': config.id_config,
        'parametro': config.parametro,
        'valor': config.valor,
        'descripcion': config.descripcion
    } for config in configs])

@system_configuration_bp.route('/system_configuration', methods=['POST'])
@role_required('admin')  # Solo Admin puede crear configuraciones
def create_system_configuration():
    data = request.get_json()
    
    # Validación básica
    if not data.get('parametro'):
        return jsonify({'error': 'El parámetro es obligatorio'}), 400
        
    new_config = ConfiguracionSistema(
        parametro=data['parametro'],
        valor=data.get('valor'),
        descripcion=data.get('descripcion')
    )
    
    try:
        db.session.add(new_config)
        db.session.commit()
        return jsonify({
            'message': 'System configuration created successfully',
            'id_config': new_config.id_config
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@system_configuration_bp.route('/system_configuration/<int:id>', methods=['PUT'])
@role_required('admin')  # Solo Admin puede actualizar configuraciones
def update_system_configuration(id):
    config = ConfiguracionSistema.query.get_or_404(id)
    data = request.get_json()
    
    try:
        config.parametro = data.get('parametro', config.parametro)
        config.valor = data.get('valor', config.valor)
        config.descripcion = data.get('descripcion', config.descripcion)
        db.session.commit()
        return jsonify({'message': 'System configuration updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@system_configuration_bp.route('/system_configuration/<int:id>', methods=['DELETE'])
@role_required('admin')  # Solo Admin puede eliminar configuraciones
def delete_system_configuration(id):
    config = ConfiguracionSistema.query.get_or_404(id)
    
    try:
        db.session.delete(config)
        db.session.commit()
        return jsonify({'message': 'System configuration deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500