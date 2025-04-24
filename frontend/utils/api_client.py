import requests
from PyQt6.QtCore import QObject, pyqtSignal

class ApiClient(QObject):
    """
    Cliente para comunicarse con el backend mediante API REST 
    Permite CRUD sobre ventas, productos y clientes.
    """
    # Señales para notificar resultados
    login_success = pyqtSignal(dict)
    login_error = pyqtSignal(str)
    request_error = pyqtSignal(str)
    request_success = pyqtSignal(str, object)  # endpoint, data
    data_received = pyqtSignal(dict)
    
    def __init__(self, base_url="http://localhost:5000/api"):
        super().__init__()
        self.base_url = base_url.rstrip("/")
        self.token = None
        self.session = requests.Session()
    
    def set_auth_header(self):
        """Configura el encabezado de autorización con el token JWT si existe"""
        if self.token:
            self.session.headers.update({'Authorization': f'Bearer {self.token}'})
    
    # --- AUTENTICACIÓN Y USUARIOS ---
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
    
    # --- CLIENTES (CRUD) ---
    def get_clients(self):
        """Obtiene la lista de clientes"""
        try:
            response = self.session.get(f"{self.base_url}/clientes")
            if response.status_code == 200:
                data = response.json()
                self.data_received.emit({"type": "clients", "data": data})
                return data
            return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener clientes: {str(e)}")
            return []
    
    def get_client(self, client_id):
        """Obtiene un cliente por su ID"""
        try:
            response = self.session.get(f"{self.base_url}/clientes/{client_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            self.request_error.emit(f"Error al obtener cliente: {str(e)}")
            return None
    
    def create_client(self, client_data):
        """Crea un nuevo cliente"""
        try:
            response = self.session.post(
                f"{self.base_url}/clientes",
                json=client_data
            )
            result = response.json() if response.status_code in [200, 201] else None
            if result:
                self.request_success.emit("create_client", result)
            return result
        except Exception as e:
            self.request_error.emit(f"Error al crear cliente: {str(e)}")
            return None
    
    def update_client(self, client_id, client_data):
        """Actualiza un cliente existente"""
        try:
            response = self.session.put(
                f"{self.base_url}/clientes/{client_id}",
                json=client_data
            )
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("update_client", result)
            return result
        except Exception as e:
            self.request_error.emit(f"Error al actualizar cliente: {str(e)}")
            return None
    
    def delete_client(self, client_id):
        """Elimina un cliente"""
        try:
            response = self.session.delete(f"{self.base_url}/clientes/{client_id}")
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("delete_client", result)
            return result
        except Exception as e:
            self.request_error.emit(f"Error al eliminar cliente: {str(e)}")
            return None
    
    # --- PRODUCTOS (CRUD) ---
    def get_products(self):
        """Obtiene la lista de productos del endpoint /products"""
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
    
    def get_product(self, product_id):
        """Obtiene un producto por su ID"""
        try:
            response = self.session.get(f"{self.base_url}/products/{product_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            self.request_error.emit(f"Error al obtener producto: {str(e)}")
            return None
    
    def create_product(self, product_data):
        """Crea un nuevo producto (POST /products)"""
        try:
            response = self.session.post(
                f"{self.base_url}/products",
                json=product_data
            )
            result = response.json() if response.status_code in [200, 201] else None
            if result:
                self.request_success.emit("create_product", result)
            return result
        except Exception as e:
            self.request_error.emit(f"Error al crear producto: {str(e)}")
            return None
    
    def update_product(self, product_id, product_data):
        """Actualiza un producto existente (PUT /products/<id>)"""
        try:
            response = self.session.put(
                f"{self.base_url}/products/{product_id}",
                json=product_data
            )
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("update_product", result)
            return result
        except Exception as e:
            self.request_error.emit(f"Error al actualizar producto: {str(e)}")
            return None
    
    def delete_product(self, product_id):
        """Elimina un producto (DELETE /products/<id>)"""
        try:
            response = self.session.delete(f"{self.base_url}/products/{product_id}")
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("delete_product", result)
            return result
        except Exception as e:
            self.request_error.emit(f"Error al eliminar producto: {str(e)}")
            return None
    
    # --- VENTAS (CRUD) ---
    def get_sales(self):
        """Obtiene la lista de ventas"""
        try:
            response = self.session.get(f"{self.base_url}/ventas")
            if response.status_code == 200:
                data = response.json()
                # Post-proceso: enriquecer ventas con nombres de cliente y usuario
                for v in data:
                    if "cliente" in v and isinstance(v["cliente"], dict):
                        v["cliente_nombre"] = v["cliente"].get("nombre", "Cliente")
                    else:
                        v["cliente_nombre"] = v.get("cliente_nombre", "Cliente")
                    if "usuario" in v and isinstance(v["usuario"], dict):
                        v["usuario_nombre"] = v["usuario"].get("nombre", "Usuario")
                    else:
                        v["usuario_nombre"] = v.get("usuario_nombre", "Usuario")
                self.data_received.emit({"type": "sales", "data": data})
                return data
            return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener ventas: {str(e)}")
            return []
    
    def get_sale(self, sale_id):
        """Obtiene una venta por su ID"""
        try:
            response = self.session.get(f"{self.base_url}/ventas/{sale_id}")
            if response.status_code == 200:
                v = response.json()
                # Enriquecimiento para UI
                if "cliente" in v and isinstance(v["cliente"], dict):
                    v["cliente_nombre"] = v["cliente"].get("nombre", "Cliente")
                if "usuario" in v and isinstance(v.get("usuario", {}), dict):
                    v["usuario_nombre"] = v["usuario"].get("nombre", "Usuario")
                # Nombres de productos en detalles
                if "detalles" in v:
                    for d in v["detalles"]:
                        if "producto" in d and isinstance(d["producto"], dict):
                            d["producto_nombre"] = d["producto"].get("nombre", "Producto")
                return v
            return None
        except Exception as e:
            self.request_error.emit(f"Error al obtener venta: {str(e)}")
            return None
    
    def create_sale(self, sale_data):
        """Crea una nueva venta"""
        try:
            response = self.session.post(
                f"{self.base_url}/ventas",
                json=sale_data
            )
            result = response.json() if response.status_code in [200, 201] else None
            if result:
                self.request_success.emit("create_sale", result)
            return result
        except Exception as e:
            self.request_error.emit(f"Error al crear venta: {str(e)}")
            return None
    
    def update_sale(self, sale_id, sale_data):
        """Actualiza una venta existente"""
        try:
            response = self.session.put(
                f"{self.base_url}/ventas/{sale_id}",
                json=sale_data
            )
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("update_sale", result)
            return result
        except Exception as e:
            self.request_error.emit(f"Error al actualizar venta: {str(e)}")
            return None
    
    def delete_sale(self, sale_id):
        """Elimina una venta"""
        try:
            response = self.session.delete(f"{self.base_url}/ventas/{sale_id}")
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("delete_sale", result)
            return result
        except Exception as e:
            self.request_error.emit(f"Error al eliminar venta: {str(e)}")
            return None
    
    # --- DASHBOARD ---
    def get_dashboard_data(self):
        """
        Obtiene los datos del dashboard desde el backend y emite la señal data_received.
        El diccionario emitido tiene la forma: {"type": "dashboard", "data": ...}
        """
        try:
            self.set_auth_header()
            url = f"{self.base_url}/dashboard"
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
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
