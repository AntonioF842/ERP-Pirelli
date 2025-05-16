from typing import List, Dict, Any, Optional
from models.incident_model import Incident

class IncidentController:
    """Controlador para gestionar incidentes"""
    
    def __init__(self, api_client):
        """
        Inicializa el controlador de incidentes
        
        Args:
            api_client: Cliente API para comunicarse con el backend
        """
        self.api_client = api_client
    
    async def get_incidents(self, params: Optional[Dict[str, Any]] = None) -> List[Incident]:
        """
        Obtiene la lista de incidentes
        
        Args:
            params: Parámetros de filtrado opcionales
            
        Returns:
            Lista de objetos Incidente
        """
        response = await self.api_client.get('/incidents', params=params)
        
        if response and isinstance(response, list):
            return [Incident.from_dict(item) for item in response]
        return []
    
    async def get_incident(self, incident_id: int) -> Optional[Incident]:
        """
        Obtiene un incidente por su ID
        
        Args:
            incident_id: ID del incidente
            
        Returns:
            Objeto Incidente o None si no se encuentra
        """
        response = await self.api_client.get(f'/incidents/{incident_id}')
        
        if response:
            return Incident.from_dict(response)
        return None
    
    async def create_incident(self, incident_data: Dict[str, Any]) -> Optional[Incident]:
        """
        Crea un nuevo incidente
        
        Args:
            incident_data: Datos del incidente
            
        Returns:
            Incidente creado o None si hay error
        """
        response = await self.api_client.post('/incidents', json=incident_data)
        
        if response:
            return Incident.from_dict(response)
        return None
    
    async def update_incident(self, incident_id: int, incident_data: Dict[str, Any]) -> Optional[Incident]:
        """
        Actualiza un incidente existente
        
        Args:
            incident_id: ID del incidente
            incident_data: Datos actualizados
            
        Returns:
            Incidente actualizado o None si hay error
        """
        response = await self.api_client.put(f'/incidents/{incident_id}', json=incident_data)
        
        if response:
            return Incident.from_dict(response)
        return None
    
    async def delete_incident(self, incident_id: int) -> bool:
        """
        Elimina un incidente
        
        Args:
            incident_id: ID del incidente
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        response = await self.api_client.delete(f'/incidents/{incident_id}')
        
        return response is not None
    
    def validate_incident_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Valida los datos de un incidente
        
        Args:
            data: Datos a validar
            
        Returns:
            Diccionario con errores de validación (vacío si no hay errores)
        """
        errors = {}
        
        if not data.get('tipo'):
            errors['tipo'] = 'El tipo es obligatorio'
        
        if not data.get('descripcion'):
            errors['descripcion'] = 'La descripción es obligatoria'
        
        if not data.get('fecha'):
            errors['fecha'] = 'La fecha es obligatoria'
        
        return errors