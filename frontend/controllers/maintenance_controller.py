from typing import List, Dict, Any, Optional
from models.maintenance_model import Maintenance

class MaintenanceController:
    """Controlador para gestionar registros de mantenimiento"""
    
    def __init__(self, api_client):
        """
        Inicializa el controlador de mantenimiento
        
        Args:
            api_client: Cliente API para comunicarse con el backend
        """
        self.api_client = api_client
    
    async def get_maintenance_records(self, params: Optional[Dict[str, Any]] = None) -> List[Maintenance]:
        """
        Obtiene la lista de registros de mantenimiento
        
        Args:
            params: Parámetros de filtrado opcionales
            
        Returns:
            Lista de objetos Maintenance
        """
        response = await self.api_client.get('/maintenance', params=params)
        
        if response and isinstance(response, list):
            return [Maintenance.from_dict(item) for item in response]
        return []
    
    async def get_maintenance_record(self, record_id: int) -> Optional[Maintenance]:
        """
        Obtiene un registro de mantenimiento por su ID
        
        Args:
            record_id: ID del registro
            
        Returns:
            Objeto Maintenance o None si no se encuentra
        """
        response = await self.api_client.get(f'/maintenance/{record_id}')
        
        if response:
            return Maintenance.from_dict(response)
        return None
    
    async def create_maintenance(self, maintenance_data: Dict[str, Any]) -> Optional[Maintenance]:
        """
        Crea un nuevo registro de mantenimiento
        
        Args:
            maintenance_data: Datos del mantenimiento
            
        Returns:
            Maintenance creado o None si hay error
        """
        response = await self.api_client.post('/maintenance', json=maintenance_data)
        
        if response:
            return Maintenance.from_dict(response)
        return None
    
    async def update_maintenance(self, record_id: int, maintenance_data: Dict[str, Any]) -> Optional[Maintenance]:
        """
        Actualiza un registro de mantenimiento existente
        
        Args:
            record_id: ID del registro
            maintenance_data: Datos actualizados
            
        Returns:
            Maintenance actualizado o None si hay error
        """
        response = await self.api_client.put(f'/maintenance/{record_id}', json=maintenance_data)
        
        if response:
            return Maintenance.from_dict(response)
        return None
    
    async def delete_maintenance(self, record_id: int) -> bool:
        """
        Elimina un registro de mantenimiento
        
        Args:
            record_id: ID del registro
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        response = await self.api_client.delete(f'/maintenance/{record_id}')
        
        return response is not None
    
    async def get_assets(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de activos disponibles
        
        Returns:
            Lista de diccionarios con activos
        """
        response = await self.api_client.get('/production_assets')
        return response if response else []
    
    async def get_employees(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de empleados disponibles
        
        Returns:
            Lista de diccionarios con empleados
        """
        response = await self.api_client.get('/employees')
        return response if response else []
    
    def validate_maintenance_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Valida los datos de un registro de mantenimiento
        
        Args:
            data: Datos a validar
            
        Returns:
            Diccionario con errores de validación (vacío si no hay errores)
        """
        errors = {}
        
        if not data.get('id_activo'):
            errors['id_activo'] = 'Se debe seleccionar un activo'
        
        if not data.get('tipo'):
            errors['tipo'] = 'El tipo de mantenimiento es obligatorio'
        
        if not data.get('fecha'):
            errors['fecha'] = 'La fecha es obligatoria'
        
        if data.get('costo') and float(data.get('costo', 0)) < 0:
            errors['costo'] = 'El costo no puede ser negativo'
        
        return errors