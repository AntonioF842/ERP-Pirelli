from flask import Blueprint, request, jsonify
from flask_login import login_required
from models import Producto, db

products_bp = Blueprint('products_bp', __name__)

@products_bp.route('/products', methods=['GET'])
@login_required
def get_products():
    products = Producto.query.all()
    products_list = [{"id_producto": p.id_producto, "codigo": p.codigo, "nombre": p.nombre, "precio": p.precio, "categoria": p.categoria} for p in products]
    return jsonify(products_list)

@products_bp.route('/products/<int:id>', methods=['GET'])
@login_required
def get_product(id):
    product = Producto.query.get(id)
    if not product:
        return jsonify({"error": "Producto no encontrado"}), 404
    return jsonify({"id_producto": product.id_producto, "codigo": product.codigo, "nombre": product.nombre, "precio": product.precio, "categoria": product.categoria})

@products_bp.route('/products', methods=['POST'])
@login_required
def create_product():
    data = request.json
    new_product = Producto(
        codigo=data['codigo'],
        nombre=data['nombre'],
        descripcion=data.get('descripcion', ''),
        precio=data['precio'],
        categoria=data['categoria']
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Producto creado exitosamente"})

@products_bp.route('/products/<int:id>', methods=['PUT'])
@login_required
def update_product(id):
    product = Producto.query.get(id)
    if not product:
        return jsonify({"error": "Producto no encontrado"}), 404

    data = request.json
    product.codigo = data.get('codigo', product.codigo)
    product.nombre = data.get('nombre', product.nombre)
    product.descripcion = data.get('descripcion', product.descripcion)
    product.precio = data.get('precio', product.precio)
    product.categoria = data.get('categoria', product.categoria)

    db.session.commit()
    return jsonify({"message": "Producto actualizado"})

@products_bp.route('/products/<int:id>', methods=['DELETE'])
@login_required
def delete_product(id):
    product = Producto.query.get(id)
    if not product:
        return jsonify({"error": "Producto no encontrado"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Producto eliminado"})
