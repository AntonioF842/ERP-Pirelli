"""
Modelo de datos para configuraciones del sistema
"""

class SystemConfiguration:
    """Clase para representar configuraciones del sistema en el frontend"""
    
    def __init__(self, 
                 id_config=None, 
                 parametro=None,
                 valor=None,
                 descripcion=None):
        """
        Inicializa un nuevo objeto de configuración
        
        Args:
            id_config: ID único de la configuración
            parametro: Nombre del parámetro
            valor: Valor del parámetro
            descripcion: Descripción del parámetro
        """
        self.id_config = id_config
        self.parametro = parametro
        self.valor = valor
        self.descripcion = descripcion if descripcion else "Sin descripción"
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea un objeto SystemConfiguration a partir de un diccionario
        
        Args:
            data: Diccionario con los datos de la configuración
            
        Returns:
            SystemConfiguration: Objeto configuración
        """
        return cls(
            id_config=data.get('id_config'),
            parametro=data.get('parametro'),
            valor=data.get('valor'),
            descripcion=data.get('descripcion')
        )
    
    def to_dict(self):
        """
        Convierte el objeto SystemConfiguration a un diccionario
        
        Returns:
            dict: Diccionario con los datos de la configuración
        """
        return {
            'id_config': self.id_config,
            'parametro': self.parametro,
            'valor': self.valor,
            'descripcion': self.descripcion
        }
    
    @property
    def descripcion_display(self):
        """
        Devuelve la descripción o un mensaje por defecto si está vacía.
        
        Returns:
            str: Descripción del parámetro o mensaje por defecto
        """
        if not self.descripcion or str(self.descripcion).strip() == "":
            return "Sin descripción disponible"
        return self.descripcion