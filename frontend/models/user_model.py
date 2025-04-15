"""
Modelo de datos para usuarios
"""

class User:
    """Clase para representar usuarios en el frontend"""
    
    def __init__(self, 
                 id_usuario=None, 
                 nombre=None, 
                 email=None,
                 rol="empleado",
                 fecha_registro=None):
        """
        Inicializa un nuevo objeto de usuario
        
        Args:
            id_usuario: ID único del usuario
            nombre: Nombre completo del usuario
            email: Correo electrónico del usuario
            rol: Rol del usuario ('admin', 'supervisor', 'empleado')
            fecha_registro: Fecha de registro del usuario
        """
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.email = email
        self.rol = rol
        self.fecha_registro = fecha_registro
        
    @classmethod
    def from_dict(cls, data):
        """
        Crea un objeto Usuario a partir de un diccionario
        
        Args:
            data: Diccionario con los datos del usuario
            
        Returns:
            User: Objeto Usuario
        """
        return cls(
            id_usuario=data.get('id_usuario'),
            nombre=data.get('nombre'),
            email=data.get('email'),
            rol=data.get('rol', 'empleado'),
            fecha_registro=data.get('fecha_registro')
        )
    
    def to_dict(self):
        """
        Convierte el objeto Usuario a un diccionario
        
        Returns:
            dict: Diccionario con los datos del usuario
        """
        return {
            'id_usuario': self.id_usuario,
            'nombre': self.nombre,
            'email': self.email,
            'rol': self.rol,
            'fecha_registro': self.fecha_registro
        }
    
    def is_admin(self):
        """
        Verifica si el usuario es administrador
        
        Returns:
            bool: True si es administrador, False en caso contrario
        """
        return self.rol == 'admin'
    
    def is_supervisor(self):
        """
        Verifica si el usuario es supervisor
        
        Returns:
            bool: True si es supervisor, False en caso contrario
        """
        return self.rol == 'supervisor'
    
    def has_admin_privileges(self):
        """
        Verifica si el usuario tiene privilegios administrativos
        
        Returns:
            bool: True si tiene privilegios administrativos, False en caso contrario
        """
        return self.is_admin() or self.is_supervisor()


class UserSession:
    """Clase para gestionar la sesión del usuario actual"""
    
    _instance = None
    _current_user = None
    _token = None
    
    def __new__(cls):
        """Implementación de Singleton"""
        if cls._instance is None:
            cls._instance = super(UserSession, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def login(cls, user, token):
        """
        Establece el usuario actual y el token de sesión
        
        Args:
            user: Objeto Usuario o diccionario de usuario
            token: Token JWT de autenticación
        """
        if isinstance(user, dict):
            cls._current_user = User.from_dict(user)
        else:
            cls._current_user = user
        cls._token = token
    
    @classmethod
    def logout(cls):
        """Cierra la sesión actual"""
        cls._current_user = None
        cls._token = None
    
    @classmethod
    def get_current_user(cls):
        """
        Obtiene el usuario actual
        
        Returns:
            User: Objeto del usuario actual o None si no hay sesión
        """
        return cls._current_user
    
    @classmethod
    def get_token(cls):
        """
        Obtiene el token de autenticación
        
        Returns:
            str: Token JWT o None si no hay sesión
        """
        return cls._token
    
    @classmethod
    def is_authenticated(cls):
        """
        Verifica si hay un usuario autenticado
        
        Returns:
            bool: True si hay un usuario autenticado, False en caso contrario
        """
        return cls._current_user is not None and cls._token is not None