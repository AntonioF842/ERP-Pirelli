from flask import Blueprint, jsonify, request
from flask_login import login_required
from models import RecetaProduccion, Producto, Material, db

production_recipes_bp = Blueprint('production_recipes', __name__)

@production_recipes_bp.route('/production_recipes', methods=['GET'])
@login_required
def get_production_recipes():
    """Obtiene todas las recetas de producción"""
    recipes = RecetaProduccion.query.all()
    return jsonify([{
        'id_receta': recipe.id_receta,
        'id_producto': recipe.id_producto,
        'producto_name': recipe.producto.nombre if recipe.producto else '',
        'id_material': recipe.id_material,
        'material_name': recipe.material.nombre if recipe.material else '',
        'cantidad': float(recipe.cantidad)
    } for recipe in recipes])

@production_recipes_bp.route('/materials', methods=['GET'])
@login_required
def get_materials():
    """Obtiene todos los materiales"""
    materials = Material.query.all()
    return jsonify([{
        'id_material': material.id_material,
        'nombre': material.nombre,
        'descripcion': material.descripcion,
        'unidad_medida': material.unidad_medida,
        'stock_minimo': material.stock_minimo,
        'stock_maximo': material.stock_maximo
        # No incluimos stock ya que no existe en el modelo
    } for material in materials])

@production_recipes_bp.route('/production_recipes', methods=['POST'])
@login_required
def create_production_recipe():
    """Crea una nueva receta de producción"""
    data = request.json
    
    # Validar que existan el producto y el material
    producto = Producto.query.get(data.get('id_producto'))
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404
        
    material = Material.query.get(data.get('id_material'))
    if not material:
        return jsonify({"error": "Material no encontrado"}), 404
    
    new_recipe = RecetaProduccion(
        id_producto=data['id_producto'],
        id_material=data['id_material'],
        cantidad=data['cantidad']
    )
    
    db.session.add(new_recipe)
    db.session.commit()
    
    return jsonify({
        "message": "Receta de producción creada exitosamente",
        "id_receta": new_recipe.id_receta
    }), 201

@production_recipes_bp.route('/production_recipes/<int:id>', methods=['PUT'])
@login_required
def update_production_recipe(id):
    """Actualiza una receta de producción existente"""
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