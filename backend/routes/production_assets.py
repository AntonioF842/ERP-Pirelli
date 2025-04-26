from flask import Blueprint, jsonify, request
from models import ActivoProduccion, AreaTrabajo, db
from datetime import datetime

production_assets_bp = Blueprint('production_assets', __name__)

@production_assets_bp.route('/production_assets', methods=['GET'])
def get_production_assets():
    assets = ActivoProduccion.query.all()
    return jsonify([{
        'id_activo': asset.id_activo,
        'nombre': asset.nombre,
        'tipo': asset.tipo,
        'id_area': asset.id_area,
        'area_name': asset.area.nombre_area if asset.area else None,
        'fecha_adquisicion': asset.fecha_adquisicion.isoformat() if asset.fecha_adquisicion else None,
        'estado': asset.estado
    } for asset in assets])

@production_assets_bp.route('/production_assets', methods=['POST'])
def create_production_asset():
    data = request.get_json()
    new_asset = ActivoProduccion(
        nombre=data['nombre'],
        tipo=data['tipo'],
        id_area=data.get('id_area'),
        fecha_adquisicion=datetime.strptime(data['fecha_adquisicion'], '%Y-%m-%d').date() if 'fecha_adquisicion' in data else None,
        estado=data.get('estado', 'operativo')
    )
    db.session.add(new_asset)
    db.session.commit()
    return jsonify({'message': 'Production asset created successfully'}), 201

@production_assets_bp.route('/production_assets/<int:id>', methods=['PUT'])
def update_production_asset(id):
    asset = ActivoProduccion.query.get_or_404(id)
    data = request.get_json()
    asset.nombre = data.get('nombre', asset.nombre)
    asset.tipo = data.get('tipo', asset.tipo)
    asset.id_area = data.get('id_area', asset.id_area)
    if 'fecha_adquisicion' in data:
        asset.fecha_adquisicion = datetime.strptime(data['fecha_adquisicion'], '%Y-%m-%d').date()
    asset.estado = data.get('estado', asset.estado)
    db.session.commit()
    return jsonify({'message': 'Production asset updated successfully'})

@production_assets_bp.route('/production_assets/<int:id>', methods=['DELETE'])
def delete_production_asset(id):
    asset = ActivoProduccion.query.get_or_404(id)
    db.session.delete(asset)
    db.session.commit()
    return jsonify({'message': 'Production asset deleted successfully'})