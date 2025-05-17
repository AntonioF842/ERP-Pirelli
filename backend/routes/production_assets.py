from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from routes.auth import role_required
from models import ActivoProduccion, AreaTrabajo, db
from datetime import datetime

production_assets_bp = Blueprint('production_assets', __name__)

@production_assets_bp.route('/production_assets', methods=['GET'])
@login_required
def get_production_assets():
    try:
        # Admin y Supervisor ven todos los activos
        if current_user.rol in ['admin', 'supervisor']:
            assets = ActivoProduccion.query.all()
        # Empleados solo ven activos de su área
        elif current_user.rol == 'empleado':
            # Asume que current_user tiene id_area o relación con área
            assets = ActivoProduccion.query.filter_by(id_area=current_user.id_area).all()
        else:
            return jsonify({'error': 'No autorizado'}), 403

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
@login_required
def get_production_asset(id):
    try:
        asset = ActivoProduccion.query.get_or_404(id)
        
        # Empleados solo pueden ver activos de su área
        if current_user.rol == 'empleado' and asset.id_area != current_user.id_area:
            return jsonify({'error': 'No autorizado'}), 403
            
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
@role_required('admin', 'supervisor')  # Solo admin y supervisor pueden crear
def create_production_asset():
    try:
        data = request.get_json()
        
        # Validación de campos obligatorios
        if not data.get('nombre') or not data.get('tipo'):
            return jsonify({'error': 'Nombre y tipo son campos obligatorios'}), 400
            
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
@role_required('admin', 'supervisor')  # Solo admin y supervisor pueden actualizar
def update_production_asset(id):
    try:
        asset = ActivoProduccion.query.get_or_404(id)
        data = request.get_json()
        
        # Validación de campos
        if 'nombre' in data and not data['nombre']:
            return jsonify({'error': 'El nombre no puede estar vacío'}), 400
        if 'tipo' in data and not data['tipo']:
            return jsonify({'error': 'El tipo no puede estar vacío'}), 400
            
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
@role_required('admin')  # Solo admin puede eliminar
def delete_production_asset(id):
    try:
        asset = ActivoProduccion.query.get_or_404(id)
        
        # Verificar si el activo tiene mantenimientos asociados
        if hasattr(asset, 'mantenimientos') and len(asset.mantenimientos) > 0:
            return jsonify({'error': 'No se puede eliminar el activo porque tiene mantenimientos asociados'}), 400

        db.session.delete(asset)
        db.session.commit()
        return jsonify({'message': 'Activo de producción eliminado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500