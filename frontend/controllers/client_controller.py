from typing import List, Dict, Any, Optional
from models.client_model import Client

class ClientController:
    """Controlador para gestionar clientes"""
    
    def __init__(self, api_client):
        """
        Inicializa el controlador de clientes
        
        Args:
            api_client: Cliente API para comunicarse con el backend
        """
        self.api_client = api_client
    
    async def get_clients(self, params: Optional[Dict[str, Any]] = None) -> List[Client]:
        """
        Obtiene la lista de clientes
        
        Args:
            params: Parámetros de filtrado opcionales
            
        Returns:
            Lista de objetos Client
        """
        response = await self.api_client.get('/clientes', params=params)
        
        if response and isinstance(response, list):
            return [Client.from_dict(item) for item in response]
        return []
    
    async def get_client(self, client_id: int) -> Optional[Client]:
        """
        Obtiene un cliente por su ID
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Objeto Client o None si no se encuentra
        """
        response = await self.api_client.get(f'/clientes/{client_id}')
        
        if response:
            return Client.from_dict(response)
        return None
    
    async def create_client(self, client_data: Dict[str, Any]) -> Optional[Client]:
        """
        Crea un nuevo cliente
        
        Args:
            client_data: Datos del cliente
            
        Returns:
            Cliente creado o None si hay error
        """
        response = await self.api_client.post('/clientes', json=client_data)
        
        if response:
            return Client.from_dict(response)
        return None
    
    async def update_client(self, client_id: int, client_data: Dict[str, Any]) -> Optional[Client]:
        """
        Actualiza un cliente existente
        
        Args:
            client_id: ID del cliente
            client_data: Datos actualizados
            
        Returns:
            Cliente actualizado o None si hay error
        """
        response = await self.api_client.put(f'/clientes/{client_id}', json=client_data)
        
        if response:
            return Client.from_dict(response)
        return None
    
    async def delete_client(self, client_id: int) -> bool:
        """
        Elimina un cliente
        
        Args:
            client_id: ID del cliente
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        response = await self.api_client.delete(f'/clientes/{client_id}')
        
        return response is not None
    
    async def get_client_types(self) -> List[str]:
        """
        Obtiene la lista de tipos de cliente
        
        Returns:
            Lista de tipos
        """
        return ['distribuidor', 'mayorista', 'minorista', 'OEM']
    
    def validate_client_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Valida los datos de un cliente
        
        Args:
            data: Datos a validar
            
        Returns:
            Diccionario con errores de validación (vacío si no hay errores)
        """
        errors = {}
        
        if not data.get('nombre'):
            errors['nombre'] = 'El nombre es obligatorio'
        
        if not data.get('email'):
            errors['email'] = 'El email es obligatorio'
        elif '@' not in data['email']:
            errors['email'] = 'El email no es válido'
        
        if not data.get('tipo'):
            errors['tipo'] = 'El tipo de cliente es obligatorio'
        
        return errors