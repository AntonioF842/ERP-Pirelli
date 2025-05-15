"""
Modelo de datos para órdenes de producción
"""

class ProductionOrder:
    ESTADOS = {
        "planificada": "Planificada",
        "en_proceso": "En Proceso",
        "completada": "Completada",
        "cancelada": "Cancelada"
    }
    
    def __init__(self, 
                 id_orden_produccion=None, 
                 id_producto=None,
                 producto=None,
                 cantidad=None,
                 fecha_inicio=None,
                 fecha_fin=None,
                 estado="planificada",
                 id_usuario=None,
                 usuario=None):
        self.id_orden_produccion = id_orden_produccion
        self.id_producto = id_producto
        self.producto = producto or {}
        self.cantidad = int(cantidad) if cantidad else 0
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.estado = estado
        self.id_usuario = id_usuario
        self.usuario = usuario or {}
    
    @classmethod
    def from_dict(cls, data):
        from datetime import datetime
        
        # Convertir strings de fecha a objetos date si es necesario
        fecha_inicio = data.get('fecha_inicio')
        if isinstance(fecha_inicio, str):
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                fecha_inicio = None
        
        fecha_fin = data.get('fecha_fin')
        if isinstance(fecha_fin, str):
            try:
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                fecha_fin = None
        
        return cls(
            id_orden_produccion=data.get('id_orden_produccion'),
            id_producto=data.get('id_producto'),
            producto=data.get('producto', {}),
            cantidad=data.get('cantidad'),
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado=data.get('estado', 'planificada'),
            id_usuario=data.get('id_usuario'),
            usuario=data.get('usuario', {})
        )
    
    def to_dict(self):
        return {
            'id_orden_produccion': self.id_orden_produccion,
            'id_producto': self.id_producto,
            'cantidad': self.cantidad,
            'fecha_inicio': self.fecha_inicio.strftime('%Y-%m-%d') if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.strftime('%Y-%m-%d') if self.fecha_fin else None,
            'estado': self.estado,
            'id_usuario': self.id_usuario
        }
    
    def get_estado_display(self):
        """
        Obtiene el nombre para mostrar del estado
        
        Returns:
            str: Nombre del estado para mostrar
        """
        return self.ESTADOS.get(self.estado, "Desconocido")
    
    @staticmethod
    def get_estados_lista():
        """
        Obtiene la lista de estados para mostrar en un combo box
        
        Returns:
            list: Lista de tuplas (valor, display)
        """
        return [(k, v) for k, v in ProductionOrder.ESTADOS.items()]