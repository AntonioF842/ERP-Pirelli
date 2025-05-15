from flask import Blueprint, jsonify, request
from models import ActivoProduccion, AreaTrabajo, db
from datetime import datetime

production_assets_bp = Blueprint('production_assets', __name__)

@production_assets_bp.route('/production_assets', methods=['GET'])
def get_production_assets():
    try:
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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@production_assets_bp.route('/production_assets/<int:id>', methods=['GET'])
def get_production_asset(id):
    try:
        asset = ActivoProduccion.query.get_or_404(id)
        return jsonify({
            'id_activo': asset.id_activo,
            'nombre': asset.nombre,
            'tipo': asset.tipo,
            'id_area': asset.id_area,
            'area_name': asset.area.nombre_area if asset.area else None,
            'fecha_adquisicion': asset.fecha_adquisicion.isoformat() if asset.fecha_adquisicion else None,
            'estado': asset.estado
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@production_assets_bp.route('/production_assets', methods=['POST'])
def create_production_asset():
    try:
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
        return jsonify({
            'id_activo': new_asset.id_activo,
            'nombre': new_asset.nombre,
            'tipo': new_asset.tipo,
            'id_area': new_asset.id_area,
            'area_name': new_asset.area.nombre_area if new_asset.area else None,
            'fecha_adquisicion': new_asset.fecha_adquisicion.isoformat() if new_asset.fecha_adquisicion else None,
            'estado': new_asset.estado
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@production_assets_bp.route('/production_assets/<int:id>', methods=['PUT'])
def update_production_asset(id):
    try:
        asset = ActivoProduccion.query.get_or_404(id)
        data = request.get_json()
        
        if 'nombre' in data:
            asset.nombre = data['nombre']
        if 'tipo' in data:
            asset.tipo = data['tipo']
        if 'id_area' in data:
            asset.id_area = data['id_area']
        if 'fecha_adquisicion' in data:
            asset.fecha_adquisicion = datetime.strptime(data['fecha_adquisicion'], '%Y-%m-%d').date()
        if 'estado' in data:
            asset.estado = data['estado']
            
        db.session.commit()
        return jsonify({
            'id_activo': asset.id_activo,
            'nombre': asset.nombre,
            'tipo': asset.tipo,
            'id_area': asset.id_area,
            'area_name': asset.area.nombre_area if asset.area else None,
            'fecha_adquisicion': asset.fecha_adquisicion.isoformat() if asset.fecha_adquisicion else None,
            'estado': asset.estado
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@production_assets_bp.route('/production_assets/<int:id>', methods=['DELETE'])
def delete_production_asset(id):
    try:
        asset = ActivoProduccion.query.get_or_404(id)
        db.session.delete(asset)
        db.session.commit()
        return jsonify({'message': 'Production asset deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
