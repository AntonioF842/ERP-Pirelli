"""
Configuración global de la aplicación
"""

class AppConfig:
    """Configuración global de la aplicación"""
    
    # Información de la aplicación
    APP_NAME = "ERP Pirelli"
    APP_VERSION = "1.0"
    COMPANY_NAME = "Pirelli"
    
    # Configuración de la API
    API_BASE_URL = "http://localhost:5000/api"
    
    # Rutas de recursos
    ICONS_PATH = "resources/icons/"
    IMAGES_PATH = "resources/images/"
    STYLES_PATH = "resources/styles/"
    
    # Configuración de la interfaz
    WINDOW_WIDTH = 1024
    WINDOW_HEIGHT = 768
    
    # Configuración de sesión
    SESSION_TIMEOUT = 30 * 60  # 30 minutos en segundos
    
    # Configuración de caché
    CACHE_ENABLED = True
    CACHE_TIMEOUT = 5 * 60  # 5 minutos en segundos
    
    # Roles de usuario
    ROLES = {
        "admin": {
            "name": "Administrador",
            "permissions": ["all"]
        },
        "supervisor": {
            "name": "Supervisor",
            "permissions": ["view_all", "edit_basic", "approve"]
        },
        "empleado": {
            "name": "Empleado",
            "permissions": ["view_basic", "edit_own"]
        }
    }

    @staticmethod
    def get_icon_path(icon_name):
        """
        Obtiene la ruta completa a un icono
        
        Args:
            icon_name: Nombre del archivo de icono
            
        Returns:
            str: Ruta completa al archivo de icono
        """
        return f"{AppConfig.ICONS_PATH}{icon_name}"

    @staticmethod
    def get_image_path(image_name):
        """
        Obtiene la ruta completa a una imagen
        
        Args:
            image_name: Nombre del archivo de imagen
            
        Returns:
            str: Ruta completa al archivo de imagen
        """
        return f"{AppConfig.IMAGES_PATH}{image_name}"

    @staticmethod
    def get_style_path(style_name):
        """
        Obtiene la ruta completa a un archivo de estilo
        
        Args:
            style_name: Nombre del archivo de estilo
            
        Returns:
            str: Ruta completa al archivo de estilo
        """
        return f"{AppConfig.STYLES_PATH}{style_name}"

    @staticmethod
    def has_permission(user_role, permission):
        """
        Verifica si un rol tiene un permiso específico
        
        Args:
            user_role: Rol del usuario
            permission: Permiso a verificar
            
        Returns:
            bool: True si tiene el permiso, False en caso contrario
        """
        if user_role not in AppConfig.ROLES:
            return False
            
        role_permissions = AppConfig.ROLES[user_role]["permissions"]
        
        if "all" in role_permissions:
            return True
            
        return permission in role_permissions