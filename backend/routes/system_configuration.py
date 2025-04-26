from flask import Blueprint, jsonify, request
from models import ConfiguracionSistema, db

system_configuration_bp = Blueprint('system_configuration', __name__)

@system_configuration_bp.route('/system_configuration', methods=['GET'])
def get_system_configurations():
    configs = ConfiguracionSistema.query.all()
    return jsonify([{
        'id_config': config.id_config,
        'parametro': config.parametro,
        'valor': config.valor,
        'descripcion': config.descripcion
    } for config in configs])

@system_configuration_bp.route('/system_configuration', methods=['POST'])
def create_system_configuration():
    data = request.get_json()
    new_config = ConfiguracionSistema(
        parametro=data['parametro'],
        valor=data.get('valor'),
        descripcion=data.get('descripcion')
    )
    db.session.add(new_config)
    db.session.commit()
    return jsonify({'message': 'System configuration created successfully'}), 201

@system_configuration_bp.route('/system_configuration/<int:id>', methods=['PUT'])
def update_system_configuration(id):
    config = ConfiguracionSistema.query.get_or_404(id)
    data = request.get_json()
    config.parametro = data.get('parametro', config.parametro)
    config.valor = data.get('valor', config.valor)
    config.descripcion = data.get('descripcion', config.descripcion)
    db.session.commit()
    return jsonify({'message': 'System configuration updated successfully'})

@system_configuration_bp.route('/system_configuration/<int:id>', methods=['DELETE'])
def delete_system_configuration(id):
    config = ConfiguracionSistema.query.get_or_404(id)
    db.session.delete(config)
    db.session.commit()
    return jsonify({'message': 'System configuration deleted successfully'})