"""
Modelo de datos para recetas de producción
"""

class ProductionRecipe:
    """Clase para representar recetas de producción en el frontend"""
    
    def __init__(self, 
                 id_receta=None, 
                 id_producto=None,
                 producto_nombre=None,
                 id_material=None,
                 material_nombre=None,
                 cantidad=0.0):
        """
        Inicializa un nuevo objeto de receta de producción
        
        Args:
            id_receta: ID único de la receta
            id_producto: ID del producto asociado
            producto_nombre: Nombre del producto (opcional)
            id_material: ID del material asociado
            material_nombre: Nombre del material (opcional)
            cantidad: Cantidad de material requerida
        """
        self.id_receta = id_receta
        self.id_producto = id_producto
        self.producto_nombre = producto_nombre
        self.id_material = id_material
        self.material_nombre = material_nombre
        self.cantidad = float(cantidad) if cantidad is not None else 0.0
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea un objeto ProductionRecipe a partir de un diccionario
        
        Args:
            data: Diccionario con los datos de la receta
            
        Returns:
            ProductionRecipe: Objeto receta de producción
        """
        return cls(
            id_receta=data.get('id_receta'),
            id_producto=data.get('id_producto'),
            producto_nombre=data.get('producto_nombre', data.get('producto_name', '')),
            id_material=data.get('id_material'),
            material_nombre=data.get('material_nombre', data.get('material_name', '')),
            cantidad=data.get('cantidad', 0.0)
        )
    
    def to_dict(self):
        """
        Convierte el objeto ProductionRecipe a un diccionario
        
        Returns:
            dict: Diccionario con los datos de la receta
        """
        return {
            'id_receta': self.id_receta,
            'id_producto': self.id_producto,
            'producto_nombre': self.producto_nombre,
            'id_material': self.id_material,
            'material_nombre': self.material_nombre,
            'cantidad': self.cantidad
        }
    
    def __str__(self):
        return f"Receta {self.id_receta}: {self.producto_nombre} - {self.material_nombre} ({self.cantidad})"