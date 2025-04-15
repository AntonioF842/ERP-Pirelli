from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                           QLabel, QLineEdit, QDateEdit, QComboBox, QPushButton,
                           QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                           QSpinBox, QDoubleSpinBox, QDialogButtonBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon

class SalesForm(QDialog):
    """Formulario para crear o editar ventas"""
    
    def __init__(self, api_client, sale_id=None):
        super().__init__()
        
        self.api_client = api_client
        self.sale_id = sale_id
        self.edit_mode = sale_id is not None
        self.sale_data = {}
        self.products = []
        self.clients = []
        self.sale_items = []
        
        # Conectar señales
        self.api_client.request_success.connect(self.on_request_success)
        self.api_client.request_error.connect(self.on_request_error)
        
        # Configurar ventana
        self.setWindowTitle("Nueva Venta" if not self.edit_mode else "Editar Venta")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        self.init_ui()
        
        # Cargar datos necesarios
        self.load_products()
        self.load_clients()
        
        # Si estamos en modo edición, cargar los datos de la venta
        if self.edit_mode:
            self.load_sale_data()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        
        # Título
        title_label = QLabel("Nueva Venta" if not self.edit_mode else "Editar Venta")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        # Formulario de datos generales
        general_form = QFormLayout()
        
        # Selección de cliente
        self.client_combo = QComboBox()
        self.client_combo.setMinimumWidth(300)
        
        # Fecha
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        
        # Estado
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Pendiente", "Completada", "Cancelada"])
        
        # Total (solo lectura)
        self.total_edit = QLineEdit()
        self.total_edit.setReadOnly(True)
        self.total_edit.setText("$0.00")
        
        general_form.addRow("Cliente:", self.client_combo)
        general_form.addRow("Fecha:", self.date_edit)
        general_form.addRow("Estado:", self.status_combo)
        general_form.addRow("Total:", self.total_edit)
        
        # Sección de productos
        products_label = QLabel("Productos")
        products_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        # Barra de herramientas de productos
        products_toolbar = QHBoxLayout()
        
        # Selección de producto
        self.product_combo = QComboBox()
        self.product_combo.setMinimumWidth(300)
        
        # Cantidad
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(1000)
        self.quantity_spin.setValue(1)
        
        # Botón para agregar producto
        add_product_btn = QPushButton("Agregar Producto")
        add_product_btn.setIcon(QIcon("resources/icons/add.png"))
        add_product_btn.clicked.connect(self.add_product_to_sale)
        
        products_toolbar.addWidget(QLabel("Producto:"))
        products_toolbar.addWidget(self.product_combo)
        products_toolbar.addWidget(QLabel("Cantidad:"))
        products_toolbar.addWidget(self.quantity_spin)
        products_toolbar.addWidget(add_product_btn)
        
        # Tabla de productos en la venta
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels([
            "Código", "Producto", "Cantidad", "Precio Unitario", "Subtotal", "Acciones"
        ])
        
        # Configurar tabla
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.products_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.products_table.setAlternatingRowColors(True)
        
        # Botones de acción
        buttons = QDialogButtonBox()
        
        if self.edit_mode:
            save_btn = buttons.addButton("Actualizar", QDialogButtonBox.ButtonRole.AcceptRole)
        else:
            save_btn = buttons.addButton("Guardar", QDialogButtonBox.ButtonRole.AcceptRole)
            
        cancel_btn = buttons.addButton("Cancelar", QDialogButtonBox.ButtonRole.RejectRole)
        
        buttons.accepted.connect(self.save_sale)
        buttons.rejected.connect(self.reject)
        
        # Armar layout
        main_layout.addWidget(title_label)
        main_layout.addLayout(general_form)
        main_layout.addWidget(products_label)
        main_layout.addLayout(products_toolbar)
        main_layout.addWidget(self.products_table)
        main_layout.addWidget(buttons)
        
        self.setLayout(main_layout)
    
    def load_products(self):
        """Carga la lista de productos disponibles"""
        self.api_client.get("productos")
    
    def load_clients(self):
        """Carga la lista de clientes"""
        self.api_client.get("clientes")
    
    def load_sale_data(self):
        """Carga los datos de la venta en modo edición"""
        self.api_client.get(f"ventas/{self.sale_id}")
    
    def on_request_success(self, endpoint, data):
        """Maneja las respuestas exitosas de la API"""
        if endpoint == "productos":
            self.products = data
            
            # Llenar el combo de productos
            self.product_combo.clear()
            for product in self.products:
                self.product_combo.addItem(
                    f"{product.get('codigo')} - {product.get('nombre')}", 
                    product.get('id_producto')
                )
                
        elif endpoint == "clientes":
            self.clients = data
            
            # Llenar el combo de clientes
            self.client_combo.clear()
            for client in self.clients:
                self.client_combo.addItem(
                    client.get('nombre'),
                    client.get('id_cliente')
                )
                
        elif endpoint.startswith("ventas/") and self.edit_mode:
            # Cargar datos de la venta existente
            self.sale_data = data
            
            # Establecer los valores del formulario
            client_index = self.client_combo.findData(self.sale_data.get('id_cliente'))
            if client_index >= 0:
                self.client_combo.setCurrentIndex(client_index)
                
            self.date_edit.setDate(QDate.fromString(self.sale_data.get('fecha'), "yyyy-MM-dd"))
            
            status_index = self.status_combo.findText(self.sale_data.get('estado').capitalize())
            if status_index >= 0:
                self.status_combo.setCurrentIndex(status_index)
                
            self.total_edit.setText(f"${self.sale_data.get('total', 0):,.2f}")
            
            # Cargar productos de la venta
            self.sale_items = self.sale_data.get('detalles', [])
            self.update_products_table()
    
    def update_products_table(self):
        """Actualiza la tabla de productos en la venta"""
        self.products_table.setRowCount(0)
        
        total = 0
        
        for row, item in enumerate(self.sale_items):
            self.products_table.insertRow(row)
            
            # Buscar información del producto
            product_info = next(
                (p for p in self.products if p.get('id_producto') == item.get('id_producto')),
                {}
            )
            
            # Datos del producto
            self.products_table.setItem(row, 0, QTableWidgetItem(product_info.get('codigo', 'N/A')))
            self.products_table.setItem(row, 1, QTableWidgetItem(product_info.get('nombre', 'N/A')))
            self.products_table.setItem(row, 2, QTableWidgetItem(str(item.get('cantidad', 0))))
            
            # Precio unitario
            precio_unitario = item.get('precio_unitario', 0)
            precio_item = QTableWidgetItem(f"${precio_unitario:,.2f}")
            precio_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.products_table.setItem(row, 3, precio_item)
            
            # Subtotal
            subtotal = item.get('subtotal', precio_unitario * item.get('cantidad', 0))
            subtotal_item = QTableWidgetItem(f"${subtotal:,.2f}")
            subtotal_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.products_table.setItem(row, 4, subtotal_item)
            
            total += subtotal
            
            # Botón de eliminar
            delete_btn = QPushButton()
            delete_btn.setIcon(QIcon("resources/icons/delete.png"))
            delete_btn.setToolTip("Eliminar producto")
            delete_btn.clicked.connect(lambda checked, idx=row: self.remove_product_from_sale(idx))
            
            self.products_table.setCellWidget(row, 5, delete_btn)
        
        # Actualizar el total
        self.total_edit.setText(f"${total:,.2f}")
    
    def add_product_to_sale(self):
        """Agrega un producto a la venta"""
        product_id = self.product_combo.currentData()
        quantity = self.quantity_spin.value()
        
        if product_id is None:
            QMessageBox.warning(self, "Advertencia", "Por favor seleccione un producto.")
            return
        
        # Buscar información del producto
        product_info = next((p for p in self.products if p.get('id_producto') == product_id), None)
        
        if not product_info:
            QMessageBox.warning(self, "Advertencia", "Producto no encontrado.")
            return
        
        # Verificar si el producto ya está en la venta
        existing_item = next(
            (item for item in self.sale_items if item.get('id_producto') == product_id),
            None
        )
        
        if existing_item:
            # Actualizar cantidad
            existing_item['cantidad'] += quantity
            existing_item['subtotal'] = existing_item['precio_unitario'] * existing_item['cantidad']
        else:
            # Agregar nuevo item
            precio = float(product_info.get('precio', 0))
            
            new_item = {
                'id_producto': product_id,
                'cantidad': quantity,
                'precio_unitario': precio,
                'subtotal': precio * quantity
            }
            
            self.sale_items.append(new_item)
        
        # Actualizar tabla
        self.update_products_table()
    
    def remove_product_from_sale(self, row_index):
        """Elimina un producto de la venta"""
        if 0 <= row_index < len(self.sale_items):
            self.sale_items.pop(row_index)
            self.update_products_table()
    
    def save_sale(self):
        """Guarda la venta"""
        # Validar datos
        if not self.sale_items:
            QMessageBox.warning(self, "Advertencia", "Debe agregar al menos un producto a la venta.")
            return
        
        client_id = self.client_combo.currentData()
        if client_id is None:
            QMessageBox.warning(self, "Advertencia", "Por favor seleccione un cliente.")
            return
        
        # Calcular total
        total = sum(item.get('subtotal', 0) for item in self.sale_items)
        
        # Crear objeto de venta
        sale = {
            'id_cliente': client_id,
            'fecha': self.date_edit.date().toString("yyyy-MM-dd"),
            'estado': self.status_combo.currentText().lower(),
            'total': total,
            'detalles': self.sale_items
        }
        
        if self.edit_mode:
            # Actualizar venta existente
            self.api_client.put(f"ventas/{self.sale_id}", sale)
        else:
            # Crear nueva venta
            self.api_client.post("ventas", sale)
        
        # Cerrar formulario
        self.accept()
    
    def on_request_error(self, error_message):
        """Maneja errores de la API"""
        QMessageBox.critical(self, "Error", f"Error: {error_message}")