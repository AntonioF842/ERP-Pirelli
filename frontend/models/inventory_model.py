from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import date

@dataclass
class Producto:
    id_producto: int
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    precio: float = 0.0
    categoria: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Producto':
        return cls(
            id_producto=data.get('id_producto'),
            codigo=data.get('codigo'),
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion'),
            precio=float(data.get('precio', 0)),
            categoria=data.get('categoria')
        )

@dataclass
class Inventario:
    id_inventario: int
    id_producto: int
    cantidad: int
    fecha_actualizacion: Optional[date] = None
    producto: Optional[Producto] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Inventario':
        fecha = data.get('fecha_actualizacion')
        if isinstance(fecha, str):
            try:
                fecha = date.fromisoformat(fecha)
            except Exception:
                fecha = None
        return cls(
            id_inventario=data.get('id_inventario'),
            id_producto=data.get('id_producto'),
            cantidad=int(data.get('cantidad', 0)),
            fecha_actualizacion=fecha,
            producto=Producto.from_dict(data.get('producto')) if data.get('producto') else None
        )