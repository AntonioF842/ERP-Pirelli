from typing import Dict, Any, Optional

class AuthController:
    """Controlador para la autenticación y gestión de usuarios"""
    
    def __init__(self, api_client):
        """
        Inicializa el controlador de autenticación
        
        Args:
            api_client: Cliente API para comunicarse con el backend
        """
        self.api_client = api_client
        self.current_user = None
    
    async def login(self, email: str, password: str) -> bool:
        """
        Realiza el inicio de sesión
        
        Args:
            email: Correo electrónico del usuario
            password: Contraseña del usuario
            
        Returns:
            True si el login es exitoso, False en caso contrario
        """
        response = await self.api_client.post(
            '/auth/login',
            json={
                'email': email,
                'password': password
            }
        )
        
        if response and response.get('token'):
            self.api_client.set_token(response.get('token'))
            self.current_user = response.get('user')
            return True
        
        return False
    
    def logout(self) -> None:
        """
        Cierra la sesión actual
        """
        self.api_client.clear_token()
        self.current_user = None
    
    async def register(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Registra un nuevo usuario
        
        Args:
            user_data: Datos del usuario a registrar
            
        Returns:
            Datos del usuario registrado o None si hay error
        """
        response = await self.api_client.post('/auth/register', json=user_data)
        return response
    
    async def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene los datos del usuario actual
        
        Returns:
            Datos del usuario actual o None si no hay sesión
        """
        if not self.current_user:
            response = await self.api_client.get('/auth/me')
            if response:
                self.current_user = response
        
        return self.current_user
    
    async def change_password(self, old_password: str, new_password: str) -> bool:
        """
        Cambia la contraseña del usuario actual
        
        Args:
            old_password: Contraseña actual
            new_password: Nueva contraseña
            
        Returns:
            True si el cambio fue exitoso, False en caso contrario
        """
        response = await self.api_client.post(
            '/auth/change-password',
            json={
                'old_password': old_password,
                'new_password': new_password
            }
        )
        
        return response is not None
    
    def has_permission(self, permission: str) -> bool:
        """
        Verifica si el usuario actual tiene un permiso específico
        
        Args:
            permission: Permiso a verificar
            
        Returns:
            True si tiene el permiso, False en caso contrario
        """
        if not self.current_user:
            return False
        
        user_role = self.current_user.get('rol', '')
        
        # Esquema simple de permisos basado en roles
        role_permissions = {
            'admin': ['all', 'view_users', 'edit_users', 'view_reports', 'edit_config'],
            'supervisor': ['view_reports', 'edit_inventory', 'view_employees'],
            'empleado': ['view_products', 'create_sales']
        }
        
        # Administrador tiene todos los permisos
        if user_role == 'admin':
            return True
        
        # Verificar permiso específico para el rol
        return permission in role_permissions.get(user_role, [])