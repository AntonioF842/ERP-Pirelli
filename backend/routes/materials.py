from flask import Blueprint, jsonify, request
from models import Material, db

materials_bp = Blueprint('materials', __name__)

@materials_bp.route('/materials', methods=['GET'])
def get_materials():
    materials = Material.query.all()
    return jsonify([{
        'id_material': mat.id_material,
        'nombre': mat.nombre,
        'descripcion': mat.descripcion,
        'unidad_medida': mat.unidad_medida,
        'stock_minimo': mat.stock_minimo,
        'stock_maximo': mat.stock_maximo
    } for mat in materials])

@materials_bp.route('/materials', methods=['POST'])
def create_material():
    data = request.get_json()
    new_material = Material(
        nombre=data['nombre'],
        descripcion=data.get('descripcion'),
        unidad_medida=data.get('unidad_medida'),
        stock_minimo=data.get('stock_minimo'),
        stock_maximo=data.get('stock_maximo')
    )
    db.session.add(new_material)
    db.session.commit()
    return jsonify({'message': 'Material created successfully'}), 201

@materials_bp.route('/materials/<int:id>', methods=['PUT'])
def update_material(id):
    material = Material.query.get_or_404(id)
    data = request.get_json()
    material.nombre = data.get('nombre', material.nombre)
    material.descripcion = data.get('descripcion', material.descripcion)
    material.unidad_medida = data.get('unidad_medida', material.unidad_medida)
    material.stock_minimo = data.get('stock_minimo', material.stock_minimo)
    material.stock_maximo = data.get('stock_maximo', material.stock_maximo)
    db.session.commit()
    return jsonify({'message': 'Material updated successfully'})

@materials_bp.route('/materials/<int:id>', methods=['DELETE'])
def delete_material(id):
    material = Material.query.get_or_404(id)
    db.session.delete(material)
    db.session.commit()
    return jsonify({'message': 'Material deleted successfully'})