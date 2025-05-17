"""
Modelo de datos para productos con validaciones y conversiones
"""

class Product:
    """Clase para representar productos en el frontend"""
    
    CATEGORIAS = {
        "automovil": "Automóvil",
        "motocicleta": "Motocicleta",
        "camion": "Camión",
        "industrial": "Industrial",
        "competicion": "Competición"
    }
    
    ESTADOS = {
        "activo": "Activo",
        "descontinuado": "Descontinuado",
        "oferta": "En oferta"
    }
    
    def __init__(self, 
                 id_producto=None, 
                 codigo=None, 
                 nombre=None,
                 descripcion=None,
                 precio=0.0,
                 categoria="automovil",
                 estado="activo"):
        """
        Inicializa un nuevo objeto de producto
        
        Args:
            id_producto: ID único del producto
            codigo: Código único del producto (max 50 chars)
            nombre: Nombre del producto (max 100 chars)
            descripcion: Descripción del producto
            precio: Precio del producto (mayor que 0)
            categoria: Categoría del producto
            estado: Estado del producto (activo/descontinuado/oferta)
        """
        self.id_producto = id_producto
        self.codigo = str(codigo) if codigo is not None else None
        self.nombre = str(nombre) if nombre is not None else None
        self.descripcion = str(descripcion) if descripcion is not None else None
        self.precio = float(precio) if precio is not None else 0.0
        self.categoria = str(categoria) if categoria is not None else "automovil"
        self.estado = str(estado).lower() if estado is not None else "activo"
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea un objeto Producto a partir de un diccionario
        
        Args:
            data: Diccionario con los datos del producto
            
        Returns:
            Product: Objeto Producto
        """
        return cls(
            id_producto=data.get('id_producto'),
            codigo=data.get('codigo'),
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion'),
            precio=data.get('precio', 0.0),
            categoria=data.get('categoria', 'automovil'),
            estado=data.get('estado', 'activo')
        )
    
    def to_dict(self):
        """
        Convierte el objeto Producto a un diccionario
        
        Returns:
            dict: Diccionario con los datos del producto
        """
        return {
            'id_producto': self.id_producto,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio': self.precio,
            'categoria': self.categoria,
            'estado': self.estado
        }
    
    def get_categoria_display(self):
        """
        Obtiene el nombre para mostrar de la categoría
        
        Returns:
            str: Nombre de la categoría para mostrar
        """
        return self.CATEGORIAS.get(self.categoria, "Desconocida")
    
    def get_estado_display(self):
        """
        Obtiene el nombre para mostrar del estado
        
        Returns:
            str: Nombre del estado para mostrar
        """
        return self.ESTADOS.get(self.estado, self.estado.capitalize())
    
    @property
    def descripcion_display(self):
        """
        Devuelve la descripción o un mensaje por defecto si está vacía.
        
        Returns:
            str: Descripción del producto o mensaje por defecto
        """
        if not self.descripcion or str(self.descripcion).strip() == "":
            return "Sin descripción disponible"
        return self.descripcion
    
    @staticmethod
    def get_categorias_lista():
        """
        Obtiene la lista de categorías para mostrar en un combo box
        
        Returns:
            list: Lista de tuplas (valor, display)
        """
        return [(k, v) for k, v in Product.CATEGORIAS.items()]
    
    @staticmethod
    def get_estados_lista():
        """
        Obtiene la lista de estados para mostrar en un combo box
        
        Returns:
            list: Lista de tuplas (valor, display)
        """
        return [(k, v) for k, v in Product.ESTADOS.items()]
    
    def validate(self):
        """
        Valida los datos del producto
        
        Returns:
            tuple: (bool, dict) - (True si es válido, diccionario de errores)
        """
        errors = {}
        
        if not self.codigo or not str(self.codigo).strip():
            errors['codigo'] = 'El código es obligatorio'
        elif len(str(self.codigo)) > 50:
            errors['codigo'] = 'El código no puede exceder 50 caracteres'
        
        if not self.nombre or not str(self.nombre).strip():
            errors['nombre'] = 'El nombre es obligatorio'
        elif len(str(self.nombre)) > 100:
            errors['nombre'] = 'El nombre no puede exceder 100 caracteres'
        
        if self.precio is None or float(self.precio) <= 0:
            errors['precio'] = 'El precio debe ser mayor que cero'
        
        if not self.categoria or self.categoria not in self.CATEGORIAS:
            errors['categoria'] = 'La categoría no es válida'
        
        if not self.estado or self.estado not in self.ESTADOS:
            errors['estado'] = 'El estado no es válido'
        
        return len(errors) == 0, errors