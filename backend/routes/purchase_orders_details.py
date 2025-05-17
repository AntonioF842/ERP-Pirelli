from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from routes.auth import role_required
from models import DetalleOrdenCompra, Material, OrdenCompra
from config import db

# Crear el Blueprint
purchase_orders_details_bp = Blueprint(
    "purchase_orders_details",
    __name__,
    url_prefix="/api/ordenes_compra_detalle"
)

@purchase_orders_details_bp.route("/", methods=["GET"])
@login_required
def get_purchase_orders_details():
    """
    Endpoint para obtener todos los detalles de órdenes de compra.
    Acceso: Admin (completo), Supervisor (completo), Empleado (solo sus órdenes)
    """
    if current_user.rol in ['admin', 'supervisor']:
        purchase_order_details = DetalleOrdenCompra.query.all()
    elif current_user.rol == 'empleado':
        # Empleados solo ven detalles de órdenes que ellos crearon
        purchase_order_details = DetalleOrdenCompra.query.join(OrdenCompra).filter(
            OrdenCompra.id_empleado == current_user.id_empleado
        ).all()
    else:
        return jsonify({"error": "No autorizado"}), 403

    result = []
    for d in purchase_order_details:
        result.append({
            'id_detalle': d.id_detalle,
            'id_orden_compra': d.id_orden_compra,
            'id_material': d.id_material,
            'material_name': d.material.nombre if d.material else "",
            'cantidad': d.cantidad,
            'precio_unitario': float(d.precio_unitario) if d.precio_unitario else None,
            'subtotal': float(d.subtotal) if d.subtotal else None
        })
    return jsonify(result), 200

@purchase_orders_details_bp.route("/<int:detalle_id>", methods=["GET"])
@login_required
def get_purchase_order_detail(detalle_id):
    """
    Endpoint para obtener un detalle de orden de compra por su ID.
    Acceso: Admin (completo), Supervisor (completo), Empleado (solo sus órdenes)
    """
    d = DetalleOrdenCompra.query.get_or_404(detalle_id)
    
    # Verificar acceso para empleados
    if current_user.rol == 'empleado':
        orden = OrdenCompra.query.get(d.id_orden_compra)
        if not orden or orden.id_empleado != current_user.id_empleado:
            return jsonify({"error": "No autorizado"}), 403

    return jsonify({
        'id_detalle': d.id_detalle,
        'id_orden_compra': d.id_orden_compra,
        'id_material': d.id_material,
        'material_name': d.material.nombre if d.material else "",
        'cantidad': d.cantidad,
        'precio_unitario': float(d.precio_unitario) if d.precio_unitario else None,
        'subtotal': float(d.subtotal) if d.subtotal else None
    })

@purchase_orders_details_bp.route("/", methods=["POST"])
@role_required('admin', 'supervisor', 'empleado')  # Todos pueden crear, con validaciones
def create_purchase_order_detail():
    """
    Endpoint para crear un nuevo detalle de orden de compra.
    Acceso: Admin, Supervisor, Empleado (con restricciones)
    """
    data = request.get_json()
    required_fields = ["id_orden_compra", "id_material", "cantidad"]
    for field in required_fields:
        if field not in data:
            abort(400, description=f"Campo requerido faltante: {field}")

    # Validar que la orden pertenezca al empleado (si es empleado)
    if current_user.rol == 'empleado':
        orden = OrdenCompra.query.get(data["id_orden_compra"])
        if not orden or orden.id_empleado != current_user.id_empleado:
            return jsonify({"error": "No autorizado para modificar esta orden"}), 403

    new_detail = DetalleOrdenCompra(
        id_orden_compra=data["id_orden_compra"],
        id_material=data["id_material"],
        cantidad=data["cantidad"],
        precio_unitario=data.get("precio_unitario"),
        subtotal=data.get("subtotal")
    )
    db.session.add(new_detail)
    db.session.commit()
    return jsonify({
        "message": "Detalle de orden de compra creado",
        "id_detalle": new_detail.id_detalle
    }), 201

@purchase_orders_details_bp.route("/<int:detalle_id>", methods=["PUT"])
@role_required('admin', 'supervisor', 'empleado')  # Todos pueden actualizar, con validaciones
def update_purchase_order_detail(detalle_id):
    """
    Endpoint para actualizar un detalle de orden de compra existente.
    Acceso: Admin, Supervisor, Empleado (solo sus órdenes)
    """
    d = DetalleOrdenCompra.query.get_or_404(detalle_id)
    
    # Validar acceso para empleados
    if current_user.rol == 'empleado':
        orden = OrdenCompra.query.get(d.id_orden_compra)
        if not orden or orden.id_empleado != current_user.id_empleado:
            return jsonify({"error": "No autorizado para modificar esta orden"}), 403

    data = request.get_json()
    
    d.id_material = data.get("id_material", d.id_material)
    d.cantidad = data.get("cantidad", d.cantidad)
    d.precio_unitario = data.get("precio_unitario", d.precio_unitario)
    d.subtotal = data.get("subtotal", d.subtotal)
    
    db.session.commit()
    return jsonify({"message": "Detalle actualizado correctamente"})

@purchase_orders_details_bp.route("/<int:detalle_id>", methods=["DELETE"])
@role_required('admin', 'supervisor')  # Solo admin y supervisor pueden eliminar
def delete_purchase_order_detail(detalle_id):
    """
    Endpoint para eliminar un detalle de orden de compra.
    Acceso: Admin, Supervisor
    """
    d = DetalleOrdenCompra.query.get_or_404(detalle_id)
    db.session.delete(d)
    db.session.commit()
    return jsonify({"message": "Detalle eliminado correctamente"})

@login_required
def list_purchase_orders_details():
    """
    Retrieves all records from detalle_ordenes_compra and returns them as a list of dictionaries.
    Acceso: Admin (completo), Supervisor (completo), Empleado (solo sus órdenes)
    """
    if current_user.rol in ['admin', 'supervisor']:
        purchase_order_details = DetalleOrdenCompra.query.all()
    elif current_user.rol == 'empleado':
        purchase_order_details = DetalleOrdenCompra.query.join(OrdenCompra).filter(
            OrdenCompra.id_empleado == current_user.id_empleado
        ).all()
    else:
        return []

    result = []
    for d in purchase_order_details:
        result.append({
            'id_detalle': d.id_detalle,
            'id_orden_compra': d.id_orden_compra,
            'id_material': d.id_material,
            'material_name': d.material.nombre if d.material else "",
            'cantidad': d.cantidad,
            'precio_unitario': float(d.precio_unitario) if d.precio_unitario else None,
            'subtotal': float(d.subtotal) if d.subtotal else None
        })
    return result