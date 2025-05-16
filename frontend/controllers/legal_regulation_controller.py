from typing import List, Dict, Any, Optional
from models.legal_regulation_model import LegalRegulation

class LegalRegulationController:
    """Controlador para gestionar normativas legales"""
    
    def __init__(self, api_client):
        """
        Inicializa el controlador de normativas legales
        
        Args:
            api_client: Cliente API para comunicarse con el backend
        """
        self.api_client = api_client
    
    async def get_regulations(self, params: Optional[Dict[str, Any]] = None) -> List[LegalRegulation]:
        """
        Obtiene la lista de normativas legales
        
        Args:
            params: Parámetros de filtrado opcionales
            
        Returns:
            Lista de objetos LegalRegulation
        """
        response = await self.api_client.get('/legal_regulations', params=params)
        
        if response and isinstance(response, list):
            return [LegalRegulation.from_dict(item) for item in response]
        return []
    
    async def get_regulation(self, regulation_id: int) -> Optional[LegalRegulation]:
        """
        Obtiene una normativa legal por su ID
        
        Args:
            regulation_id: ID de la normativa
            
        Returns:
            Objeto LegalRegulation o None si no se encuentra
        """
        response = await self.api_client.get(f'/legal_regulations/{regulation_id}')
        
        if response:
            return LegalRegulation.from_dict(response)
        return None
    
    async def create_regulation(self, regulation_data: Dict[str, Any]) -> Optional[LegalRegulation]:
        """
        Crea una nueva normativa legal
        
        Args:
            regulation_data: Datos de la normativa
            
        Returns:
            LegalRegulation creada o None si hay error
        """
        response = await self.api_client.post('/legal_regulations', json=regulation_data)
        
        if response:
            return LegalRegulation.from_dict(response)
        return None
    
    async def update_regulation(self, regulation_id: int, regulation_data: Dict[str, Any]) -> Optional[LegalRegulation]:
        """
        Actualiza una normativa legal existente
        
        Args:
            regulation_id: ID de la normativa
            regulation_data: Datos actualizados
            
        Returns:
            LegalRegulation actualizada o None si hay error
        """
        response = await self.api_client.put(f'/legal_regulations/{regulation_id}', json=regulation_data)
        
        if response:
            return LegalRegulation.from_dict(response)
        return None
    
    async def delete_regulation(self, regulation_id: int) -> bool:
        """
        Elimina una normativa legal
        
        Args:
            regulation_id: ID de la normativa
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        response = await self.api_client.delete(f'/legal_regulations/{regulation_id}')
        
        return response is not None
    
    async def get_types(self) -> List[str]:
        """
        Obtiene la lista de tipos de normativas
        
        Returns:
            Lista de tipos
        """
        return ['ambiental', 'seguridad', 'laboral', 'calidad']
    
    def validate_regulation_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Valida los datos de una normativa legal
        
        Args:
            data: Datos a validar
            
        Returns:
            Diccionario con errores de validación (vacío si no hay errores)
        """
        errors = {}
        
        if not data.get('nombre'):
            errors['nombre'] = 'El nombre es obligatorio'
        
        if not data.get('tipo'):
            errors['tipo'] = 'El tipo es obligatorio'
        
        return errors