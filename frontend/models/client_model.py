"""
Modelo de datos para clientes
"""

class Client:
    """Clase para representar clientes en el frontend"""
    
    TIPOS_CLIENTE = {
        "distribuidor": "Distribuidor",
        "mayorista": "Mayorista",
        "minorista": "Minorista",
        "OEM": "Fabricante de Equipo Original"
    }
    
    def __init__(self, 
                 id_cliente=None, 
                 nombre=None,
                 contacto=None,
                 telefono=None,
                 email=None,
                 direccion=None,
                 tipo="distribuidor"):
        """
        Inicializa un nuevo objeto de cliente
        
        Args:
            id_cliente: ID único del cliente
            nombre: Nombre del cliente
            contacto: Persona de contacto
            telefono: Teléfono de contacto
            email: Correo electrónico
            direccion: Dirección física
            tipo: Tipo de cliente ('distribuidor', 'mayorista', 'minorista', 'OEM')
        """
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.contacto = contacto
        self.telefono = telefono
        self.email = email
        self.direccion = direccion
        self.tipo = tipo
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea un objeto Client a partir de un diccionario
        
        Args:
            data: Diccionario con los datos del cliente
            
        Returns:
            Client: Objeto Client
        """
        return cls(
            id_cliente=data.get('id_cliente'),
            nombre=data.get('nombre'),
            contacto=data.get('contacto'),
            telefono=data.get('telefono'),
            email=data.get('email'),
            direccion=data.get('direccion'),
            tipo=data.get('tipo', 'distribuidor')
        )
    
    def to_dict(self):
        """
        Convierte el objeto Client a un diccionario
        
        Returns:
            dict: Diccionario con los datos del cliente
        """
        return {
            'id_cliente': self.id_cliente,
            'nombre': self.nombre,
            'contacto': self.contacto,
            'telefono': self.telefono,
            'email': self.email,
            'direccion': self.direccion,
            'tipo': self.tipo
        }
    
    def get_tipo_display(self):
        """
        Obtiene el nombre para mostrar del tipo de cliente
        
        Returns:
            str: Nombre del tipo para mostrar
        """
        return self.TIPOS_CLIENTE.get(self.tipo, "Desconocido")
    
    @property
    def contacto_display(self):
        """
        Devuelve el contacto o un mensaje por defecto si está vacío.
        
        Returns:
            str: Contacto del cliente o mensaje por defecto
        """
        if not self.contacto or str(self.contacto).strip() == "":
            return "Sin contacto especificado"
        return self.contacto
    
    @staticmethod
    def get_tipos_lista():
        """
        Obtiene la lista de tipos de cliente para mostrar en un combo box
        
        Returns:
            list: Lista de tuplas (valor, display)
        """
        return [(k, v) for k, v in Client.TIPOS_CLIENTE.items()]