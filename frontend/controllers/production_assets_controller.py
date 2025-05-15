from typing import List, Dict, Any, Optional
from models import ActivoProduccion as ProductionAsset

class ProductionAssetController:
    """Controlador para gestionar activos de producción"""
    
    def __init__(self, api_client):
        self.api_client = api_client
    
    def get_assets(self, params: Optional[Dict[str, Any]] = None) -> List[ProductionAsset]:
        """
        Obtiene la lista de activos de producción
        
        Args:
            params: Parámetros de filtrado opcionales
            
        Returns:
            Lista de objetos ProductionAsset
        """
        response = self.api_client.get_production_assets()
        
        if response and isinstance(response, list):
            return [ProductionAsset(**item) for item in response]
        return []
    
    def get_asset(self, asset_id: int) -> Optional[ProductionAsset]:
        """
        Obtiene un activo por su ID
        
        Args:
            asset_id: ID del activo
            
        Returns:
            Objeto ProductionAsset o None si no se encuentra
        """
        response = self.api_client.get_production_asset(asset_id)
        
        if response:
            return ProductionAsset(**response)
        return None
    
    def create_asset(self, asset_data: Dict[str, Any]) -> Optional[ProductionAsset]:
        """
        Crea un nuevo activo de producción
        
        Args:
            asset_data: Datos del activo
            
        Returns:
            ProductionAsset creado o None si hay error
        """
        response = self.api_client.create_production_asset(asset_data)
        
        if response:
            return ProductionAsset(**response)
        return None
    
    def update_asset(self, asset_id: int, asset_data: Dict[str, Any]) -> Optional[ProductionAsset]:
        """
        Actualiza un activo existente
        
        Args:
            asset_id: ID del activo
            asset_data: Datos actualizados
            
        Returns:
            ProductionAsset actualizado o None si hay error
        """
        response = self.api_client.update_production_asset(asset_id, asset_data)
        
        if response:
            return ProductionAsset(**response)
        return None
    
    def delete_asset(self, asset_id: int) -> bool:
        """
        Elimina un activo
        
        Args:
            asset_id: ID del activo
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        response = self.api_client.delete_production_asset(asset_id)
        return response is not None
    
    def get_work_areas(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de áreas de trabajo para combobox
        
        Returns:
            Lista de áreas de trabajo como diccionarios
        """
        response = self.api_client.get_work_areas()
        
        if response and isinstance(response, list):
            return response
        return []
    
    def validate_asset_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Valida los datos de un activo
        
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
        
        if not data.get('estado'):
            errors['estado'] = 'El estado es obligatorio'
        
        return errors