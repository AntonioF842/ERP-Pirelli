from typing import List, Dict, Any, Optional
from models.rd_project_model import RDProject

class RDProjectController:
    """Controlador para gestionar proyectos de I+D"""
    
    def __init__(self, api_client):
        """
        Inicializa el controlador de proyectos I+D
        
        Args:
            api_client: Cliente API para comunicarse con el backend
        """
        self.api_client = api_client
    
    async def get_projects(self, params: Optional[Dict[str, Any]] = None) -> List[RDProject]:
        """
        Obtiene la lista de proyectos I+D
        
        Args:
            params: Parámetros de filtrado opcionales
            
        Returns:
            Lista de objetos RDProject
        """
        response = await self.api_client.get('/r_d_projects', params=params)
        
        if response and isinstance(response, list):
            return [RDProject.from_dict(item) for item in response]
        return []
    
    async def get_project(self, project_id: int) -> Optional[RDProject]:
        """
        Obtiene un proyecto por su ID
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Objeto RDProject o None si no se encuentra
        """
        response = await self.api_client.get(f'/r_d_projects/{project_id}')
        
        if response:
            return RDProject.from_dict(response)
        return None
    
    async def create_project(self, project_data: Dict[str, Any]) -> Optional[RDProject]:
        """
        Crea un nuevo proyecto I+D
        
        Args:
            project_data: Datos del proyecto
            
        Returns:
            Proyecto creado o None si hay error
        """
        response = await self.api_client.post('/r_d_projects', json=project_data)
        
        if response:
            return RDProject.from_dict(response)
        return None
    
    async def update_project(self, project_id: int, project_data: Dict[str, Any]) -> Optional[RDProject]:
        """
        Actualiza un proyecto existente
        
        Args:
            project_id: ID del proyecto
            project_data: Datos actualizados
            
        Returns:
            Proyecto actualizado o None si hay error
        """
        response = await self.api_client.put(f'/r_d_projects/{project_id}', json=project_data)
        
        if response:
            return RDProject.from_dict(response)
        return None
    
    async def delete_project(self, project_id: int) -> bool:
        """
        Elimina un proyecto
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        response = await self.api_client.delete(f'/r_d_projects/{project_id}')
        
        return response is not None
    
    async def get_estados(self) -> List[str]:
        """
        Obtiene la lista de estados de proyectos
        
        Returns:
            Lista de estados
        """
        return ['planificacion', 'en_desarrollo', 'completado', 'cancelado']
    
    def validate_project_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Valida los datos de un proyecto
        
        Args:
            data: Datos a validar
            
        Returns:
            Diccionario con errores de validación (vacío si no hay errores)
        """
        errors = {}
        
        if not data.get('nombre'):
            errors['nombre'] = 'El nombre es obligatorio'
        
        if not data.get('fecha_inicio'):
            errors['fecha_inicio'] = 'La fecha de inicio es obligatoria'
        
        if data.get('presupuesto') and float(data.get('presupuesto', 0)) < 0:
            errors['presupuesto'] = 'El presupuesto no puede ser negativo'
        
        if not data.get('estado'):
            errors['estado'] = 'El estado es obligatorio'
        
        return errors