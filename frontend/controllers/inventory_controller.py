from typing import List, Dict, Any, Optional
from models.inventory_model import Inventario, Producto

class InventoryController:
    """Controlador para gestionar el inventario"""

    def __init__(self, api_client):
        self.api_client = api_client

    async def get_inventory(self, params: Optional[Dict[str, Any]] = None) -> List[Inventario]:
        response = await self.api_client.get('/inventario', params=params)
        if response and isinstance(response, list):
            return [Inventario.from_dict(item) for item in response]
        return []

    async def get_inventory_item(self, inventory_id: int) -> Optional[Inventario]:
        response = await self.api_client.get(f'/inventario/{inventory_id}')
        if response:
            return Inventario.from_dict(response)
        return None

    async def create_inventory_item(self, inv_data: Dict[str, Any]) -> Optional[Inventario]:
        response = await self.api_client.post('/inventario', json=inv_data)
        if response:
            return Inventario.from_dict(response)
        return None

    async def update_inventory_item(self, inventory_id: int, inv_data: Dict[str, Any]) -> Optional[Inventario]:
        response = await self.api_client.put(f'/inventario/{inventory_id}', json=inv_data)
        if response:
            return Inventario.from_dict(response)
        return None

    async def delete_inventory_item(self, inventory_id: int) -> bool:
        response = await self.api_client.delete(f'/inventario/{inventory_id}')
        return response is not None

    async def get_products(self, params: Optional[Dict[str, Any]] = None) -> List[Producto]:
        response = await self.api_client.get('/productos', params=params)
        if response and isinstance(response, list):
            return [Producto.from_dict(item) for item in response]
        return []