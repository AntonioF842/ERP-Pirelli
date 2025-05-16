"""
Modelo de datos para normativas legales
"""

class LegalRegulation:
    """Clase para representar normativas legales en el frontend"""
    
    TYPES = {
        "ambiental": "Ambiental",
        "seguridad": "Seguridad",
        "laboral": "Laboral",
        "calidad": "Calidad"
    }
    
    def __init__(self, 
                 id_normativa=None, 
                 nombre=None,
                 tipo="ambiental",
                 descripcion=None,
                 fecha_actualizacion=None,
                 aplicable_a=None):
        """
        Inicializa un nuevo objeto de normativa legal
        
        Args:
            id_normativa: ID único de la normativa
            nombre: Nombre de la normativa
            tipo: Tipo de normativa ('ambiental', 'seguridad', 'laboral', 'calidad')
            descripcion: Descripción de la normativa
            fecha_actualizacion: Fecha de última actualización
            aplicable_a: Área a la que aplica la normativa
        """
        self.id_normativa = id_normativa
        self.nombre = nombre
        self.tipo = tipo
        self.descripcion = descripcion
        self.fecha_actualizacion = fecha_actualizacion
        self.aplicable_a = aplicable_a
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea un objeto LegalRegulation a partir de un diccionario
        
        Args:
            data: Diccionario con los datos de la normativa
            
        Returns:
            LegalRegulation: Objeto LegalRegulation
        """
        return cls(
            id_normativa=data.get('id_normativa'),
            nombre=data.get('nombre'),
            tipo=data.get('tipo', 'ambiental'),
            descripcion=data.get('descripcion'),
            fecha_actualizacion=data.get('fecha_actualizacion'),
            aplicable_a=data.get('aplicable_a')
        )
    
    def to_dict(self):
        """
        Convierte el objeto LegalRegulation a un diccionario
        
        Returns:
            dict: Diccionario con los datos de la normativa
        """
        return {
            'id_normativa': self.id_normativa,
            'nombre': self.nombre,
            'tipo': self.tipo,
            'descripcion': self.descripcion,
            'fecha_actualizacion': self.fecha_actualizacion,
            'aplicable_a': self.aplicable_a
        }
    
    def get_type_display(self):
        """
        Obtiene el nombre para mostrar del tipo de normativa
        
        Returns:
            str: Nombre del tipo para mostrar
        """
        return self.TYPES.get(self.tipo, "Desconocido")
    
    @property
    def descripcion_display(self):
        """
        Devuelve la descripción o un mensaje por defecto si está vacía.
        
        Returns:
            str: Descripción de la normativa o mensaje por defecto
        """
        if not self.descripcion or str(self.descripcion).strip() == "":
            return "Sin descripción disponible"
        return self.descripcion
    
    @staticmethod
    def get_types_list():
        """
        Obtiene la lista de tipos para mostrar en un combo box
        
        Returns:
            list: Lista de tuplas (valor, display)
        """
        return [(k, v) for k, v in LegalRegulation.TYPES.items()]