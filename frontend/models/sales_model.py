from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Dict, Any

@dataclass
class Cliente:
    id_cliente: int
    nombre: str
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    tipo: Optional[str] = None  # 'distribuidor', 'mayorista', 'minorista', 'OEM'
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Cliente':
        return cls(
            id_cliente=data.get('id_cliente'),
            nombre=data.get('nombre'),
            contacto=data.get('contacto'),
            telefono=data.get('telefono'),
            email=data.get('email'),
            direccion=data.get('direccion'),
            tipo=data.get('tipo')
        )

@dataclass
class Producto:
    id_producto: int
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    precio: float = 0.0
    categoria: Optional[str] = None  # 'automovil', 'motocicleta', 'camion', 'industrial'
    
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
class DetalleVenta:
    id_detalle: int
    id_venta: int
    id_producto: int
    cantidad: int
    precio_unitario: float
    subtotal: float
    producto: Optional[Producto] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DetalleVenta':
        return cls(
            id_detalle=data.get('id_detalle'),
            id_venta=data.get('id_venta'),
            id_producto=data.get('id_producto'),
            cantidad=data.get('cantidad'),
            precio_unitario=float(data.get('precio_unitario', 0)),
            subtotal=float(data.get('subtotal', 0)),
            producto=Producto.from_dict(data.get('producto')) if data.get('producto') else None
        )

@dataclass
class Venta:
    id_venta: int
    id_cliente: int
    fecha: date
    total: float
    estado: str  # 'pendiente', 'completada', 'cancelada'
    id_usuario: int
    cliente: Optional[Cliente] = None
    detalles: List[DetalleVenta] = None
    
    def __post_init__(self):
        if self.detalles is None:
            self.detalles = []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Venta':
        fecha = data.get('fecha')
        if isinstance(fecha, str):
            fecha = date.fromisoformat(fecha)
            
        venta = cls(
            id_venta=data.get('id_venta'),
            id_cliente=data.get('id_cliente'),
            fecha=fecha,
            total=float(data.get('total', 0)),
            estado=data.get('estado', 'pendiente'),
            id_usuario=data.get('id_usuario'),
            cliente=Cliente.from_dict(data.get('cliente')) if data.get('cliente') else None,
        )
        
        if data.get('detalles'):
            venta.detalles = [DetalleVenta.from_dict(detalle) for detalle in data.get('detalles')]
            
        return venta