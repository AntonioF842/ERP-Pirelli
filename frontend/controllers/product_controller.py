from typing import List, Dict, Any, Optional
from models.sales_model import Producto

class ProductController:
    """Controlador para gestionar productos"""
    
    def __init__(self, api_client):
        """
        Inicializa el controlador de productos
        
        Args:
            api_client: Cliente API para comunicarse con el backend
        """
        self.api_client = api_client
    
    async def get_products(self, params: Optional[Dict[str, Any]] = None) -> List[Producto]:
        """
        Obtiene la lista de productos
        
        Args:
            params: Parámetros de filtrado opcionales
            
        Returns:
            Lista de objetos Producto
        """
        response = await self.api_client.get('/productos', params=params)
        
        if response and isinstance(response, list):
            return [Producto.from_dict(item) for item in response]
        return []
    
    async def get_product(self, product_id: int) -> Optional[Producto]:
        """
        Obtiene un producto por su ID
        
        Args:
            product_id: ID del producto
            
        Returns:
            Objeto Producto o None si no se encuentra
        """
        response = await self.api_client.get(f'/productos/{product_id}')
        
        if response:
            return Producto.from_dict(response)
        return None
    
    async def get_product_by_code(self, code: str) -> Optional[Producto]:
        """
        Obtiene un producto por su código
        
        Args:
            code: Código del producto
            
        Returns:
            Objeto Producto o None si no se encuentra
        """
        response = await self.api_client.get('/productos', params={'codigo': code})
        
        if response and isinstance(response, list) and len(response) > 0:
            return Producto.from_dict(response[0])
        return None
    
    async def create_product(self, product_data: Dict[str, Any]) -> Optional[Producto]:
        """
        Crea un nuevo producto
        
        Args:
            product_data: Datos del producto
            
        Returns:
            Producto creado o None si hay error
        """
        response = await self.api_client.post('/productos', json=product_data)
        
        if response:
            return Producto.from_dict(response)
        return None
    
    async def update_product(self, product_id: int, product_data: Dict[str, Any]) -> Optional[Producto]:
        """
        Actualiza un producto existente
        
        Args:
            product_id: ID del producto
            product_data: Datos actualizados
            
        Returns:
            Producto actualizado o None si hay error
        """
        response = await self.api_client.put(f'/productos/{product_id}', json=product_data)
        
        if response:
            return Producto.from_dict(response)
        return None
    
    async def delete_product(self, product_id: int) -> bool:
        """
        Elimina un producto
        
        Args:
            product_id: ID del producto
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        response = await self.api_client.delete(f'/productos/{product_id}')
        
        return response is not None
    
    async def get_categories(self) -> List[str]:
        """
        Obtiene la lista de categorías de productos
        
        Returns:
            Lista de categorías
        """
        return ['automovil', 'motocicleta', 'camion', 'industrial']
    
    def validate_product_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Valida los datos de un producto
        
        Args:
            data: Datos a validar
            
        Returns:
            Diccionario con errores de validación (vacío si no hay errores)
        """
        errors = {}
        
        if not data.get('codigo'):
            errors['codigo'] = 'El código es obligatorio'
        
        if not data.get('nombre'):
            errors['nombre'] = 'El nombre es obligatorio'
        
        if not data.get('precio') or float(data.get('precio', 0)) <= 0:
            errors['precio'] = 'El precio debe ser mayor que cero'
        
        if not data.get('categoria'):
            errors['categoria'] = 'La categoría es obligatoria'
        
        return errors