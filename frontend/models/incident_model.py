"""
Modelo de datos para incidentes
"""

class Incident:
    """Clase para representar incidentes en el frontend"""
    
    TIPOS = {
        "seguridad": "Seguridad",
        "calidad": "Calidad",
        "logistica": "Logística"
    }
    
    ESTADOS = {
        "reportado": "Reportado",
        "investigacion": "En investigación",
        "resuelto": "Resuelto"
    }
    
    def __init__(self, 
                 id_incidente=None, 
                 tipo=None,
                 descripcion=None,
                 fecha=None,
                 id_area=None,
                 id_empleado_reporta=None,
                 estado="reportado"):
        """
        Inicializa un nuevo objeto de incidente
        
        Args:
            id_incidente: ID único del incidente
            tipo: Tipo de incidente ('seguridad', 'calidad', 'logistica')
            descripcion: Descripción del incidente
            fecha: Fecha del incidente
            id_area: ID del área relacionada
            id_empleado_reporta: ID del empleado que reportó
            estado: Estado del incidente ('reportado', 'investigacion', 'resuelto')
        """
        self.id_incidente = id_incidente
        self.tipo = tipo
        self.descripcion = descripcion
        self.fecha = fecha
        self.id_area = id_area
        self.id_empleado_reporta = id_empleado_reporta
        self.estado = estado
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea un objeto Incidente a partir de un diccionario
        
        Args:
            data: Diccionario con los datos del incidente
            
        Returns:
            Incident: Objeto Incidente
        """
        return cls(
            id_incidente=data.get('id_incidente'),
            tipo=data.get('tipo'),
            descripcion=data.get('descripcion'),
            fecha=data.get('fecha'),
            id_area=data.get('id_area'),
            id_empleado_reporta=data.get('id_empleado_reporta'),
            estado=data.get('estado', 'reportado')
        )
    
    def to_dict(self):
        """
        Convierte el objeto Incidente a un diccionario
        
        Returns:
            dict: Diccionario con los datos del incidente
        """
        return {
            'id_incidente': self.id_incidente,
            'tipo': self.tipo,
            'descripcion': self.descripcion,
            'fecha': self.fecha,
            'id_area': self.id_area,
            'id_empleado_reporta': self.id_empleado_reporta,
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
        return [(k, v) for k, v in Incident.TIPOS.items()]
    
    @staticmethod
    def get_estados_lista():
        """
        Obtiene la lista de estados para mostrar en un combo box
        
        Returns:
            list: Lista de tuplas (valor, display)
        """
        return [(k, v) for k, v in Incident.ESTADOS.items()]