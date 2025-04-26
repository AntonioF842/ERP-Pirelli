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
