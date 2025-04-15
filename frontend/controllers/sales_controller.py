from typing import List, Dict, Any, Optional, Callable
from models.sales_model import Venta, DetalleVenta, Producto, Cliente

class SalesController:
    """Controlador para gestionar las ventas"""
    
    def __init__(self, api_client):
        """
        Inicializa el controlador de ventas
        
        Args:
            api_client: Cliente API para comunicarse con el backend
        """
        self.api_client = api_client
    
    async def get_sales(self, params: Optional[Dict[str, Any]] = None) -> List[Venta]:
        """
        Obtiene la lista de ventas
        
        Args:
            params: Parámetros de filtrado opcionales
            
        Returns:
            Lista de objetos Venta
        """
        response = await self.api_client.get('/ventas', params=params)
        
        if response and isinstance(response, list):
            return [Venta.from_dict(item) for item in response]
        return []
    
    async def get_sale(self, sale_id: int) -> Optional[Venta]:
        """
        Obtiene una venta por su ID
        
        Args:
            sale_id: ID de la venta
            
        Returns:
            Objeto Venta o None si no se encuentra
        """
        response = await self.api_client.get(f'/ventas/{sale_id}')
        
        if response:
            return Venta.from_dict(response)
        return None
    
    async def create_sale(self, sale_data: Dict[str, Any]) -> Optional[Venta]:
        """
        Crea una nueva venta
        
        Args:
            sale_data: Datos de la venta
            
        Returns:
            Venta creada o None si hay error
        """
        response = await self.api_client.post('/ventas', json=sale_data)
        
        if response:
            return Venta.from_dict(response)
        return None
    
    async def update_sale(self, sale_id: int, sale_data: Dict[str, Any]) -> Optional[Venta]:
        """
        Actualiza una venta existente
        
        Args:
            sale_id: ID de la venta
            sale_data: Datos actualizados
            
        Returns:
            Venta actualizada o None si hay error
        """
        response = await self.api_client.put(f'/ventas/{sale_id}', json=sale_data)
        
        if response:
            return Venta.from_dict(response)
        return None
    
    async def delete_sale(self, sale_id: int) -> bool:
        """
        Elimina una venta
        
        Args:
            sale_id: ID de la venta
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        response = await self.api_client.delete(f'/ventas/{sale_id}')
        
        return response is not None
    
    async def get_clients(self, params: Optional[Dict[str, Any]] = None) -> List[Cliente]:
        """
        Obtiene la lista de clientes
        
        Args:
            params: Parámetros de filtrado opcionales
            
        Returns:
            Lista de objetos Cliente
        """
        response = await self.api_client.get('/clientes', params=params)
        
        if response and isinstance(response, list):
            return [Cliente.from_dict(item) for item in response]
        return []
    
    async def get_products(self, params: Optional[Dict[str, Any]] = None) -> List[Producto]:
        """
        Obtiene la lista de productos disponibles para venta
        
        Args:
            params: Parámetros de filtrado opcionales
            
        Returns:
            Lista de objetos Producto
        """
        response = await self.api_client.get('/productos', params=params)
        
        if response and isinstance(response, list):
            return [Producto.from_dict(item) for item in response]
        return []
    
    def calculate_subtotal(self, quantity: int, unit_price: float) -> float:
        """
        Calcula el subtotal de una línea de detalle
        
        Args:
            quantity: Cantidad de productos
            unit_price: Precio unitario
            
        Returns:
            Subtotal calculado
        """
        return round(quantity * unit_price, 2)
    
    def calculate_total(self, details: List[Dict[str, Any]]) -> float:
        """
        Calcula el total de una venta a partir de sus detalles
        
        Args:
            details: Lista de detalles de venta
            
        Returns:
            Total calculado
        """
        return round(sum(item.get('subtotal', 0) for item in details), 2)