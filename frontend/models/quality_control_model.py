"""
Modelo de datos para control de calidad
"""

class QualityControl:
    """Clase para representar controles de calidad en el frontend"""
    
    RESULTS = {
        "aprobado": "Aprobado",
        "rechazado": "Rechazado",
        "reparacion": "Requiere Reparación"
    }
    
    def __init__(self, 
                 id_control=None,
                 id_orden_produccion=None,
                 fecha=None,
                 resultado="aprobado",
                 observaciones=None,
                 id_usuario=None):
        """
        Inicializa un nuevo objeto de control de calidad
        
        Args:
            id_control: ID único del control
            id_orden_produccion: ID de la orden de producción asociada
            fecha: Fecha del control (string en formato YYYY-MM-DD)
            resultado: Resultado del control ('aprobado', 'rechazado', 'reparacion')
            observaciones: Observaciones del control
            id_usuario: ID del usuario que realizó el control
        """
        self.id_control = id_control
        self.id_orden_produccion = id_orden_produccion
        self.fecha = fecha
        self.resultado = resultado
        self.observaciones = observaciones
        self.id_usuario = id_usuario
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea un objeto QualityControl a partir de un diccionario
        
        Args:
            data: Diccionario con los datos del control
            
        Returns:
            QualityControl: Objeto QualityControl
        """
        return cls(
            id_control=data.get('id_control'),
            id_orden_produccion=data.get('id_orden_produccion'),
            fecha=data.get('fecha'),
            resultado=data.get('resultado', 'aprobado'),
            observaciones=data.get('observaciones'),
            id_usuario=data.get('id_usuario')
        )
    
    def to_dict(self):
        """
        Convierte el objeto QualityControl a un diccionario
        
        Returns:
            dict: Diccionario con los datos del control
        """
        return {
            'id_control': self.id_control,
            'id_orden_produccion': self.id_orden_produccion,
            'fecha': self.fecha,
            'resultado': self.resultado,
            'observaciones': self.observaciones,
            'id_usuario': self.id_usuario
        }
    
    def get_resultado_display(self):
        """
        Obtiene el nombre para mostrar del resultado
        
        Returns:
            str: Nombre del resultado para mostrar
        """
        return self.RESULTS.get(self.resultado, "Desconocido")
    
    @property
    def observaciones_display(self):
        """
        Devuelve las observaciones o un mensaje por defecto si está vacío.
        
        Returns:
            str: Observaciones o mensaje por defecto
        """
        if not self.observaciones or str(self.observaciones).strip() == "":
            return "Sin observaciones"
        return self.observaciones
    
    @staticmethod
    def get_resultados_lista():
        """
        Obtiene la lista de resultados para mostrar en un combo box
        
        Returns:
            list: Lista de tuplas (valor, display)
        """
        return [(k, v) for k, v in QualityControl.RESULTS.items()]