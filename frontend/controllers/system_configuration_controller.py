from typing import List, Dict, Any, Optional
from models.system_configuration_model import SystemConfiguration

class SystemConfigurationController:
    """Controlador para gestionar configuraciones del sistema"""
    
    def __init__(self, api_client):
        """
        Inicializa el controlador de configuraciones
        
        Args:
            api_client: Cliente API para comunicarse con el backend
        """
        self.api_client = api_client
    
    async def get_configurations(self, params: Optional[Dict[str, Any]] = None) -> List[SystemConfiguration]:
        """
        Obtiene la lista de configuraciones
        
        Args:
            params: Parámetros de filtrado opcionales
            
        Returns:
            Lista de objetos SystemConfiguration
        """
        response = await self.api_client.get('/system_configuration', params=params)
        
        if response and isinstance(response, list):
            return [SystemConfiguration.from_dict(item) for item in response]
        return []
    
    async def get_configuration(self, config_id: int) -> Optional[SystemConfiguration]:
        """
        Obtiene una configuración por su ID
        
        Args:
            config_id: ID de la configuración
            
        Returns:
            Objeto SystemConfiguration o None si no se encuentra
        """
        response = await self.api_client.get(f'/system_configuration/{config_id}')
        
        if response:
            return SystemConfiguration.from_dict(response)
        return None
    
    async def create_configuration(self, config_data: Dict[str, Any]) -> Optional[SystemConfiguration]:
        """
        Crea una nueva configuración
        
        Args:
            config_data: Datos de la configuración
            
        Returns:
            Configuración creada o None si hay error
        """
        response = await self.api_client.post('/system_configuration', json=config_data)
        
        if response:
            return SystemConfiguration.from_dict(response)
        return None
    
    async def update_configuration(self, config_id: int, config_data: Dict[str, Any]) -> Optional[SystemConfiguration]:
        """
        Actualiza una configuración existente
        
        Args:
            config_id: ID de la configuración
            config_data: Datos actualizados
            
        Returns:
            Configuración actualizada o None si hay error
        """
        response = await self.api_client.put(f'/system_configuration/{config_id}', json=config_data)
        
        if response:
            return SystemConfiguration.from_dict(response)
        return None
    
    async def delete_configuration(self, config_id: int) -> bool:
        """
        Elimina una configuración
        
        Args:
            config_id: ID de la configuración
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        response = await self.api_client.delete(f'/system_configuration/{config_id}')
        
        return response is not None
    
    def validate_configuration_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Valida los datos de una configuración
        
        Args:
            data: Datos a validar
            
        Returns:
            Diccionario con errores de validación (vacío si no hay errores)
        """
        errors = {}
        
        if not data.get('parametro'):
            errors['parametro'] = 'El parámetro es obligatorio'
        
        if data.get('valor') is None:
            errors['valor'] = 'El valor es obligatorio'
        
        return errors