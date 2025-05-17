from flask import Blueprint, jsonify, request, abort
from models import db, Material, Inventario
from routes.auth import role_required, login_required
from flask_login import current_user

# ¡Corrige el prefijo aquí!
materials_bp = Blueprint("materials", __name__, url_prefix="/api/materiales")

# GET /api/materiales - Listar todos los materiales
@materials_bp.route("", methods=["GET"])
@login_required
def get_materials():
    materiales = Material.query.all()
    result = [
        {
            "id_material": m.id_material,
            "nombre": m.nombre,
            "descripcion": m.descripcion,
            "unidad_medida": m.unidad_medida,
            "stock_minimo": m.stock_minimo,
            "stock_maximo": m.stock_maximo
        } for m in materiales
    ]
    return jsonify(result), 200

# GET /api/materiales/<id> - Obtener material puntual
@materials_bp.route("/<int:material_id>", methods=["GET"])
@login_required
def get_material(material_id):
    m = Material.query.get_or_404(material_id)
    data = {
        "id_material": m.id_material,
        "nombre": m.nombre,
        "descripcion": m.descripcion,
        "unidad_medida": m.unidad_medida,
        "stock_minimo": m.stock_minimo,
        "stock_maximo": m.stock_maximo
    }
    return jsonify(data), 200

# POST /api/materiales - Crear material
@materials_bp.route("", methods=["POST"])
@role_required("admin", "supervisor")
def create_material():
    data = request.json or {}
    nombre = data.get("nombre")
    if not nombre:
        abort(400, "Nombre es obligatorio")
    material = Material(
        nombre=nombre,
        descripcion=data.get("descripcion", ""),
        unidad_medida=data.get("unidad_medida", ""),
        stock_minimo=data.get("stock_minimo", 0),
        stock_maximo=data.get("stock_maximo", 0)
    )
    db.session.add(material)
    db.session.commit()
    return jsonify({"id_material": material.id_material}), 201

# PUT /api/materiales/<id> - Editar material
@materials_bp.route("/<int:material_id>", methods=["PUT"])
@role_required("admin", "supervisor")
def update_material(material_id):
    m = Material.query.get_or_404(material_id)
    data = request.json or {}
    m.nombre = data.get("nombre", m.nombre)
    m.descripcion = data.get("descripcion", m.descripcion)
    m.unidad_medida = data.get("unidad_medida", m.unidad_medida)
    m.stock_minimo = data.get("stock_minimo", m.stock_minimo)
    m.stock_maximo = data.get("stock_maximo", m.stock_maximo)
    db.session.commit()
    return jsonify({"message": "Material actualizado"}), 200

# DELETE /api/materiales/<id> - Eliminar material
@materials_bp.route("/<int:material_id>", methods=["DELETE"])
@role_required("admin", "supervisor")
def delete_material(material_id):
    m = Material.query.get_or_404(material_id)
    # Check for references in the inventory
    inventario_refs = db.session.query(db.exists().where(Inventario.id_material == m.id_material)).scalar()
    if inventario_refs:
        return jsonify({"error": "No se puede eliminar el material porque está referenciado en inventario."}), 400
    db.session.delete(m)
    db.session.commit()
    return jsonify({"message": "Material eliminado"}), 200