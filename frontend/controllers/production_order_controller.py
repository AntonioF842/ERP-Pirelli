from typing import List, Dict, Any, Optional
from models import ProductionOrder
from datetime import datetime

class ProductionOrderController:
    def __init__(self, api_client):
        self.api_client = api_client
    
    async def get_production_orders(self, params=None):
        response = await self.api_client.get_production_orders(params)
        if response:
            return [ProductionOrder.from_dict(item) for item in response]
        return []
    
    async def get_production_order(self, order_id):
        response = await self.api_client.get_production_order(order_id)
        if response:
            return ProductionOrder.from_dict(response)
        return None
    
    async def create_production_order(self, order_data):
        errors = self.validate_production_order_data(order_data)
        if errors:
            raise ValueError("Datos de orden inválidos: " + ", ".join(errors.values()))
        
        formatted_data = self._format_dates(order_data)
        response = await self.api_client.create_production_order(formatted_data)
        
        if response:
            return ProductionOrder.from_dict(response)
        return None
    
    async def update_production_order(self, order_id, order_data):
        errors = self.validate_production_order_data(order_data)
        if errors:
            raise ValueError("Datos de orden inválidos: " + ", ".join(errors.values()))
        
        formatted_data = self._format_dates(order_data)
        response = await self.api_client.update_production_order(order_id, formatted_data)
        
        if response:
            return ProductionOrder.from_dict(response)
        return None
    
    async def delete_production_order(self, order_id):
        return await self.api_client.delete_production_order(order_id)
    
    def validate_production_order_data(self, data):
        errors = {}
        
        if not data.get('id_producto'):
            errors['id_producto'] = 'El producto es obligatorio'
        
        if not data.get('cantidad') or int(data.get('cantidad', 0)) <= 0:
            errors['cantidad'] = 'La cantidad debe ser mayor que cero'
        
        if not data.get('fecha_inicio'):
            errors['fecha_inicio'] = 'La fecha de inicio es obligatoria'
        
        if not data.get('id_usuario'):
            errors['id_usuario'] = 'El usuario responsable es obligatorio'
        
        return errors
    
    def _format_dates(self, data):
        formatted_data = data.copy()
        
        # Handle fecha_inicio
        if isinstance(data.get('fecha_inicio'), str):
            try:
                datetime.strptime(data['fecha_inicio'], '%Y-%m-%d')
            except ValueError:
                formatted_data['fecha_inicio'] = None
                
        # Handle fecha_fin
        if isinstance(data.get('fecha_fin'), str):
            try:
                datetime.strptime(data['fecha_fin'], '%Y-%m-%d')
            except ValueError:
                formatted_data['fecha_fin'] = None
                
        return formatted_data