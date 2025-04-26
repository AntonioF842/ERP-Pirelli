from backend.models import DetalleOrdenCompra
from backend.config import db

def list_purchase_orders_details():
    """
    Retrieves all records from detalle_ordenes_compra and returns them as a list of dictionaries.
    """
    purchase_order_details = DetalleOrdenCompra.query.all()
    result = []
    for purchase_order_detail in purchase_order_details:
        result.append({
            'id_detail': purchase_order_detail.id_detalle,
            'purchase_order_id': purchase_order_detail.id_orden_compra,
            'material_id': purchase_order_detail.id_material,
            'quantity': purchase_order_detail.cantidad,
            'unit_price': float(purchase_order_detail.precio_unitario),
            'subtotal': float(purchase_order_detail.subtotal)
        })
    return result