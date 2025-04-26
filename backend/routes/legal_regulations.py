from flask import Blueprint, jsonify, request
from models import NormativaLegal, db
from datetime import datetime

legal_regulations_bp = Blueprint('legal_regulations', __name__)

@legal_regulations_bp.route('/legal_regulations', methods=['GET'])
def get_legal_regulations():
    regulations = NormativaLegal.query.all()
    return jsonify([{
        'id_normativa': reg.id_normativa,
        'nombre': reg.nombre,
        'tipo': reg.tipo,
        'descripcion': reg.descripcion,
        'fecha_actualizacion': reg.fecha_actualizacion.isoformat() if reg.fecha_actualizacion else None,
        'aplicable_a': reg.aplicable_a
    } for reg in regulations])

@legal_regulations_bp.route('/legal_regulations', methods=['POST'])
def create_legal_regulation():
    data = request.get_json()
    new_regulation = NormativaLegal(
        nombre=data['nombre'],
        tipo=data['tipo'],
        descripcion=data.get('descripcion'),
        fecha_actualizacion=datetime.strptime(data['fecha_actualizacion'], '%Y-%m-%d').date() if 'fecha_actualizacion' in data else None,
        aplicable_a=data.get('aplicable_a')
    )
    db.session.add(new_regulation)
    db.session.commit()
    return jsonify({'message': 'Legal regulation created successfully'}), 201

@legal_regulations_bp.route('/legal_regulations/<int:id>', methods=['PUT'])
def update_legal_regulation(id):
    regulation = NormativaLegal.query.get_or_404(id)
    data = request.get_json()
    regulation.nombre = data.get('nombre', regulation.nombre)
    regulation.tipo = data.get('tipo', regulation.tipo)
    regulation.descripcion = data.get('descripcion', regulation.descripcion)
    if 'fecha_actualizacion' in data:
        regulation.fecha_actualizacion = datetime.strptime(data['fecha_actualizacion'], '%Y-%m-%d').date()
    regulation.aplicable_a = data.get('aplicable_a', regulation.aplicable_a)
    db.session.commit()
    return jsonify({'message': 'Legal regulation updated successfully'})

@legal_regulations_bp.route('/legal_regulations/<int:id>', methods=['DELETE'])
def delete_legal_regulation(id):
    regulation = NormativaLegal.query.get_or_404(id)
    db.session.delete(regulation)
    db.session.commit()
    return jsonify({'message': 'Legal regulation deleted successfully'})