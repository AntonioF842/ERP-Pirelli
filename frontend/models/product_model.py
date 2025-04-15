"""
Modelo de datos para productos
"""

class Product:
    """Clase para representar productos en el frontend"""
    
    CATEGORIAS = {
        "automovil": "Automóvil",
        "motocicleta": "Motocicleta",
        "camion": "Camión",
        "industrial": "Industrial"
    }
    
    def __init__(self, 
                 id_producto=None, 
                 codigo=None, 
                 nombre=None,
                 descripcion=None,
                 precio=0.0,
                 categoria="automovil"):
        """
        Inicializa un nuevo objeto de producto
        
        Args:
            id_producto: ID único del producto
            codigo: Código único del producto
            nombre: Nombre del producto
            descripcion: Descripción del producto
            precio: Precio del producto
            categoria: Categoría del producto ('automovil', 'motocicleta', 'camion', 'industrial')
        """
        self.id_producto = id_producto
        self.codigo = codigo
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = float(precio) if precio is not None else 0.0
        self.categoria = categoria
    
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
            categoria=data.get('categoria', 'automovil')
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
            'categoria': self.categoria
        }
    
    def get_categoria_display(self):
        """
        Obtiene el nombre para mostrar de la categoría
        
        Returns:
            str: Nombre de la categoría para mostrar
        """
        return self.CATEGORIAS.get(self.categoria, "Desconocida")
    
    @staticmethod
    def get_categorias_lista():
        """
        Obtiene la lista de categorías para mostrar en un combo box
        
        Returns:
            list: Lista de tuplas (valor, display)
        """
        return [(k, v) for k, v in Product.CATEGORIAS.items()]