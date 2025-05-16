from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Dict, Any
from .sales_model import Venta, Producto

@dataclass
class DetalleVenta:
    id_detalle: int
    id_venta: int
    id_producto: int
    cantidad: int
    precio_unitario: float
    subtotal: float
    venta: Optional[Venta] = None
    producto: Optional[Producto] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DetalleVenta':
        venta_data = data.get('venta')
        producto_data = data.get('producto')
        
        return cls(
            id_detalle=data.get('id_detalle'),
            id_venta=data.get('id_venta'),
            id_producto=data.get('id_producto'),
            cantidad=data.get('cantidad'),
            precio_unitario=float(data.get('precio_unitario', 0)),
            subtotal=float(data.get('subtotal', 0)),
            venta=Venta.from_dict(venta_data) if venta_data else None,
            producto=Producto.from_dict(producto_data) if producto_data else None
        )