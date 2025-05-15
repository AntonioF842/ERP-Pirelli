"""
Modelo de datos para activos de producción
"""

class ProductionAsset:
    """Clase para representar activos de producción en el frontend"""
    
    TIPOS = {
        "maquinaria": "Maquinaria",
        "herramienta": "Herramienta",
        "equipo": "Equipo"
    }
    
    ESTADOS = {
        "operativo": "Operativo",
        "mantenimiento": "En Mantenimiento",
        "baja": "Dado de Baja"
    }
    
    def __init__(self, 
                 id_activo=None, 
                 nombre=None,
                 tipo="maquinaria",
                 id_area=None,
                 area_name=None,
                 fecha_adquisicion=None,
                 estado="operativo"):
        """
        Inicializa un nuevo objeto de activo de producción
        
        Args:
            id_activo: ID único del activo
            nombre: Nombre del activo
            tipo: Tipo de activo ('maquinaria', 'herramienta', 'equipo')
            id_area: ID del área de trabajo asociada
            area_name: Nombre del área de trabajo
            fecha_adquisicion: Fecha de adquisición (string YYYY-MM-DD)
            estado: Estado del activo ('operativo', 'mantenimiento', 'baja')
        """
        self.id_activo = id_activo
        self.nombre = nombre
        self.tipo = tipo
        self.id_area = id_area
        self.area_name = area_name
        self.fecha_adquisicion = fecha_adquisicion
        self.estado = estado
    
    def to_dict(self):
        """
        Convierte el objeto ProductionAsset a un diccionario
        
        Returns:
            dict: Diccionario con los datos del activo
        """
        return {
            'id_activo': self.id_activo,
            'nombre': self.nombre,
            'tipo': self.tipo,
            'id_area': self.id_area,
            'area_name': self.area_name,
            'fecha_adquisicion': self.fecha_adquisicion,
            'estado': self.estado
        }
    
    def get_tipo_display(self):
        """
        Obtiene el nombre para mostrar del tipo
        
        Returns:
            str: Nombre del tipo para mostrar
        """
        return self.TIPOS.get(self.tipo, "Desconocido")
    
    def get_estado_display(self):
        """
        Obtiene el nombre para mostrar del estado
        
        Returns:
            str: Nombre del estado para mostrar
        """
        return self.ESTADOS.get(self.estado, "Desconocido")
    
    @staticmethod
    def get_tipos_lista():
        """
        Obtiene la lista de tipos para mostrar en un combo box
        
        Returns:
            list: Lista de tuplas (valor, display)
        """
        return [(k, v) for k, v in ProductionAsset.TIPOS.items()]
    
    @staticmethod
    def get_estados_lista():
        """
        Obtiene la lista de estados para mostrar en un combo box
        
        Returns:
            list: Lista de tuplas (valor, display)
        """
        return [(k, v) for k, v in ProductionAsset.ESTADOS.items()]