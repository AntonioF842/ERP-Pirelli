from flask import Blueprint, jsonify, request
from models import RecetaProduccion, Producto, Material, db

production_recipes_bp = Blueprint('production_recipes', __name__)

@production_recipes_bp.route('/production_recipes', methods=['GET'])
def get_production_recipes():
    recipes = RecetaProduccion.query.all()
    return jsonify([{
        'id_receta': recipe.id_receta,
        'id_producto': recipe.id_producto,
        'producto_name': recipe.producto.nombre,
        'id_material': recipe.id_material,
        'material_name': recipe.material.nombre,
        'cantidad': float(recipe.cantidad)
    } for recipe in recipes])

@production_recipes_bp.route('/production_recipes', methods=['POST'])
def create_production_recipe():
    data = request.get_json()
    new_recipe = RecetaProduccion(
        id_producto=data['id_producto'],
        id_material=data['id_material'],
        cantidad=data['cantidad']
    )
    db.session.add(new_recipe)
    db.session.commit()
    return jsonify({'message': 'Production recipe created successfully'}), 201

@production_recipes_bp.route('/production_recipes/<int:id>', methods=['PUT'])
def update_production_recipe(id):
    recipe = RecetaProduccion.query.get_or_404(id)
    data = request.get_json()
    recipe.id_producto = data.get('id_producto', recipe.id_producto)
    recipe.id_material = data.get('id_material', recipe.id_material)
    recipe.cantidad = data.get('cantidad', recipe.cantidad)
    db.session.commit()
    return jsonify({'message': 'Production recipe updated successfully'})

@production_recipes_bp.route('/production_recipes/<int:id>', methods=['DELETE'])
def delete_production_recipe(id):
    recipe = RecetaProduccion.query.get_or_404(id)
    db.session.delete(recipe)
    db.session.commit()
    return jsonify({'message': 'Production recipe deleted successfully'})