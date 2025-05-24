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
    def get_products(self, filters=None):
        """Obtiene la lista de productos con filtros opcionales"""
        try:
            # Envía los filtros como parámetros GET
            response = self.session.get(
                f"{self.base_url}/products",
                params=filters or {}  # Envía {} si filters es None
            )
            
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
    
    # --- EMPLEADOS (CRUD) ---
    def get_employees(self):
        """Obtiene la lista de empleados"""
        try:
            response = self.session.get(f"{self.base_url}/employees")
            if response.status_code == 200:
                data = response.json()
                self.data_received.emit({"type": "employees", "data": data})
                return data
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al obtener empleados: {response.status_code} {error_msg}")
                return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener empleados: {str(e)}")
            return []
    
    def get_areas_trabajo(self):
        """
        Obtiene la lista de áreas de trabajo desde el backend.
        Retorna una lista de diccionarios con las áreas.
        """
        try:
            response = self.session.get(f"{self.base_url}/work_areas")
            if response.status_code == 200:
                data = response.json()
                self.data_received.emit({"type": "work_areas", "data": data})
                return data
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al obtener áreas de trabajo: {response.status_code} {error_msg}")
                return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener áreas de trabajo: {str(e)}")
            return []
    
    def get_employee(self, employee_id):
        """Obtiene un empleado por su ID"""
        try:
            response = self.session.get(f"{self.base_url}/employees/{employee_id}")
            if response.status_code == 200:
                return response.json()
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al obtener empleado: {response.status_code} {error_msg}")
                return None
        except Exception as e:
            self.request_error.emit(f"Error al obtener empleado: {str(e)}")
            return None
    
    def create_employee(self, employee_data):
        """Crea un nuevo empleado"""
        try:
            response = self.session.post(
                f"{self.base_url}/employees",
                json=employee_data
            )
            result = response.json() if response.status_code in [200, 201] else None
            if result:
                self.request_success.emit("create_employee", result)
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al crear empleado: {response.status_code} {error_msg}")
            return result
        except Exception as e:
            self.request_error.emit(f"Error al crear empleado: {str(e)}")
            return None
    
    def update_employee(self, employee_id, employee_data):
        """Actualiza un empleado existente"""
        try:
            response = self.session.put(
                f"{self.base_url}/employees/{employee_id}",
                json=employee_data
            )
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("update_employee", result)
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al actualizar empleado: {response.status_code} {error_msg}")
            return result
        except Exception as e:
            self.request_error.emit(f"Error al actualizar empleado: {str(e)}")
            return None
    
    def delete_employee(self, employee_id):
        """Elimina un empleado por su ID"""
        try:
            response = self.session.delete(f"{self.base_url}/employees/{employee_id}")
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("delete_employee", result)
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al eliminar empleado: {response.status_code} {error_msg}")
            return result
        except Exception as e:
            self.request_error.emit(f"Error al eliminar empleado: {str(e)}")
            return None
    
    # --- ASISTENCIA (CRUD) ---
    def get_attendance(self):
        """Obtiene la lista de registros de asistencia"""
        try:
            response = self.session.get(f"{self.base_url}/attendance")
            if response.status_code == 200:
                data = response.json()
                self.data_received.emit({"type": "attendance", "data": data})
                return data
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al obtener registros de asistencia: {response.status_code} {error_msg}")
                return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener registros de asistencia: {str(e)}")
            return []
    
    def get_attendance_by_id(self, attendance_id):
        """Obtiene un registro de asistencia por su ID"""
        try:
            response = self.session.get(f"{self.base_url}/attendance/{attendance_id}")
            if response.status_code == 200:
                return response.json()
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al obtener registro de asistencia: {response.status_code} {error_msg}")
                return None
        except Exception as e:
            self.request_error.emit(f"Error al obtener registro de asistencia: {str(e)}")
            return None
    
    def create_attendance(self, attendance_data):
        """Crea un nuevo registro de asistencia"""
        try:
            response = self.session.post(
                f"{self.base_url}/attendance",
                json=attendance_data
            )
            result = response.json() if response.status_code in [200, 201] else None
            if result:
                self.request_success.emit("create_attendance", result)
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al crear registro de asistencia: {response.status_code} {error_msg}")
            return result
        except Exception as e:
            self.request_error.emit(f"Error al crear registro de asistencia: {str(e)}")
            return None
    
    def update_attendance(self, attendance_id, attendance_data):
        """Actualiza un registro de asistencia existente"""
        try:
            response = self.session.put(
                f"{self.base_url}/attendance/{attendance_id}",
                json=attendance_data
            )
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("update_attendance", result)
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al actualizar registro de asistencia: {response.status_code} {error_msg}")
            return result
        except Exception as e:
            self.request_error.emit(f"Error al actualizar registro de asistencia: {str(e)}")
            return None
    
    def delete_attendance(self, attendance_id):
        """Elimina un registro de asistencia por su ID"""
        try:
            response = self.session.delete(f"{self.base_url}/attendance/{attendance_id}")
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("delete_attendance", result)
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al eliminar registro de asistencia: {response.status_code} {error_msg}")
            return result
        except Exception as e:
            self.request_error.emit(f"Error al eliminar registro de asistencia: {str(e)}")
            return None
            
    # --- USUARIOS (CRUD) ---
    def get_users(self):
        """Obtiene la lista de usuarios"""
        try:
            response = self.session.get(f"{self.base_url}/users")
            if response.status_code == 200:
                data = response.json()
                self.data_received.emit({"type": "users", "data": data})
                return data
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al obtener usuarios: {response.status_code} {error_msg}")
                return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener usuarios: {str(e)}")
            return []
    
    def get_user(self, user_id):
        """Obtiene un usuario por su ID"""
        try:
            response = self.session.get(f"{self.base_url}/users/{user_id}")
            if response.status_code == 200:
                return response.json()
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al obtener usuario: {response.status_code} {error_msg}")
                return None
        except Exception as e:
            self.request_error.emit(f"Error al obtener usuario: {str(e)}")
            return None
    
    def create_user(self, user_data):
        """Crea un nuevo usuario"""
        try:
            response = self.session.post(
                f"{self.base_url}/users",
                json=user_data
            )
            result = response.json() if response.status_code in [200, 201] else None
            if result:
                self.request_success.emit("create_user", result)
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al crear usuario: {response.status_code} {error_msg}")
            return result
        except Exception as e:
            self.request_error.emit(f"Error al crear usuario: {str(e)}")
            return None
    
    def update_user(self, user_id, user_data):
        """Actualiza un usuario existente"""
        try:
            response = self.session.put(
                f"{self.base_url}/users/{user_id}",
                json=user_data
            )
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("update_user", result)
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al actualizar usuario: {response.status_code} {error_msg}")
            return result
        except Exception as e:
            self.request_error.emit(f"Error al actualizar usuario: {str(e)}")
            return None
    
    def delete_user(self, user_id):
        """Elimina un usuario por su ID"""
        try:
            response = self.session.delete(f"{self.base_url}/users/{user_id}")
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("delete_user", result)
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al eliminar usuario: {response.status_code} {error_msg}")
            return result
        except Exception as e:
            self.request_error.emit(f"Error al eliminar usuario: {str(e)}")
            return None
    
    # --- ÁREAS DE TRABAJO (CRUD) ---
    def get_work_areas(self):
        """Obtiene la lista de áreas de trabajo"""
        try:
            response = self.session.get(f"{self.base_url}/work_areas")
            if response.status_code == 200:
                data = response.json()
                self.data_received.emit({"type": "work_areas", "data": data})
                return data
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al obtener áreas de trabajo: {response.status_code} {error_msg}")
                return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener áreas de trabajo: {str(e)}")
            return []
    
    def get_work_area(self, area_id):
        """Obtiene un área de trabajo por su ID"""
        try:
            response = self.session.get(f"{self.base_url}/work_areas/{area_id}")
            if response.status_code == 200:
                return response.json()
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al obtener área de trabajo: {response.status_code} {error_msg}")
                return None
        except Exception as e:
            self.request_error.emit(f"Error al obtener área de trabajo: {str(e)}")
            return None
    
    def create_work_area(self, area_data):
        """Crea una nueva área de trabajo"""
        try:
            response = self.session.post(
                f"{self.base_url}/work_areas",
                json=area_data
            )
            result = response.json() if response.status_code in [200, 201] else None
            if result:
                self.request_success.emit("create_work_area", result)
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al crear área de trabajo: {response.status_code} {error_msg}")
            return result
        except Exception as e:
            self.request_error.emit(f"Error al crear área de trabajo: {str(e)}")
            return None
    
    def update_work_area(self, area_id, area_data):
        """Actualiza una área de trabajo existente"""
        try:
            response = self.session.put(
                f"{self.base_url}/work_areas/{area_id}",
                json=area_data
            )
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("update_work_area", result)
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al actualizar área de trabajo: {response.status_code} {error_msg}")
            return result
        except Exception as e:
            self.request_error.emit(f"Error al actualizar área de trabajo: {str(e)}")
            return None
    
    def delete_work_area(self, area_id):
        """Elimina una área de trabajo por su ID"""
        try:
            response = self.session.delete(f"{self.base_url}/work_areas/{area_id}")
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("delete_work_area", result)
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al eliminar área de trabajo: {response.status_code} {error_msg}")
            return result
        except Exception as e:
            self.request_error.emit(f"Error al eliminar área de trabajo: {str(e)}")
            return None
    
    # --- NÓMINAS / PAYROLL (CRUD) ---
    def get_payrolls(self):
        """Obtiene la lista de nóminas"""
        try:
            response = self.session.get(f"{self.base_url}/payroll")
            if response.status_code == 200:
                data = response.json()
                self.data_received.emit({"type": "payroll", "data": data})
                return data
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al obtener nóminas: {response.status_code} {error_msg}")
                return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener nóminas: {str(e)}")
            return []
    
    def get_payroll(self, payroll_id):
        """Obtiene una nómina por su ID"""
        try:
            response = self.session.get(f"{self.base_url}/payroll/{payroll_id}")
            if response.status_code == 200:
                return response.json()
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al obtener nómina: {response.status_code} {error_msg}")
                return None
        except Exception as e:
            self.request_error.emit(f"Error al obtener nómina: {str(e)}")
            return None
    
    def create_payroll(self, payroll_data):
        """Crea una nueva nómina"""
        try:
            response = self.session.post(
                f"{self.base_url}/payroll",
                json=payroll_data
            )
            result = response.json() if response.status_code in [200, 201] else None
            if result:
                self.request_success.emit("create_payroll", result)
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al crear nómina: {response.status_code} {error_msg}")
            return result
        except Exception as e:
            self.request_error.emit(f"Error al crear nómina: {str(e)}")
            return None
    
    def update_payroll(self, payroll_id, payroll_data):
        """Actualiza una nómina existente"""
        try:
            response = self.session.put(
                f"{self.base_url}/payroll/{payroll_id}",
                json=payroll_data
            )
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("update_payroll", result)
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al actualizar nómina: {response.status_code} {error_msg}")
            return result
        except Exception as e:
            self.request_error.emit(f"Error al actualizar nómina: {str(e)}")
            return None
    
    def delete_payroll(self, payroll_id):
        """Elimina una nómina por su ID"""
        try:
            response = self.session.delete(f"{self.base_url}/payroll/{payroll_id}")
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("delete_payroll", result)
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al eliminar nómina: {response.status_code} {error_msg}")
            return result
        except Exception as e:
            self.request_error.emit(f"Error al eliminar nómina: {str(e)}")
            return None

    # === MÉTODOS PARA INVENTARIO ===
    def get_inventory(self):
        """Obtiene la lista de items de inventario"""
        try:
            response = self.session.get(f"{self.base_url}/inventario")
            if response.status_code == 200:
                data = response.json()
                # Enriquecer resultado con nombre de producto si viene anidado
                for item in data:
                    if "producto" in item and isinstance(item["producto"], dict):
                        item["producto_nombre"] = item["producto"].get("nombre", "Producto")
                self.data_received.emit({"type": "inventory", "data": data})
                return data
            return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener inventario: {str(e)}")
            return []

    def get_inventory_item(self, inventory_id):
        """Obtiene un registro de inventario por su ID"""
        try:
            response = self.session.get(f"{self.base_url}/inventario/{inventory_id}")
            if response.status_code == 200:
                item = response.json()
                # Enriquecer para la vista
                if "producto" in item and isinstance(item["producto"], dict):
                    item["producto_nombre"] = item["producto"].get("nombre", "Producto")
                return item
            return None
        except Exception as e:
            self.request_error.emit(f"Error al obtener ítem de inventario: {str(e)}")
            return None

    def create_inventory_item(self, inv_data):
        """Crea un nuevo registro de inventario"""
        try:
            response = self.session.post(
                f"{self.base_url}/inventario",
                json=inv_data
            )
            result = response.json() if response.status_code in [200, 201] else None
            if result:
                self.request_success.emit("create_inventory_item", result)
            return result
        except Exception as e:
            self.request_error.emit(f"Error al crear ítem de inventario: {str(e)}")
            return None

    def update_inventory_item(self, inventory_id, inv_data):
        """Actualiza un ítem de inventario existente"""
        try:
            response = self.session.put(
                f"{self.base_url}/inventario/{inventory_id}",
                json=inv_data
            )
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("update_inventory_item", result)
            return result
        except Exception as e:
            self.request_error.emit(f"Error al actualizar ítem de inventario: {str(e)}")
            return None

    def delete_inventory_item(self, inventory_id):
        """Elimina un ítem de inventario por su ID"""
        try:
            response = self.session.delete(f"{self.base_url}/inventario/{inventory_id}")
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("delete_inventory_item", result)
            return result
        except Exception as e:
            self.request_error.emit(f"Error al eliminar ítem de inventario: {str(e)}")
            return None
    
    def delete_inventory(self, inventory_id):
        """Elimina un registro de inventario por su ID"""
        try:
            response = self.session.delete(f"{self.base_url}/inventario/{inventory_id}")
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("delete_inventory", result)
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al eliminar inventario: {response.status_code} {error_msg}")
            return result
        except Exception as e:
            self.request_error.emit(f"Error al eliminar inventario: {str(e)}")
            return None
    
    # --- MATERIALES (CRUD) ---
    def get_materials(self):
        """Obtiene la lista de materiales"""
        try:
            response = self.session.get(f"{self.base_url}/materiales")
            if response.status_code == 200:
                data = response.json()
                self.data_received.emit({"type": "materials", "data": data})
                return data
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al obtener materiales: {response.status_code} {error_msg}")
                return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener materiales: {str(e)}")
            return []
    
    def get_material(self, material_id):
        """Obtiene un material por su ID"""
        try:
            response = self.session.get(f"{self.base_url}/materiales/{material_id}")
            if response.status_code == 200:
                return response.json()
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al obtener material: {response.status_code} {error_msg}")
                return None
        except Exception as e:
            self.request_error.emit(f"Error al obtener material: {str(e)}")
            return None
    
    def create_material(self, material_data):
        """Crea un nuevo material"""
        try:
            response = self.session.post(
                f"{self.base_url}/materiales",
                json=material_data
            )
            result = response.json() if response.status_code in [200, 201] else None
            if result:
                self.request_success.emit("create_material", result)
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al crear material: {response.status_code} {error_msg}")
            return result
        except Exception as e:
            self.request_error.emit(f"Error al crear material: {str(e)}")
            return None
    
    def update_material(self, material_id, material_data):
        """Actualiza un material existente"""
        try:
            response = self.session.put(
                f"{self.base_url}/materiales/{material_id}",
                json=material_data
            )
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("update_material", result)
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al actualizar material: {response.status_code} {error_msg}")
            return result
        except Exception as e:
            self.request_error.emit(f"Error al actualizar material: {str(e)}")
            return None
    
    def delete_material(self, material_id):
        """Elimina un material por su ID"""
        try:
            response = self.session.delete(f"{self.base_url}/materiales/{material_id}")
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("delete_material", result)
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al eliminar material: {response.status_code} {error_msg}")
            return result
        except Exception as e:
            self.request_error.emit(f"Error al eliminar material: {str(e)}")
            return None
    
    # --- PROVEEDORES (CRUD) ---
    def get_suppliers(self):
        """Obtiene la lista de proveedores"""
        try:
            response = self.session.get(f"{self.base_url}/proveedores")
            if response.status_code == 200:
                data = response.json()
                self.data_received.emit({"type": "suppliers", "data": data})
                return data
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al obtener proveedores: {response.status_code} {error_msg}")
                return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener proveedores: {str(e)}")
            return []
    
    def get_supplier(self, supplier_id):
        """Obtiene un proveedor por su ID"""
        try:
            response = self.session.get(f"{self.base_url}/proveedores/{supplier_id}")
            if response.status_code == 200:
                return response.json()
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al obtener proveedor: {response.status_code} {error_msg}")
                return None
        except Exception as e:
            self.request_error.emit(f"Error al obtener proveedor: {str(e)}")
            return None
    
    def create_supplier(self, supplier_data):
        """Crea un nuevo proveedor"""
        try:
            response = self.session.post(
                f"{self.base_url}/proveedores",
                json={
                    "nombre": supplier_data.get("name", supplier_data.get("nombre", "")),
                    "contacto": supplier_data.get("contact", supplier_data.get("contacto", "")),
                    "telefono": supplier_data.get("phone", supplier_data.get("telefono", "")),
                    "email": supplier_data.get("email", ""),
                    "tipo_material": supplier_data.get("material_type", supplier_data.get("tipo_material", ""))
                }
            )
            result = response.json() if response.status_code in [200, 201] else None
            if result:
                self.request_success.emit("create_supplier", result)
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al crear proveedor: {response.status_code} {error_msg}")
            return result
        except Exception as e:
            self.request_error.emit(f"Error al crear proveedor: {str(e)}")
            return None
    
    def update_supplier(self, supplier_id, supplier_data):
        """Actualiza un proveedor existente"""
        try:
            response = self.session.put(
                f"{self.base_url}/proveedores/{supplier_id}",
                json={
                    "nombre": supplier_data.get("name", supplier_data.get("nombre", "")),
                    "contacto": supplier_data.get("contact", supplier_data.get("contacto", "")),
                    "telefono": supplier_data.get("phone", supplier_data.get("telefono", "")),
                    "email": supplier_data.get("email", ""),
                    "tipo_material": supplier_data.get("material_type", supplier_data.get("tipo_material", ""))
                }
            )
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("update_supplier", result)
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al actualizar proveedor: {response.status_code} {error_msg}")
            return result
        except Exception as e:
            self.request_error.emit(f"Error al actualizar proveedor: {str(e)}")
            return None
    
    def delete_supplier(self, supplier_id):
        """Elimina un proveedor por su ID"""
        try:
            response = self.session.delete(f"{self.base_url}/proveedores/{supplier_id}")
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("delete_supplier", result)
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al eliminar proveedor: {response.status_code} {error_msg}")
            return result
        except Exception as e:
            self.request_error.emit(f"Error al eliminar proveedor: {str(e)}")
            return None
    
    # --- Helpers de mapeo entre backend y frontend ---
    def _backend_to_frontend_order(self, order):
        """
        Convierte una orden desde la API a formato friendly de frontend.
        
        Maneja tanto el formato original del backend (con campos en español)
        como el formato nuevo (con campos en inglés) para asegurar compatibilidad.
        """
        # Determinar qué formato de backend estamos recibiendo
        if "id_orden_compra" in order:
            # Formato original (español)
            return {
                "po_id": order.get("id_orden_compra"),
                "supplier_id": order.get("id_proveedor"),
                "supplier_name": order.get("proveedor_name", order.get("nombre_proveedor", "")),
                "user_id": order.get("id_usuario"),
                "user_name": order.get("usuario_name", order.get("nombre_usuario", "")),
                "date": order.get("fecha"),
                "expected_delivery": order.get("fecha_entrega_esperada"),
                "status": order.get("estado", ""),
                "total": order.get("total"),
                "details": [self._backend_to_frontend_detail(d, is_spanish=True) 
                           for d in order.get("detalles", [])]
            }
        else:
            # Formato nuevo (inglés)
            return {
                "po_id": order.get("po_id"),
                "supplier_id": order.get("supplier_id"),
                "supplier_name": order.get("supplier_name", ""),
                "user_id": order.get("user_id"),
                "user_name": order.get("user_name", ""),
                "date": order.get("date"),
                "expected_delivery": order.get("delivery_date", order.get("expected_delivery")),
                "status": order.get("status", ""),
                "total": order.get("total"),
                "details": [self._backend_to_frontend_detail(d, is_spanish=False) 
                           for d in order.get("details", [])]
            }
    
    def _backend_to_frontend_detail(self, detail, is_spanish=True):
        """
        Convierte un detalle de orden desde el formato API al formato frontend.
        
        Args:
            detail: Diccionario con datos del detalle
            is_spanish: Indica si los campos vienen en español (True) o inglés (False)
        """
        if is_spanish:
            return {
                "detail_id": detail.get("id_detalle"),
                "material_id": detail.get("id_material"),
                "material_name": detail.get("material_name", detail.get("nombre_material", "")),
                "quantity": detail.get("cantidad"),
                "unit_price": detail.get("precio_unitario"),
                "subtotal": detail.get("subtotal")
            }
        else:
            return {
                "detail_id": detail.get("detail_id"),
                "material_id": detail.get("material_id"),
                "material_name": detail.get("material_name", ""),
                "quantity": detail.get("quantity"),
                "unit_price": detail.get("unit_price"),
                "subtotal": detail.get("subtotal")
            }

    def _frontend_to_backend_order(self, order):
        """
        Convierte una orden formato frontend a backend para el POST/PUT.

        Mantiene nombres de campos consistentes con el backend.
        """
        return {
            "supplier_id": order.get("supplier_id"),
            "user_id": order.get("user_id", 1),
            "date": order.get("date"),
            "delivery_date": order.get("expected_delivery") or order.get("delivery_date"),
            "status": order.get("status", "pendiente"),
            "total": order.get("total", 0),
            "details": [self._frontend_to_backend_detail(d) for d in order.get("details", [])]
        }

    def _frontend_to_backend_detail(self, detail):
        """
        Convierte un detalle de orden del formato frontend al formato backend.
        """
        return {
            "material_id": detail.get("material_id"),
            "quantity": detail.get("quantity"),
            "unit_price": detail.get("unit_price"),
            "subtotal": detail.get("subtotal", detail.get("quantity", 0) * detail.get("unit_price", 0))
        }

    
    def calculate_order_total(self, details):
        """
        Calcula el total de una orden a partir de sus detalles.
        
        Args:
            details: Lista de diccionarios con los detalles de la orden
            
        Returns:
            float: El total calculado de la orden
        """
        total = 0
        for detail in details:
            quantity = detail.get("quantity", 0)
            unit_price = detail.get("unit_price", 0)
            subtotal = detail.get("subtotal")
            
            if subtotal is not None:
                total += float(subtotal)
            elif quantity is not None and unit_price is not None:
                total += float(quantity) * float(unit_price)
                
        return round(total, 2)
    
    # --- ÓRDENES DE COMPRA (CRUD) ---
    def get_purchase_orders(self):
        """
        Obtiene la lista de órdenes de compra.
        
        Realiza la conversión de formato backend a frontend automáticamente.
        Emite la señal data_received con los datos convertidos.
        """
        try:
            response = self.session.get(f"{self.base_url}/ordenes_compra")
            if response.status_code == 200:
                data = response.json()
                # Adaptación de formato a frontend
                orders = [self._backend_to_frontend_order(o) for o in data]
                
                # Enriquecimiento adicional de datos si es necesario
                for order in orders:
                    # Asegurar que todos los campos críticos estén presentes
                    if not order.get("supplier_name") and order.get("supplier_id"):
                        supplier = self.get_supplier(order["supplier_id"])
                        if supplier:
                            order["supplier_name"] = supplier.get("nombre", "")
                
                self.data_received.emit({"type": "purchase_orders", "data": orders})
                return orders
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al obtener órdenes de compra: {response.status_code} {error_msg}")
                return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener órdenes de compra: {str(e)}")
            return []
    
    def get_purchase_order(self, order_id):
        """
        Obtiene una orden de compra por su ID.
        
        Args:
            order_id: ID de la orden a obtener
            
        Returns:
            dict: La orden en formato frontend o None si hubo error
        """
        try:
            response = self.session.get(f"{self.base_url}/ordenes_compra/{order_id}")
            if response.status_code == 200:
                order = response.json()
                converted_order = self._backend_to_frontend_order(order)
                
                # Enriquecer con información adicional si es necesario
                if not converted_order.get("supplier_name") and converted_order.get("supplier_id"):
                    supplier = self.get_supplier(converted_order["supplier_id"])
                    if supplier:
                        converted_order["supplier_name"] = supplier.get("nombre", "")
                
                # Enriquecer detalles con nombres de materiales si es necesario
                for detail in converted_order.get("details", []):
                    if not detail.get("material_name") and detail.get("material_id"):
                        material = self.get_material(detail["material_id"])
                        if material:
                            detail["material_name"] = material.get("nombre", "")
                
                return converted_order
            else:
                # Fallback: filtrar desde todas las órdenes
                all_orders = self.get_purchase_orders()
                for order in all_orders:
                    if order.get('po_id') == order_id:
                        return order
                
                self.request_error.emit(f"Error al obtener orden de compra: No se encontró la orden con ID {order_id}")
                return None
        except Exception as e:
            self.request_error.emit(f"Error al obtener orden de compra: {str(e)}")
            return None
    
    def create_purchase_order(self, order_data):
        """
        Crea una nueva orden de compra.
        
        Args:
            order_data: Diccionario con los datos de la orden en formato frontend
            
        Returns:
            dict: La orden creada en formato frontend o None si hubo error
        """
        try:
            # Validar datos antes de enviar
            if not order_data.get("supplier_id"):
                self.request_error.emit("Error: Se requiere un proveedor para crear la orden")
                return None
                
            if not order_data.get("details") or len(order_data.get("details", [])) == 0:
                self.request_error.emit("Error: La orden debe tener al menos un detalle")
                return None
            
            # Calcular/verificar el total si no está presente
            if not order_data.get("total"):
                order_data["total"] = self.calculate_order_total(order_data.get("details", []))
            
            # Convertir al formato esperado por el backend
            payload = self._frontend_to_backend_order(order_data)
            
            # Realizar la petición
            response = self.session.post(f"{self.base_url}/ordenes_compra", json=payload)
            
            if response.status_code in [200, 201]:
                result = response.json()
                processed_result = self._backend_to_frontend_order(result)
                self.request_success.emit("create_purchase_order", processed_result)
                return processed_result
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al crear orden de compra: {response.status_code} {error_msg}")
                return None
        except Exception as e:
            self.request_error.emit(f"Error al crear orden de compra: {str(e)}")
            return None
    
    def update_purchase_order(self, order_id, order_data):
        """
        Actualiza una orden de compra existente.
        
        Args:
            order_id: ID de la orden a actualizar
            order_data: Diccionario con los datos actualizados en formato frontend
            
        Returns:
            dict: La orden actualizada en formato frontend o None si hubo error
        """
        try:
            # Asegurar que el ID esté en los datos
            order_data["po_id"] = order_id
            
            # Validar datos antes de enviar
            if not order_data.get("supplier_id"):
                self.request_error.emit("Error: Se requiere un proveedor para la orden")
                return None
                
            if not order_data.get("details") or len(order_data.get("details", [])) == 0:
                self.request_error.emit("Error: La orden debe tener al menos un detalle")
                return None
            
            # Calcular/verificar el total si no está presente o ha cambiado
            calculated_total = self.calculate_order_total(order_data.get("details", []))
            if not order_data.get("total") or abs(float(order_data.get("total", 0)) - calculated_total) > 0.01:
                order_data["total"] = calculated_total
            
            # Convertir al formato esperado por el backend
            payload = self._frontend_to_backend_order(order_data)
            
            # Realizar la petición
            response = self.session.put(
                f"{self.base_url}/ordenes_compra/{order_id}",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                processed_result = self._backend_to_frontend_order(result)
                self.request_success.emit("update_purchase_order", processed_result)
                return processed_result
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al actualizar orden de compra: {response.status_code} {error_msg}")
                return None
        except Exception as e:
            self.request_error.emit(f"Error al actualizar orden de compra: {str(e)}")
            return None
    
    def delete_purchase_order(self, order_id):
        """Elimina una orden de compra por su ID"""
        try:
            response = self.session.delete(f"{self.base_url}/ordenes_compra/{order_id}")
            if response.status_code == 200:
                result = response.json()
                self.request_success.emit("delete_purchase_order", result)
                return result
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al eliminar orden de compra: {response.status_code} {error_msg}")
                return None
        except Exception as e:
            self.request_error.emit(f"Error al eliminar orden de compra: {str(e)}")
            return None
    
    # --- DETALLES ÓRDENES DE COMPRA ---
    def get_purchase_order_details(self):
        """
        Obtiene todos los detalles de órdenes de compra.
        
        Realiza la conversión de formato backend a frontend automáticamente.
        """
        try:
            response = self.session.get(f"{self.base_url}/ordenes_compra_detalle")
            if response.status_code == 200:
                data = response.json()
                
                # Convertir los detalles al formato frontend
                converted_details = []
                for detail in data:
                    converted_detail = self._backend_to_frontend_detail(detail, 
                                                                       is_spanish="id_detalle" in detail)
                    # Enriquecer con información adicional si es necesario
                    if not converted_detail.get("material_name") and converted_detail.get("material_id"):
                        material = self.get_material(converted_detail["material_id"])
                        if material:
                            converted_detail["material_name"] = material.get("nombre", "")
                    
                    converted_details.append(converted_detail)
                
                self.data_received.emit({"type": "purchase_order_details", "data": converted_details})
                return converted_details
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al obtener detalles de órdenes de compra: {response.status_code} {error_msg}")
                return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener detalles de órdenes de compra: {str(e)}")
            return []
    
    def get_purchase_order_detail(self, detail_id):
        """
        Obtiene un detalle de orden de compra por su ID.
        
        Args:
            detail_id: ID del detalle a obtener
            
        Returns:
            dict: El detalle en formato frontend o None si hubo error
        """
        try:
            response = self.session.get(f"{self.base_url}/ordenes_compra_detalle/{detail_id}")
            if response.status_code == 200:
                detail = response.json()
                # Convertir al formato frontend
                converted_detail = self._backend_to_frontend_detail(detail, 
                                                                  is_spanish="id_detalle" in detail)
                
                # Enriquecer con información adicional si es necesario
                if not converted_detail.get("material_name") and converted_detail.get("material_id"):
                    material = self.get_material(converted_detail["material_id"])
                    if material:
                        converted_detail["material_name"] = material.get("nombre", "")
                
                return converted_detail
            else:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                self.request_error.emit(f"Error al obtener detalle de orden de compra: {response.status_code} {error_msg}")
                return None
        except Exception as e:
            self.request_error.emit(f"Error al obtener detalle de orden de compra: {str(e)}")
            return None

    # --- Métodos de utilidad para órdenes de compra ---
    def validate_purchase_order(self, order_data):
        """
        Valida los datos de una orden de compra antes de enviarla al servidor.
        
        Args:
            order_data: Diccionario con los datos de la orden en formato frontend
            
        Returns:
            tuple: (bool, str) - (es_valido, mensaje_error)
        """
        # Validar campos obligatorios
        if not order_data.get("supplier_id"):
            return False, "Se requiere seleccionar un proveedor"
        
        if not order_data.get("date"):
            return False, "Se requiere una fecha para la orden"
        
        # Validar detalles
        details = order_data.get("details", [])
        if not details:
            return False, "La orden debe tener al menos un detalle"
        
        for i, detail in enumerate(details):
            if not detail.get("material_id"):
                return False, f"El detalle #{i+1} requiere un material"
            
            if not detail.get("quantity") or float(detail.get("quantity", 0)) <= 0:
                return False, f"El detalle #{i+1} requiere una cantidad válida"
            
            if not detail.get("unit_price") or float(detail.get("unit_price", 0)) < 0:
                return False, f"El detalle #{i+1} requiere un precio unitario válido"
        
        # Todo válido
        return True, ""
    
    def prepare_purchase_order_data(self, form_data):
        """
        Prepara los datos de un formulario para crear/actualizar una orden de compra.
        
        Args:
            form_data: Diccionario con los datos del formulario
            
        Returns:
            dict: Datos en formato frontend listos para enviar al backend
        """
        # Crear estructura base de la orden
        order = {
            "po_id": form_data.get("po_id"),
            "supplier_id": form_data.get("supplier_id"),
            "user_id": form_data.get("user_id", 1),  # Default a 1 si no se proporciona
            "date": form_data.get("date"),
            "expected_delivery": form_data.get("expected_delivery", form_data.get("delivery_date")),
            "status": form_data.get("status", "pendiente"),
            "details": []
        }
        
        # Procesar detalles
        details = form_data.get("details", [])
        for detail in details:
            # Calcular subtotal si no está presente
            quantity = float(detail.get("quantity", 0))
            unit_price = float(detail.get("unit_price", 0))
            subtotal = detail.get("subtotal")
            
            if subtotal is None:
                subtotal = quantity * unit_price
            
            # Añadir detalle procesado
            order["details"].append({
                "detail_id": detail.get("detail_id"),
                "material_id": detail.get("material_id"),
                "material_name": detail.get("material_name", ""),
                "quantity": quantity,
                "unit_price": unit_price,
                "subtotal": subtotal
            })
        
        # Calcular total de la orden
        order["total"] = self.calculate_order_total(order["details"])
        
        return order

    # --- ÓRDENES DE PRODUCCIÓN (CRUD) ---
    def get_production_orders(self):
        """Obtiene la lista de órdenes de producción"""
        try:
            response = self.session.get(f"{self.base_url}/ordenes_produccion")
            if response.status_code == 200:
                data = response.json()
                # Enriquecer datos con nombres de producto y usuario
                for order in data:
                    if "producto" in order and isinstance(order["producto"], dict):
                        order["producto_nombre"] = order["producto"].get("nombre", "Producto")
                    if "usuario" in order and isinstance(order["usuario"], dict):
                        order["usuario_nombre"] = order["usuario"].get("nombre", "Usuario")
                self.data_received.emit({"type": "production_orders", "data": data})
                return data
            return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener órdenes de producción: {str(e)}")
            return []

    def get_production_order(self, order_id):
        """Obtiene una orden de producción por su ID"""
        try:
            response = self.session.get(f"{self.base_url}/ordenes_produccion/{order_id}")
            if response.status_code == 200:
                order = response.json()
                # Enriquecer datos para la vista
                if "producto" in order and isinstance(order["producto"], dict):
                    order["producto_nombre"] = order["producto"].get("nombre", "Producto")
                if "usuario" in order and isinstance(order["usuario"], dict):
                    order["usuario_nombre"] = order["usuario"].get("nombre", "Usuario")
                return order
            return None
        except Exception as e:
            self.request_error.emit(f"Error al obtener orden de producción: {str(e)}")
            return None

    def create_production_order(self, order_data):
        """Crea una nueva orden de producción"""
        try:
            response = self.session.post(
                f"{self.base_url}/ordenes_produccion",
                json=order_data
            )
            result = response.json() if response.status_code in [200, 201] else None
            if result:
                self.request_success.emit("create_production_order", result)
                self.data_received.emit({"type": "production_order_created", "data": result})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al crear orden de producción: {str(e)}")
            return None

    def update_production_order(self, order_id, order_data):
        """Actualiza una orden de producción existente (PUT /ordenes_produccion/<id>)"""
        try:
            response = self.session.put(
                f"{self.base_url}/ordenes_produccion/{order_id}",
                json=order_data
            )
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("update_production_order", result)
            return result
        except Exception as e:
            self.request_error.emit(f"Error al actualizar orden de producción: {str(e)}")
            return None

    def delete_production_order(self, order_id):
        """Elimina una orden de producción"""
        try:
            response = self.session.delete(f"{self.base_url}/ordenes_produccion/{order_id}")
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("delete_production_order", result)
                self.data_received.emit({"type": "production_order_deleted", "data": {"id": order_id}})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al eliminar orden de producción: {str(e)}")
            return None 
        
        # --- PRODUCTION RECIPES (CRUD) ---
    def get_production_recipes(self):
        """Obtiene la lista de recetas de producción"""
        try:
            response = self.session.get(f"{self.base_url}/production_recipes")
            if response.status_code == 200:
                data = response.json()
                self.data_received.emit({"type": "production_recipes", "data": data})
                return data
            return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener recetas de producción: {str(e)}")
            return []
        
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

    def get_materials(self):
        """Obtiene la lista de materiales"""
        try:
            response = self.session.get(f"{self.base_url}/materials")
            if response.status_code == 200:
                data = response.json()
                self.data_received.emit({"type": "materials", "data": data})
                return data
            return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener materiales: {str(e)}")
            return []

    def get_production_recipe(self, recipe_id):
        """Obtiene una receta de producción por su ID"""
        try:
            response = self.session.get(f"{self.base_url}/production_recipes/{recipe_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            self.request_error.emit(f"Error al obtener receta de producción: {str(e)}")
            return None

    def create_production_recipe(self, recipe_data):
        """Crea una nueva receta de producción"""
        try:
            response = self.session.post(
                f"{self.base_url}/production_recipes",
                json=recipe_data
            )
            result = response.json() if response.status_code in [200, 201] else None
            if result:
                self.request_success.emit("create_production_recipe", result)
                self.data_received.emit({"type": "production_recipe_created", "data": result})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al crear receta de producción: {str(e)}")
            return None

    def update_production_recipe(self, recipe_id, recipe_data):
        """Actualiza una receta de producción existente"""
        try:
            response = self.session.put(
                f"{self.base_url}/production_recipes/{recipe_id}",
                json=recipe_data
            )
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("update_production_recipe", result)
                self.data_received.emit({"type": "production_recipe_updated", "data": result})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al actualizar receta de producción: {str(e)}")
            return None

    def delete_production_recipe(self, recipe_id):
        """Elimina una receta de producción"""
        try:
            response = self.session.delete(f"{self.base_url}/production_recipes/{recipe_id}")
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("delete_production_recipe", result)
                self.data_received.emit({"type": "production_recipe_deleted", "data": {"id": recipe_id}})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al eliminar receta de producción: {str(e)}")
            return None
        
    # --- CONTROL DE CALIDAD (CRUD) ---
    def get_quality_controls(self):
        """Obtiene la lista de controles de calidad"""
        try:
            response = self.session.get(f"{self.base_url}/quality_control")
            if response.status_code == 200:
                data = response.json()
                self.data_received.emit({"type": "quality_controls", "data": data})
                return data
            return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener controles de calidad: {str(e)}")
            return []

    def get_quality_control(self, control_id):
        """Obtiene un control de calidad por su ID"""
        try:
            response = self.session.get(f"{self.base_url}/quality_control/{control_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            self.request_error.emit(f"Error al obtener control de calidad: {str(e)}")
            return None

    def create_quality_control(self, control_data):
        """Crea un nuevo control de calidad"""
        try:
            response = self.session.post(
                f"{self.base_url}/quality_control",
                json=control_data
            )
            result = response.json() if response.status_code in [200, 201] else None
            if result:
                self.request_success.emit("create_quality_control", result)
                self.data_received.emit({"type": "quality_control_created", "data": result})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al crear control de calidad: {str(e)}")
            return None

    def update_quality_control(self, control_id, control_data):
        """Actualiza un control de calidad existente"""
        try:
            response = self.session.put(
                f"{self.base_url}/quality_control/{control_id}",
                json=control_data
            )
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("update_quality_control", result)
                self.data_received.emit({"type": "quality_control_updated", "data": result})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al actualizar control de calidad: {str(e)}")
            return None

    def delete_quality_control(self, control_id):
        """Elimina un control de calidad"""
        try:
            response = self.session.delete(f"{self.base_url}/quality_control/{control_id}")
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("delete_quality_control", result)
                self.data_received.emit({"type": "quality_control_deleted", "data": {"id": control_id}})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al eliminar control de calidad: {str(e)}")
            return None
        
    # --- PRODUCTION ASSETS (CRUD) ---
    def get_production_assets(self):
        """Obtiene la lista de activos de producción"""
        try:
            response = self.session.get(f"{self.base_url}/production_assets")
            if response.status_code == 200:
                data = response.json()
                self.data_received.emit({"type": "production_assets", "data": data})
                return data
            return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener activos de producción: {str(e)}")
            return []

    def get_production_asset(self, asset_id):
        """Obtiene un activo de producción por su ID"""
        try:
            response = self.session.get(f"{self.base_url}/production_assets/{asset_id}")
            if response.status_code == 200:
                return response.json()
            else:
                self.request_error.emit(f"Error al obtener activo de producción: Status {response.status_code}")
                return None
        except Exception as e:
            self.request_error.emit(f"Error al obtener activo de producción: {str(e)}")
            return None


    def create_production_asset(self, asset_data):
        """Crea un nuevo activo de producción"""
        try:
            response = self.session.post(
                f"{self.base_url}/production_assets",
                json=asset_data
            )
            result = response.json() if response.status_code in [200, 201] else None
            if result:
                self.request_success.emit("create_production_asset", result)
                self.data_received.emit({"type": "asset_created", "data": result})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al crear activo de producción: {str(e)}")
            return None

    def update_production_asset(self, asset_id, asset_data):
        """Actualiza un activo de producción existente"""
        try:
            response = self.session.put(
                f"{self.base_url}/production_assets/{asset_id}",
                json=asset_data
            )
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("update_production_asset", result)
                self.data_received.emit({"type": "asset_updated", "data": result})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al actualizar activo de producción: {str(e)}")
            return None

    def delete_production_asset(self, asset_id):
        """Elimina un activo de producción"""
        try:
            response = self.session.delete(f"{self.base_url}/production_assets/{asset_id}")
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("delete_production_asset", result)
                self.data_received.emit({"type": "asset_deleted", "data": {"id": asset_id}})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al eliminar activo de producción: {str(e)}")
            return None
        
    # --- MANTENIMIENTO (CRUD) ---
    def get_maintenance(self):
        """Obtiene la lista de registros de mantenimiento"""
        try:
            response = self.session.get(f"{self.base_url}/maintenance")
            if response.status_code == 200:
                data = response.json()
                self.data_received.emit({"type": "maintenance", "data": data})
                return data
            return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener registros de mantenimiento: {str(e)}")
            return []

    def get_maintenance_record(self, record_id):
        """Obtiene un registro de mantenimiento por su ID"""
        try:
            response = self.session.get(f"{self.base_url}/maintenance/{record_id}")
            if response.status_code == 200:
                record = response.json()
                # Enriquecer datos para la vista si es necesario
                return record
            return None
        except Exception as e:
            self.request_error.emit(f"Error al obtener registro de mantenimiento: {str(e)}")
            return None

    def create_maintenance(self, maintenance_data):
        """Crea un nuevo registro de mantenimiento"""
        try:
            response = self.session.post(
                f"{self.base_url}/maintenance",
                json=maintenance_data
            )
            result = response.json() if response.status_code in [200, 201] else None
            if result:
                self.request_success.emit("create_maintenance", result)
                self.data_received.emit({"type": "maintenance_created", "data": result})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al crear registro de mantenimiento: {str(e)}")
            return None

    def update_maintenance(self, record_id, maintenance_data):
        """Actualiza un registro de mantenimiento existente"""
        try:
            response = self.session.put(
                f"{self.base_url}/maintenance/{record_id}",
                json=maintenance_data
            )
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("update_maintenance", result)
                self.data_received.emit({"type": "maintenance_updated", "data": result})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al actualizar registro de mantenimiento: {str(e)}")
            return None

    def delete_maintenance(self, record_id):
        """Elimina un registro de mantenimiento"""
        try:
            response = self.session.delete(f"{self.base_url}/maintenance/{record_id}")
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("delete_maintenance", result)
                self.data_received.emit({"type": "maintenance_deleted", "data": {"id": record_id}})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al eliminar registro de mantenimiento: {str(e)}")
            return None
    
    # --- MÉTODOS AUXILIARES PARA MANTENIMIENTO ---
    def get_production_assets(self):
        """Obtiene la lista de activos de producción"""
        try:
            response = self.session.get(f"{self.base_url}/production_assets")
            if response.status_code == 200:
                data = response.json()
                self.data_received.emit({"type": "production_assets", "data": data})
                return data
            return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener activos de producción: {str(e)}")
            return []

    def get_employees(self):
        """Obtiene la lista de empleados"""
        try:
            response = self.session.get(f"{self.base_url}/employees")
            if response.status_code == 200:
                data = response.json()
                self.data_received.emit({"type": "employees", "data": data})
                return data
            return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener empleados: {str(e)}")
            return []
        
    # --- PROYECTOS I+D (CRUD) ---
    def get_r_d_projects(self):
        """Obtiene la lista de proyectos de I+D"""
        try:
            response = self.session.get(f"{self.base_url}/r_d_projects")
            if response.status_code == 200:
                data = response.json()
                self.data_received.emit({"type": "r_d_projects", "data": data})
                return data
            return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener proyectos I+D: {str(e)}")
            return []

    def get_r_d_project(self, project_id):
        """Obtiene un proyecto de I+D por su ID"""
        try:
            response = self.session.get(f"{self.base_url}/r_d_projects/{project_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            self.request_error.emit(f"Error al obtener proyecto I+D: {str(e)}")
            return None

    def create_r_d_project(self, project_data):
        try:
            response = self.session.post(
                f"{self.base_url}/r_d_projects",
                json=project_data
            )
            result = response.json() if response.status_code in [200, 201] else None
            if result:
                self.request_success.emit("create_r_d_project", result)
                self.data_received.emit({"type": "r_d_project_created", "data": result})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al crear proyecto I+D: {str(e)}")
            return None

    def update_r_d_project(self, project_id, project_data):
        try:
            response = self.session.put(
                f"{self.base_url}/r_d_projects/{project_id}",
                json=project_data
            )
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("update_r_d_project", result)
                self.data_received.emit({"type": "r_d_project_updated", "data": result})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al actualizar proyecto I+D: {str(e)}")
            return None

    def delete_r_d_project(self, project_id):
        try:
            response = self.session.delete(f"{self.base_url}/r_d_projects/{project_id}")
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("delete_r_d_project", result)
                self.data_received.emit({"type": "r_d_project_deleted", "data": {"id": project_id}})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al eliminar proyecto I+D: {str(e)}")
            return None
    
    # --- NORMATIVAS LEGALES (CRUD) ---
    def get_legal_regulations(self):
        """Obtiene la lista de normativas legales"""
        try:
            response = self.session.get(f"{self.base_url}/legal_regulations")
            if response.status_code == 200:
                data = response.json()
                self.data_received.emit({"type": "legal_regulations", "data": data})
                return data
            return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener normativas legales: {str(e)}")
            return []

    def get_legal_regulation(self, regulation_id):
        """Obtiene una normativa legal por su ID"""
        try:
            response = self.session.get(f"{self.base_url}/legal_regulations/{regulation_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            self.request_error.emit(f"Error al obtener normativa legal: {str(e)}")
            return None

    def create_legal_regulation(self, regulation_data):
        """Crea una nueva normativa legal"""
        try:
            response = self.session.post(
                f"{self.base_url}/legal_regulations",
                json=regulation_data
            )
            result = response.json() if response.status_code in [200, 201] else None
            if result:
                self.request_success.emit("create_legal_regulation", result)
                self.data_received.emit({"type": "legal_regulation_created", "data": result})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al crear normativa legal: {str(e)}")
            return None

    def update_legal_regulation(self, regulation_id, regulation_data):
        """Actualiza una normativa legal existente"""
        try:
            response = self.session.put(
                f"{self.base_url}/legal_regulations/{regulation_id}",
                json=regulation_data
            )
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("update_legal_regulation", result)
                self.data_received.emit({"type": "legal_regulation_updated", "data": result})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al actualizar normativa legal: {str(e)}")
            return None

    def delete_legal_regulation(self, regulation_id):
        """Elimina una normativa legal"""
        try:
            response = self.session.delete(f"{self.base_url}/legal_regulations/{regulation_id}")
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("delete_legal_regulation", result)
                self.data_received.emit({"type": "legal_regulation_deleted", "data": {"id": regulation_id}})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al eliminar normativa legal: {str(e)}")
            return None
        
    # --- INCIDENTES (CRUD) ---
    def get_incidents(self):
        """Obtiene la lista de incidentes"""
        try:
            response = self.session.get(f"{self.base_url}/incidents")
            if response.status_code == 200:
                data = response.json()
                self.data_received.emit({"type": "incidents", "data": data})
                return data
            return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener incidentes: {str(e)}")
            return []

    def get_incident(self, incident_id):
        """Obtiene un incidente por su ID"""
        try:
            response = self.session.get(f"{self.base_url}/incidents/{incident_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            self.request_error.emit(f"Error al obtener incidente: {str(e)}")
            return None

    def create_incident(self, incident_data):
        """Crea un nuevo incidente"""
        try:
            response = self.session.post(
                f"{self.base_url}/incidents",
                json=incident_data
            )
            result = response.json() if response.status_code in [200, 201] else None
            if result:
                self.request_success.emit("create_incident", result)
                self.data_received.emit({"type": "incident_created", "data": result})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al crear incidente: {str(e)}")
            return None

    def update_incident(self, incident_id, incident_data):
        """Actualiza un incidente existente"""
        try:
            response = self.session.put(
                f"{self.base_url}/incidents/{incident_id}",
                json=incident_data
            )
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("update_incident", result)
                self.data_received.emit({"type": "incident_updated", "data": result})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al actualizar incidente: {str(e)}")
            return None

    def delete_incident(self, incident_id):
        """Elimina un incidente"""
        try:
            response = self.session.delete(f"{self.base_url}/incidents/{incident_id}")
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("delete_incident", result)
                self.data_received.emit({"type": "incident_deleted", "data": {"id": incident_id}})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al eliminar incidente: {str(e)}")
            return None
        
     # --- SYSTEM CONFIGURATION (CRUD) ---
    def get_system_configurations(self):
        """Obtiene la lista de configuraciones del sistema"""
        try:
            response = self.session.get(f"{self.base_url}/system_configuration")
            if response.status_code == 200:
                data = response.json()
                self.data_received.emit({"type": "system_configurations", "data": data})
                return data
            return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener configuraciones del sistema: {str(e)}")
            return []

    def get_system_configuration(self, config_id):
        """Obtiene una configuración por su ID"""
        try:
            response = self.session.get(f"{self.base_url}/system_configuration/{config_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            self.request_error.emit(f"Error al obtener configuración: {str(e)}")
            return None

    def create_system_configuration(self, config_data):
        """Crea una nueva configuración del sistema"""
        try:
            response = self.session.post(
                f"{self.base_url}/system_configuration",
                json=config_data
            )
            result = response.json() if response.status_code in [200, 201] else None
            if result:
                self.request_success.emit("create_system_configuration", result)
                self.data_received.emit({"type": "configuration_created", "data": result})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al crear configuración: {str(e)}")
            return None

    def update_system_configuration(self, config_id, config_data):
        """Actualiza una configuración existente"""
        try:
            response = self.session.put(
                f"{self.base_url}/system_configuration/{config_id}",
                json=config_data
            )
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("update_system_configuration", result)
                self.data_received.emit({"type": "configuration_updated", "data": result})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al actualizar configuración: {str(e)}")
            return None

    def delete_system_configuration(self, config_id):
        """Elimina una configuración"""
        try:
            response = self.session.delete(f"{self.base_url}/system_configuration/{config_id}")
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("delete_system_configuration", result)
                self.data_received.emit({"type": "configuration_deleted", "data": {"id": config_id}})
            return result
        except Exception as e:
            self.request_error.emit(f"Error al eliminar configuración: {str(e)}")
            return None
        
    # --- SALES DETAILS (CRUD) ---
    def get_sales_details(self, params=None):
        """Obtiene la lista de detalles de venta"""
        try:
            response = self.session.get(f"{self.base_url}/sales-details", params=params)
            if response.status_code == 200:
                data = response.json()
                # Enriquecer datos para la vista
                for d in data:
                    if "producto" in d and isinstance(d["producto"], dict):
                        d["producto_nombre"] = d["producto"].get("nombre", "Producto")
                        d["producto_codigo"] = d["producto"].get("codigo", "")
                    if "venta" in d and isinstance(d["venta"], dict):
                        d["venta_fecha"] = d["venta"].get("fecha", "")
                self.data_received.emit({"type": "sales_details", "data": data})
                return data
            return []
        except Exception as e:
            self.request_error.emit(f"Error al obtener detalles de venta: {str(e)}")
            return []

    def get_sales_detail(self, detail_id):
        """Obtiene un detalle de venta por su ID"""
        try:
            response = self.session.get(f"{self.base_url}/sales-details/{detail_id}")
            if response.status_code == 200:
                d = response.json()
                # Enriquecer datos para la vista
                if "producto" in d and isinstance(d["producto"], dict):
                    d["producto_nombre"] = d["producto"].get("nombre", "Producto")
                    d["producto_codigo"] = d["producto"].get("codigo", "")
                    d["producto_categoria"] = d["producto"].get("categoria", "")
                if "venta" in d and isinstance(d["venta"], dict):
                    d["venta_fecha"] = d["venta"].get("fecha", "")
                    d["venta_estado"] = d["venta"].get("estado", "")
                return d
            return None
        except Exception as e:
            self.request_error.emit(f"Error al obtener detalle de venta: {str(e)}")
            return None

    def create_sales_detail(self, detail_data):
        """Crea un nuevo detalle de venta"""
        try:
            response = self.session.post(
                f"{self.base_url}/sales-details",
                json=detail_data
            )
            result = response.json() if response.status_code in [200, 201] else None
            if result:
                self.request_success.emit("create_sales_detail", result)
            return result
        except Exception as e:
            self.request_error.emit(f"Error al crear detalle de venta: {str(e)}")
            return None

    def update_sales_detail(self, detail_id, detail_data):
        """Actualiza un detalle de venta existente"""
        try:
            response = self.session.put(
                f"{self.base_url}/sales-details/{detail_id}",
                json=detail_data
            )
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("update_sales_detail", result)
            return result
        except Exception as e:
            self.request_error.emit(f"Error al actualizar detalle de venta: {str(e)}")
            return None

    def delete_sales_detail(self, detail_id):
        """Elimina un detalle de venta"""
        try:
            response = self.session.delete(f"{self.base_url}/sales-details/{detail_id}")
            result = response.json() if response.status_code == 200 else None
            if result:
                self.request_success.emit("delete_sales_detail", result)
            return result
        except Exception as e:
            self.request_error.emit(f"Error al eliminar detalle de venta: {str(e)}")
            return None