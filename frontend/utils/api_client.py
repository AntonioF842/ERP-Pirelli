import requests
import json
from PyQt6.QtCore import QObject, pyqtSignal

class ApiClient(QObject):
    """Cliente para comunicarse con el backend mediante API REST"""
    
    # Señales para notificar resultados
    login_success = pyqtSignal(dict)
    login_error = pyqtSignal(str)
    request_error = pyqtSignal(str)
    data_received = pyqtSignal(dict)
    
    def __init__(self, base_url="http://localhost:5000/api"):
        super().__init__()
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
    
    def set_auth_header(self):
        """Configura el encabezado de autorización con el token JWT si existe"""
        if self.token:
            self.session.headers.update({'Authorization': f'Bearer {self.token}'})
    
    def login(self, email, password):
        """Inicia sesión en el sistema"""
        try:
            response = self.session.post(
                f"{self.base_url}/login",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                self.set_auth_header()
                self.login_success.emit(data)
                return data
            else:
                error_msg = response.json().get('error', 'Error al iniciar sesión')
                self.login_error.emit(error_msg)
                return None
                
        except Exception as e:
            self.request_error.emit(f"Error de conexión: {str(e)}")
            return None
    
    def logout(self):
        """Cierra la sesión y limpia el token"""
        try:
            if self.token:
                response = self.session.post(f"{self.base_url}/logout")
                self.token = None
                self.session.headers.pop('Authorization', None)
                return response.status_code == 200
            return True
        except Exception as e:
            self.request_error.emit(f"Error al cerrar sesión: {str(e)}")
            return False
    
    def get_user_info(self):
        """Obtiene información del usuario actual"""
        try:
            response = self.session.get(f"{self.base_url}/me")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            self.request_error.emit(f"Error al obtener información del usuario: {str(e)}")
            return None
    
    def register_user(self, user_data):
        """Registra un nuevo usuario"""
        try:
            response = self.session.post(
                f"{self.base_url}/register",
                json=user_data
            )
            return response.json() if response.status_code in [200, 201] else None
        except Exception as e:
            self.request_error.emit(f"Error al registrar usuario: {str(e)}")
            return None
    
    def get_products(self):
        """Obtiene la lista de productos"""
        try:
            response = self.session.get(f"{self.base_url}/products")
            if response.status_code == 200:
                data = response.json()
                self.data_received.emit({"type": "products", "data": data})
                return data
            return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener productos: {str(e)}")
            return []
    
    def create_product(self, product_data):
        """Crea un nuevo producto"""
        try:
            response = self.session.post(
                f"{self.base_url}/products",
                json=product_data
            )
            return response.json() if response.status_code in [200, 201] else None
        except Exception as e:
            self.request_error.emit(f"Error al crear producto: {str(e)}")
            return None
    
    def update_product(self, product_id, product_data):
        """Actualiza un producto existente"""
        try:
            response = self.session.put(
                f"{self.base_url}/products/{product_id}",
                json=product_data
            )
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            self.request_error.emit(f"Error al actualizar producto: {str(e)}")
            return None
    
    def delete_product(self, product_id):
        """Elimina un producto"""
        try:
            response = self.session.delete(f"{self.base_url}/products/{product_id}")
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            self.request_error.emit(f"Error al eliminar producto: {str(e)}")
            return None
    
    def get_sales(self):
        """Obtiene la lista de ventas"""
        try:
            response = self.session.get(f"{self.base_url}/ventas")
            if response.status_code == 200:
                data = response.json()
                self.data_received.emit({"type": "sales", "data": data})
                return data
            return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener ventas: {str(e)}")
            return []
    
    def create_sale(self, sale_data):
        """Crea una nueva venta"""
        try:
            response = self.session.post(
                f"{self.base_url}/ventas",
                json=sale_data
            )
            return response.json() if response.status_code in [200, 201] else None
        except Exception as e:
            self.request_error.emit(f"Error al crear venta: {str(e)}")
            return None
    
    def get_dashboard_data(self):
        """
        Obtiene los datos del dashboard desde el backend y emite la señal data_received.
        El diccionario emitido tiene la forma: {"type": "dashboard", "data": ...}
        Si ocurre un error, emite la señal request_error con el mensaje correspondiente.
        """
        try:
            self.set_auth_header()
            url = f"{self.base_url}/dashboard"
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                # Emitimos la señal con el tipo 'dashboard' para que el frontend lo distinga
                self.data_received.emit({"type": "dashboard", "data": data})
                return data
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al obtener dashboard: {response.status_code} {error_msg}")
                return None
        except Exception as e:
            self.request_error.emit(f"Error de conexión al dashboard: {str(e)}")
            return None
