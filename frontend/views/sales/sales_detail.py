from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFormLayout, QLineEdit, QTableWidget, QTableWidgetItem, 
    QHeaderView, QFrame, QSpinBox, QDoubleSpinBox, QComboBox,
    QMessageBox, QDialog, QDateEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont, QIcon

class SalesDetailView(QWidget):
    """Vista detallada de una venta"""
    
    # Señales
    data_updated = pyqtSignal(dict)
    close_requested = pyqtSignal()
    
    def __init__(self, api_client, sale_id=None):
        super().__init__()
        
        self.api_client = api_client
        self.sale_id = sale_id
        self.sale_data = {}
        self.sale_items = []
        self.is_new_sale = sale_id is None
        
        # Conectar señales del API client
        self.api_client.request_success.connect(self.on_api_success)
        self.api_client.request_error.connect(self.on_api_error)
        
        self.init_ui()
        
        # Si es una venta existente, cargar los datos
        if not self.is_new_sale:
            self.load_sale_data()
        else:
            # Si es una nueva venta, inicializar con valores por defecto
            self.sale_data = {
                'id_venta': None,
                'id_cliente': None,
                'fecha': QDate.currentDate().toString("yyyy-MM-dd"),
                'total': 0.0,
                'estado': 'pendiente',
                'cliente': {
                    'id_cliente': None,
                    'nombre': '',
                    'contacto': '',
                    'telefono': '',
                    'email': '',
                }
            }
            self.update_form()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        
        # Título
        title_layout = QHBoxLayout()
        
        title_label = QLabel("Detalle de Venta")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # Panel de información principal
        info_panel = QFrame()
        info_panel.setFrameShape(QFrame.Shape.StyledPanel)
        info_panel.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 5px;
                border: 1px solid #ddd;
            }
        """)
        
        info_layout = QHBoxLayout(info_panel)
        
        # Formulario de datos de venta
        sale_form_layout = QFormLayout()
        sale_form_layout.setVerticalSpacing(10)
        sale_form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # ID Venta (solo mostrar, no editar)
        self.id_label = QLabel("Nuevo")
        sale_form_layout.addRow("ID Venta:", self.id_label)
        
        # Cliente
        self.client_combo = QComboBox()
        self.client_combo.setMinimumWidth(200)
        self.load_clients()
        sale_form_layout.addRow("Cliente:", self.client_combo)
        
        # Fecha
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        sale_form_layout.addRow("Fecha:", self.date_edit)
        
        # Estado
        self.status_combo = QComboBox()
        self.status_combo.addItems(["pendiente", "completada", "cancelada"])
        sale_form_layout.addRow("Estado:", self.status_combo)
        
        # Total (solo mostrar, se calcula)
        self.total_label = QLabel("$0.00")
        self.total_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.total_label.setStyleSheet("color: #d60000;")
        sale_form_layout.addRow("Total:", self.total_label)
        
        # Cliente info
        client_info_layout = QFormLayout()
        client_info_layout.setVerticalSpacing(10)
        client_info_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.client_contact_label = QLabel()
        client_info_layout.addRow("Contacto:", self.client_contact_label)
        
        self.client_phone_label = QLabel()
        client_info_layout.addRow("Teléfono:", self.client_phone_label)
        
        self.client_email_label = QLabel()
        client_info_layout.addRow("Email:", self.client_email_label)
        
        # Añadir formularios al panel de información
        info_layout.addLayout(sale_form_layout, 1)
        info_layout.addSpacing(20)
        info_layout.addLayout(client_info_layout, 1)
        
        # Tabla de productos
        items_title = QLabel("Productos")
        items_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        
        self.items_table = QTableWidget(0, 5)
        self.items_table.setHorizontalHeaderLabels(["Producto", "Precio Unitario", "Cantidad", "Subtotal", "Acciones"])
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.items_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.items_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.items_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.items_table.setColumnWidth(1, 120)
        self.items_table.setColumnWidth(2, 100)
        self.items_table.setColumnWidth(3, 120)
        self.items_table.setColumnWidth(4, 100)
        
        # Botones para agregar/editar productos
        items_buttons_layout = QHBoxLayout()
        
        self.add_product_button = QPushButton("Agregar Producto")
        self.add_product_button.setIcon(QIcon("resources/icons/add.png"))
        self.add_product_button.clicked.connect(self.show_add_product_dialog)
        
        items_buttons_layout.addWidget(self.add_product_button)
        items_buttons_layout.addStretch()
        
        # Botones de acción
        actions_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Guardar")
        self.save_button.setIcon(QIcon("resources/icons/save.png"))
        self.save_button.clicked.connect(self.save_sale)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setIcon(QIcon("resources/icons/cancel.png"))
        self.cancel_button.clicked.connect(self.close_detail)
        
        actions_layout.addStretch()
        actions_layout.addWidget(self.save_button)
        actions_layout.addWidget(self.cancel_button)
        
        # Agregar todo al layout principal
        main_layout.addLayout(title_layout)
        main_layout.addWidget(info_panel)
        main_layout.addWidget(items_title)
        main_layout.addWidget(self.items_table)
        main_layout.addLayout(items_buttons_layout)
        main_layout.addStretch()
        main_layout.addLayout(actions_layout)
        
        self.setLayout(main_layout)
    
    def load_sale_data(self):
        """Carga los datos de la venta desde la API"""
        if self.sale_id:
            # Simular llamada a la API (reemplazar con llamada real)
            self.api_client.get(f"/ventas/{self.sale_id}", "sale_detail")
    
    def load_clients(self):
        """Carga la lista de clientes desde la API"""
        # Simular llamada a la API (reemplazar con llamada real)
        self.api_client.get("/clientes", "client_list")
    
    def update_form(self):
        """Actualiza el formulario con los datos de la venta"""
        if not self.sale_data:
            return
        
        # Actualizar campos del formulario
        if self.sale_data.get('id_venta'):
            self.id_label.setText(str(self.sale_data['id_venta']))
        
        # Seleccionar cliente en el combo
        client_id = self.sale_data.get('id_cliente')
        if client_id:
            index = self.client_combo.findData(client_id)
            if index >= 0:
                self.client_combo.setCurrentIndex(index)
        
        # Fecha
        if self.sale_data.get('fecha'):
            try:
                date = QDate.fromString(self.sale_data['fecha'], "yyyy-MM-dd")
                self.date_edit.setDate(date)
            except:
                pass
        
        # Estado
        if self.sale_data.get('estado'):
            index = self.status_combo.findText(self.sale_data['estado'])
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
        
        # Actualizar información del cliente
        self.update_client_info()
        
        # Actualizar tabla de productos
        self.update_items_table()
        
        # Actualizar total
        self.update_total()
    
    def update_client_info(self):
        """Actualiza la información del cliente seleccionado"""
        client = self.sale_data.get('cliente', {})
        
        if client:
            self.client_contact_label.setText(client.get('contacto', ''))
            self.client_phone_label.setText(client.get('telefono', ''))
            self.client_email_label.setText(client.get('email', ''))
        else:
            self.client_contact_label.setText('')
            self.client_phone_label.setText('')
            self.client_email_label.setText('')
    
    def update_items_table(self):
        """Actualiza la tabla de productos de la venta"""
        self.items_table.setRowCount(0)
        
        for index, item in enumerate(self.sale_items):
            self.items_table.insertRow(index)
            
            # Nombre del producto
            product_name = QTableWidgetItem(item.get('producto', {}).get('nombre', ''))
            product_name.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.items_table.setItem(index, 0, product_name)
            
            # Precio unitario
            price = QTableWidgetItem(f"${item.get('precio_unitario', 0):.2f}")
            price.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            price.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.items_table.setItem(index, 1, price)
            
            # Cantidad
            quantity = QTableWidgetItem(str(item.get('cantidad', 0)))
            quantity.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            quantity.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.items_table.setItem(index, 2, quantity)
            
            # Subtotal
            subtotal = QTableWidgetItem(f"${item.get('subtotal', 0):.2f}")
            subtotal.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            subtotal.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.items_table.setItem(index, 3, subtotal)
            
            # Botón de eliminar
            delete_button = QPushButton("Eliminar")
            delete_button.setIcon(QIcon("resources/icons/delete.png"))
            delete_button.clicked.connect(lambda checked, row=index: self.remove_item(row))
            
            self.items_table.setCellWidget(index, 4, delete_button)
    
    def update_total(self):
        """Actualiza el total de la venta"""
        total = sum(item.get('subtotal', 0) for item in self.sale_items)
        self.total_label.setText(f"${total:.2f}")
        self.sale_data['total'] = total
    
    def show_add_product_dialog(self):
        """Muestra el diálogo para agregar un producto"""
        dialog = AddProductDialog(self.api_client)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_item = dialog.get_product_data()
            self.sale_items.append(new_item)
            self.update_items_table()
            self.update_total()
    
    def remove_item(self, row):
        """Elimina un producto de la lista"""
        if 0 <= row < len(self.sale_items):
            del self.sale_items[row]
            self.update_items_table()
            self.update_total()
    
    def save_sale(self):
        """Guarda la venta (nueva o actualización)"""
        # Recopilar datos del formulario
        self.sale_data['id_cliente'] = self.client_combo.currentData()
        self.sale_data['fecha'] = self.date_edit.date().toString("yyyy-MM-dd")
        self.sale_data['estado'] = self.status_combo.currentText()
        
        # Validar datos
        if not self.sale_data['id_cliente']:
            QMessageBox.warning(self, "Advertencia", "Debe seleccionar un cliente")
            return
        
        if not self.sale_items:
            QMessageBox.warning(self, "Advertencia", "Debe agregar al menos un producto")
            return
        
        # Preparar datos para enviar a la API
        payload = {
            'id_cliente': self.sale_data['id_cliente'],
            'fecha': self.sale_data['fecha'],
            'estado': self.sale_data['estado'],
            'total': self.sale_data['total'],
            'items': self.sale_items
        }
        
        # Enviar datos a la API
        if self.is_new_sale:
            self.api_client.post("/ventas", payload, "save_sale")
        else:
            self.api_client.put(f"/ventas/{self.sale_id}", payload, "update_sale")
    
    def on_api_success(self, endpoint, response_data):
        """Maneja las respuestas exitosas de la API"""
        if endpoint == "sale_detail":
            self.sale_data = response_data.get('venta', {})
            self.sale_items = response_data.get('detalles', [])
            self.update_form()
        
        elif endpoint == "client_list":
            self.client_combo.clear()
            clients = response_data.get('clientes', [])
            
            # Agregar ítem vacío
            self.client_combo.addItem("Seleccione un cliente", None)
            
            for client in clients:
                self.client_combo.addItem(client.get('nombre', ''), client.get('id_cliente'))
            
            # Si tenemos un cliente seleccionado
            if self.sale_data and self.sale_data.get('id_cliente'):
                index = self.client_combo.findData(self.sale_data['id_cliente'])
                if index >= 0:
                    self.client_combo.setCurrentIndex(index)
        
        elif endpoint in ["save_sale", "update_sale"]:
            # Mostrar mensaje de éxito
            operation = "creada" if self.is_new_sale else "actualizada"
            QMessageBox.information(self, "Éxito", f"Venta {operation} correctamente")
            
            # Emitir señal de actualización y cerrar
            self.data_updated.emit(response_data)
            self.close_detail()
    
    def on_api_error(self, error_message):
        """Maneja los errores de la API"""
        QMessageBox.critical(self, "Error", f"Error al procesar la operación: {error_message}")
    
    def close_detail(self):
        """Cierra la vista de detalle"""
        self.close_requested.emit()


class AddProductDialog(QDialog):
    """Diálogo para agregar un producto a la venta"""
    
    def __init__(self, api_client):
        super().__init__()
        
        self.api_client = api_client
        self.products = []
        self.selected_product = None
        
        self.init_ui()
        self.load_products()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Agregar Producto")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        # Selector de producto
        self.product_combo = QComboBox()
        self.product_combo.currentIndexChanged.connect(self.on_product_changed)
        form_layout.addRow("Producto:", self.product_combo)
        
        # Precio unitario
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setMinimum(0)
        self.price_spin.setMaximum(999999.99)
        self.price_spin.setDecimals(2)
        self.price_spin.setSingleStep(0.01)
        self.price_spin.setPrefix("$")
        self.price_spin.valueChanged.connect(self.update_subtotal)
        form_layout.addRow("Precio unitario:", self.price_spin)
        
        # Cantidad
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(9999)
        self.quantity_spin.valueChanged.connect(self.update_subtotal)
        form_layout.addRow("Cantidad:", self.quantity_spin)
        
        # Subtotal (solo lectura)
        self.subtotal_label = QLabel("$0.00")
        self.subtotal_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        form_layout.addRow("Subtotal:", self.subtotal_label)
        
        # Botones
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Agregar")
        self.add_button.setEnabled(False)
        self.add_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(form_layout)
        layout.addSpacing(15)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_products(self):
        """Carga la lista de productos desde la API"""
        # Simular llamada a la API (reemplazar con llamada real)
        # En un entorno real, esto usaría self.api_client.get("/productos", "product_list")
        
        # Simulamos datos de ejemplo para la demostración
        self.products = [
            {"id_producto": 1, "nombre": "Neumático P Zero 235/35ZR19", "precio": 250.00},
            {"id_producto": 2, "nombre": "Neumático Scorpion Verde 275/45R20", "precio": 300.00},
            {"id_producto": 3, "nombre": "Neumático Cinturato P7 225/45R17", "precio": 180.00}
        ]
        
        # Cargar productos en el combo
        self.product_combo.clear()
        self.product_combo.addItem("Seleccione un producto", None)
        
        for product in self.products:
            self.product_combo.addItem(product["nombre"], product["id_producto"])
    
    def on_product_changed(self, index):
        """Maneja el cambio de producto seleccionado"""
        if index <= 0:
            self.selected_product = None
            self.price_spin.setValue(0)
            self.add_button.setEnabled(False)
        else:
            product_id = self.product_combo.currentData()
            
            # Buscar el producto seleccionado
            for product in self.products:
                if product["id_producto"] == product_id:
                    self.selected_product = product
                    self.price_spin.setValue(product["precio"])
                    self.add_button.setEnabled(True)
                    break
        
        self.update_subtotal()
    
    def update_subtotal(self):
        """Actualiza el subtotal en función del precio y la cantidad"""
        price = self.price_spin.value()
        quantity = self.quantity_spin.value()
        subtotal = price * quantity
        
        self.subtotal_label.setText(f"${subtotal:.2f}")
    
    def get_product_data(self):
        """Devuelve los datos del producto para agregar a la venta"""
        return {
            "id_producto": self.selected_product["id_producto"],
            "producto": self.selected_product,
            "precio_unitario": self.price_spin.value(),
            "cantidad": self.quantity_spin.value(),
            "subtotal": self.price_spin.value() * self.quantity_spin.value()
        }