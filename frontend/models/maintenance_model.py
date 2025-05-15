"""
Modelo de datos para mantenimiento
"""

class Maintenance:
    """Clase para representar registros de mantenimiento en el frontend"""
    
    TIPOS_MANTENIMIENTO = {
        "preventivo": "Preventivo",
        "correctivo": "Correctivo"
    }
    
    ESTADOS_ACTIVO = {
        "operativo": "Operativo",
        "mantenimiento": "En Mantenimiento",
        "baja": "Dado de Baja"
    }
    
    def __init__(self, 
                 id_mantenimiento=None,
                 id_activo=None,
                 activo_nombre=None,
                 tipo=None,
                 fecha=None,
                 descripcion=None,
                 costo=None,
                 id_empleado=None,
                 empleado_nombre=None):
        """
        Inicializa un nuevo objeto de mantenimiento
        
        Args:
            id_mantenimiento: ID único del registro
            id_activo: ID del activo asociado
            activo_nombre: Nombre del activo
            tipo: Tipo de mantenimiento ('preventivo', 'correctivo')
            fecha: Fecha del mantenimiento
            descripcion: Descripción del trabajo realizado
            costo: Costo del mantenimiento
            id_empleado: ID del empleado que realizó el mantenimiento
            empleado_nombre: Nombre del empleado
        """
        self.id_mantenimiento = id_mantenimiento
        self.id_activo = id_activo
        self.activo_nombre = activo_nombre
        self.tipo = tipo
        self.fecha = fecha
        self.descripcion = descripcion or "Sin descripción"
        self.costo = float(costo) if costo is not None else 0.0
        self.id_empleado = id_empleado
        self.empleado_nombre = empleado_nombre
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea un objeto Maintenance a partir de un diccionario
        
        Args:
            data: Diccionario con los datos del mantenimiento
            
        Returns:
            Maintenance: Objeto Maintenance
        """
        return cls(
            id_mantenimiento=data.get('id_mantenimiento'),
            id_activo=data.get('id_activo'),
            activo_nombre=data.get('activo_nombre', data.get('activo_name')),
            tipo=data.get('tipo'),
            fecha=data.get('fecha'),
            descripcion=data.get('descripcion'),
            costo=data.get('costo'),
            id_empleado=data.get('id_empleado'),
            empleado_nombre=data.get('empleado_nombre', data.get('empleado_name'))
        )
    
    def to_dict(self):
        """
        Convierte el objeto Maintenance a un diccionario
        
        Returns:
            dict: Diccionario con los datos del mantenimiento
        """
        return {
            'id_mantenimiento': self.id_mantenimiento,
            'id_activo': self.id_activo,
            'activo_nombre': self.activo_nombre,
            'tipo': self.tipo,
            'fecha': self.fecha,
            'descripcion': self.descripcion,
            'costo': self.costo,
            'id_empleado': self.id_empleado,
            'empleado_nombre': self.empleado_nombre
        }
    
    def get_tipo_display(self):
        """
        Obtiene el nombre para mostrar del tipo de mantenimiento
        
        Returns:
            str: Nombre del tipo para mostrar
        """
        return self.TIPOS_MANTENIMIENTO.get(self.tipo, "Desconocido")
    
    def get_costo_display(self):
        """
        Formatea el costo para mostrar
        
        Returns:
            str: Costo formateado como moneda
        """
        return f"${self.costo:,.2f}" if self.costo else "$0.00"
    
    @staticmethod
    def get_tipos_lista():
        """
        Obtiene la lista de tipos para mostrar en un combo box
        
        Returns:
            list: Lista de tuplas (valor, display)
        """
        return [(k, v) for k, v in Maintenance.TIPOS_MANTENIMIENTO.items()]
    
    @property
    def descripcion_display(self):
        """
        Devuelve la descripción o un mensaje por defecto si está vacía.
        
        Returns:
            str: Descripción del mantenimiento o mensaje por defecto
        """
        if not self.descripcion or str(self.descripcion).strip() == "":
            return "Sin descripción disponible"
        return self.descripcion