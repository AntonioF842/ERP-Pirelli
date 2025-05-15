from typing import List, Dict, Any, Optional
from models.quality_control_model import QualityControl

class QualityControlController:
    """Controlador para gestionar controles de calidad"""
    
    def __init__(self, api_client):
        """
        Inicializa el controlador de calidad
        
        Args:
            api_client: Cliente API para comunicarse con el backend
        """
        self.api_client = api_client
    
    async def get_quality_controls(self, params: Optional[Dict[str, Any]] = None) -> List[QualityControl]:
        """
        Obtiene la lista de controles de calidad
        
        Args:
            params: Parámetros de filtrado opcionales
            
        Returns:
            Lista de objetos QualityControl
        """
        response = await self.api_client.get('/quality_control', params=params)
        
        if response and isinstance(response, list):
            return [QualityControl.from_dict(item) for item in response]
        return []
    
    async def get_quality_control(self, control_id: int) -> Optional[QualityControl]:
        """
        Obtiene un control de calidad por su ID
        
        Args:
            control_id: ID del control
            
        Returns:
            Objeto QualityControl o None si no se encuentra
        """
        response = await self.api_client.get(f'/quality_control/{control_id}')
        
        if response:
            return QualityControl.from_dict(response)
        return None
    
    async def create_quality_control(self, control_data: Dict[str, Any]) -> Optional[QualityControl]:
        """
        Crea un nuevo control de calidad
        
        Args:
            control_data: Datos del control
            
        Returns:
            QualityControl creado o None si hay error
        """
        response = await self.api_client.post('/quality_control', json=control_data)
        
        if response:
            return QualityControl.from_dict(response)
        return None
    
    async def update_quality_control(self, control_id: int, control_data: Dict[str, Any]) -> Optional[QualityControl]:
        """
        Actualiza un control de calidad existente
        
        Args:
            control_id: ID del control
            control_data: Datos actualizados
            
        Returns:
            QualityControl actualizado o None si hay error
        """
        response = await self.api_client.put(f'/quality_control/{control_id}', json=control_data)
        
        if response:
            return QualityControl.from_dict(response)
        return None
    
    async def delete_quality_control(self, control_id: int) -> bool:
        """
        Elimina un control de calidad
        
        Args:
            control_id: ID del control
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        response = await self.api_client.delete(f'/quality_control/{control_id}')
        
        return response is not None
    
    def validate_control_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Valida los datos de un control de calidad
        
        Args:
            data: Datos a validar
            
        Returns:
            Diccionario con errores de validación (vacío si no hay errores)
        """
        errors = {}
        
        if not data.get('id_orden_produccion'):
            errors['id_orden_produccion'] = 'La orden de producción es obligatoria'
        
        if not data.get('fecha'):
            errors['fecha'] = 'La fecha es obligatoria'
        
        if not data.get('resultado'):
            errors['resultado'] = 'El resultado es obligatorio'
        
        if not data.get('id_usuario'):
            errors['id_usuario'] = 'El usuario responsable es obligatorio'
        
        return errors