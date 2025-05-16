"""
Modelo de datos para proyectos de I+D
"""

class RDProject:
    """Clase para representar proyectos de I+D en el frontend"""
    
    ESTADOS = {
        "planificacion": "Planificación",
        "en_desarrollo": "En Desarrollo",
        "completado": "Completado",
        "cancelado": "Cancelado"
    }
    
    def __init__(self, 
                 id_proyecto=None, 
                 nombre=None,
                 descripcion=None,
                 fecha_inicio=None,
                 fecha_fin_estimada=None,
                 presupuesto=0.0,
                 estado="planificacion"):
        """
        Inicializa un nuevo objeto de proyecto I+D
        
        Args:
            id_proyecto: ID único del proyecto
            nombre: Nombre del proyecto
            descripcion: Descripción del proyecto
            fecha_inicio: Fecha de inicio (string en formato YYYY-MM-DD)
            fecha_fin_estimada: Fecha estimada de fin (string en formato YYYY-MM-DD)
            presupuesto: Presupuesto asignado
            estado: Estado del proyecto ('planificacion', 'en_desarrollo', 'completado', 'cancelado')
        """
        self.id_proyecto = id_proyecto
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_inicio = fecha_inicio
        self.fecha_fin_estimada = fecha_fin_estimada
        self.presupuesto = float(presupuesto) if presupuesto is not None else 0.0
        self.estado = estado
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea un objeto RDProject a partir de un diccionario
        
        Args:
            data: Diccionario con los datos del proyecto
            
        Returns:
            RDProject: Objeto proyecto
        """
        return cls(
            id_proyecto=data.get('id_proyecto'),
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion'),
            fecha_inicio=data.get('fecha_inicio'),
            fecha_fin_estimada=data.get('fecha_fin_estimada'),
            presupuesto=data.get('presupuesto', 0.0),
            estado=data.get('estado', 'planificacion')
        )
    
    def to_dict(self):
        """
        Convierte el objeto RDProject a un diccionario
        
        Returns:
            dict: Diccionario con los datos del proyecto
        """
        return {
            'id_proyecto': self.id_proyecto,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'fecha_inicio': self.fecha_inicio,
            'fecha_fin_estimada': self.fecha_fin_estimada,
            'presupuesto': self.presupuesto,
            'estado': self.estado
        }
    
    def get_estado_display(self):
        """
        Obtiene el nombre para mostrar del estado
        
        Returns:
            str: Nombre del estado para mostrar
        """
        return self.ESTADOS.get(self.estado, "Desconocido")
    
    @property
    def descripcion_display(self):
        """
        Devuelve la descripción o un mensaje por defecto si está vacía.
        
        Returns:
            str: Descripción del proyecto o mensaje por defecto
        """
        if not self.descripcion or str(self.descripcion).strip() == "":
            return "Sin descripción disponible"
        return self.descripcion
    
    @staticmethod
    def get_estados_lista():
        """
        Obtiene la lista de estados para mostrar en un combo box
        
        Returns:
            list: Lista de tuplas (valor, display)
        """
        return [(k, v) for k, v in RDProject.ESTADOS.items()]