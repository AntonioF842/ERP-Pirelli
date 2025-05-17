from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from routes.auth import role_required
from models import RecetaProduccion, Producto, Material, db

production_recipes_bp = Blueprint('production_recipes', __name__)

@production_recipes_bp.route('/production_recipes', methods=['GET'])
@login_required
def get_production_recipes():
    """Obtiene todas las recetas de producción"""
    # Admin y Supervisor ven todas las recetas
    if current_user.rol in ['admin', 'supervisor']:
        recipes = RecetaProduccion.query.all()
    # Empleados solo ven recetas de productos activos
    elif current_user.rol == 'empleado':
        recipes = RecetaProduccion.query.join(Producto).filter(Producto.activo == True).all()
    else:
        return jsonify({"error": "No autorizado"}), 403

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
    # Todos los roles pueden ver materiales pero con diferente nivel de detalle
    materials = Material.query.all()
    
    response_data = []
    for material in materials:
        material_data = {
            'id_material': material.id_material,
            'nombre': material.nombre,
            'unidad_medida': material.unidad_medida
        }
        
        # Solo admin y supervisor ven detalles completos
        if current_user.rol in ['admin', 'supervisor']:
            material_data.update({
                'descripcion': material.descripcion,
                'stock_minimo': material.stock_minimo,
                'stock_maximo': material.stock_maximo
            })
            
        response_data.append(material_data)
    
    return jsonify(response_data)

@production_recipes_bp.route('/production_recipes', methods=['POST'])
@role_required('admin', 'supervisor')  # Solo admin y supervisor pueden crear
def create_production_recipe():
    """Crea una nueva receta de producción"""
    data = request.json
    
    # Validaciones
    if not all(key in data for key in ['id_producto', 'id_material', 'cantidad']):
        return jsonify({"error": "Faltan campos requeridos"}), 400
        
    producto = Producto.query.get(data.get('id_producto'))
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404
        
    material = Material.query.get(data.get('id_material'))
    if not material:
        return jsonify({"error": "Material no encontrado"}), 404
    
    try:
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
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@production_recipes_bp.route('/production_recipes/<int:id>', methods=['PUT'])
@role_required('admin', 'supervisor')  # Solo admin y supervisor pueden actualizar
def update_production_recipe(id):
    """Actualiza una receta de producción existente"""
    recipe = RecetaProduccion.query.get_or_404(id)
    data = request.get_json()
    
    try:
        if 'id_producto' in data:
            producto = Producto.query.get(data['id_producto'])
            if not producto:
                return jsonify({"error": "Producto no encontrado"}), 404
            recipe.id_producto = data['id_producto']
            
        if 'id_material' in data:
            material = Material.query.get(data['id_material'])
            if not material:
                return jsonify({"error": "Material no encontrado"}), 404
            recipe.id_material = data['id_material']
            
        if 'cantidad' in data:
            recipe.cantidad = data['cantidad']
            
        db.session.commit()
        return jsonify({'message': 'Receta de producción actualizada correctamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@production_recipes_bp.route('/production_recipes/<int:id>', methods=['DELETE'])
@role_required('admin')  # Solo admin puede eliminar
def delete_production_recipe(id):
    """Elimina una receta de producción"""
    recipe = RecetaProduccion.query.get_or_404(id)
    
    try:
        db.session.delete(recipe)
        db.session.commit()
        return jsonify({'message': 'Receta de producción eliminada correctamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500