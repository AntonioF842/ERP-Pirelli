from typing import List, Dict, Any, Optional
from models.sales_model import ProductionRecipe

class ProductionRecipeController:
    """Controlador para gestionar recetas de producción"""
    
    def __init__(self, api_client):
        """
        Inicializa el controlador de recetas de producción
        
        Args:
            api_client: Cliente API para comunicarse con el backend
        """
        self.api_client = api_client
    
    async def get_recipes(self, params: Optional[Dict[str, Any]] = None) -> List[ProductionRecipe]:
        """
        Obtiene la lista de recetas de producción
        
        Args:
            params: Parámetros de filtrado opcionales
            
        Returns:
            Lista de objetos ProductionRecipe
        """
        response = await self.api_client.get('/production_recipes', params=params)
        
        if response and isinstance(response, list):
            return [ProductionRecipe.from_dict(item) for item in response]
        return []
    
    async def get_recipe(self, recipe_id: int) -> Optional[ProductionRecipe]:
        """
        Obtiene una receta por su ID
        
        Args:
            recipe_id: ID de la receta
            
        Returns:
            Objeto ProductionRecipe o None si no se encuentra
        """
        response = await self.api_client.get(f'/production_recipes/{recipe_id}')
        
        if response:
            return ProductionRecipe.from_dict(response)
        return None
    
    async def get_recipes_by_product(self, product_id: int) -> List[ProductionRecipe]:
        """
        Obtiene recetas por ID de producto
        
        Args:
            product_id: ID del producto
            
        Returns:
            Lista de recetas para ese producto
        """
        response = await self.api_client.get('/production_recipes', params={'id_producto': product_id})
        
        if response and isinstance(response, list):
            return [ProductionRecipe.from_dict(item) for item in response]
        return []
    
    async def create_recipe(self, recipe_data: Dict[str, Any]) -> Optional[ProductionRecipe]:
        """
        Crea una nueva receta de producción
        
        Args:
            recipe_data: Datos de la receta
            
        Returns:
            Receta creada o None si hay error
        """
        response = await self.api_client.post('/production_recipes', json=recipe_data)
        
        if response:
            return ProductionRecipe.from_dict(response)
        return None
    
    async def update_recipe(self, recipe_id: int, recipe_data: Dict[str, Any]) -> Optional[ProductionRecipe]:
        """
        Actualiza una receta existente
        
        Args:
            recipe_id: ID de la receta
            recipe_data: Datos actualizados
            
        Returns:
            Receta actualizada o None si hay error
        """
        response = await self.api_client.put(f'/production_recipes/{recipe_id}', json=recipe_data)
        
        if response:
            return ProductionRecipe.from_dict(response)
        return None
    
    async def delete_recipe(self, recipe_id: int) -> bool:
        """
        Elimina una receta
        
        Args:
            recipe_id: ID de la receta
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        response = await self.api_client.delete(f'/production_recipes/{recipe_id}')
        
        return response is not None
    
    def validate_recipe_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Valida los datos de una receta
        
        Args:
            data: Datos a validar
            
        Returns:
            Diccionario con errores de validación (vacío si no hay errores)
        """
        errors = {}
        
        if not data.get('id_producto'):
            errors['id_producto'] = 'El producto es obligatorio'
        
        if not data.get('id_material'):
            errors['id_material'] = 'El material es obligatorio'
        
        if not data.get('cantidad') or float(data.get('cantidad', 0)) <= 0:
            errors['cantidad'] = 'La cantidad debe ser mayor que cero'
        
        return errors