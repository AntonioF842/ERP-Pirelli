from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QSpinBox,
    QDateEdit, QTextEdit, QFormLayout, 
    QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont
from utils.theme import Theme

class ProductionOrderForm(QDialog):
    """Formulario para crear o editar órdenes de producción"""
    
    order_saved = pyqtSignal(dict)
    
    def __init__(self, api_client, order_data=None, parent=None):
        super().__init__(parent)
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.order_data = order_data.to_dict() if hasattr(order_data, 'to_dict') else order_data
        self.edit_mode = order_data is not None
        
        # Datos para combobox
        self.products = []
        self.users = []
        
        self.init_ui()
        self.load_combobox_data()
        
        if self.edit_mode:
            self.fill_form()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Nueva Orden de Producción" if not self.edit_mode else "Editar Orden de Producción")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        title = "Nueva Orden de Producción" if not self.edit_mode else "Editar Orden de Producción"
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setProperty("heading", True)
        
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Producto
        self.product_combo = QComboBox()
        form_layout.addRow("Producto:", self.product_combo)
        
        # Cantidad
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, 9999)
        form_layout.addRow("Cantidad:", self.quantity_input)
        
        # Fecha Inicio
        self.start_date_input = QDateEdit()
        self.start_date_input.setDate(QDate.currentDate())
        self.start_date_input.setCalendarPopup(True)
        form_layout.addRow("Fecha Inicio:", self.start_date_input)
        
        # Fecha Fin (opcional)
        self.end_date_input = QDateEdit()
        self.end_date_input.setDate(QDate.currentDate().addDays(7))
        self.end_date_input.setCalendarPopup(True)
        form_layout.addRow("Fecha Fin (opcional):", self.end_date_input)
        
        # Estado (solo visible en edición)
        self.status_combo = QComboBox()
        if self.edit_mode:
            from models.production_order_model import ProductionOrder
            for key, value in ProductionOrder.ESTADOS.items():
                self.status_combo.addItem(value, key)
            form_layout.addRow("Estado:", self.status_combo)
        
        # Usuario responsable
        self.user_combo = QComboBox()
        form_layout.addRow("Responsable:", self.user_combo)
        
        # Notas/observaciones
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        form_layout.addRow("Notas:", self.notes_input)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Guardar")
        self.save_button.setFixedHeight(40)
        self.save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_button.setProperty("secondary", True)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setFixedHeight(40)
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        
        self.save_button.clicked.connect(self.save_order)
        self.cancel_button.clicked.connect(self.reject)
        
        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addLayout(buttons_layout)
        
        self.setLayout(main_layout)
    
    def load_combobox_data(self):
        """Carga datos para los combobox de productos y usuarios"""
        # Cargar productos
        products_response = self.api_client.get_products()
        if products_response:
            self.products = products_response
            for product in products_response:
                self.product_combo.addItem(product.get('nombre', 'Producto'), product.get('id_producto'))
        
        # Cargar usuarios
        users_response = self.api_client.get_users()
        if users_response:
            self.users = users_response
            for user in users_response:
                self.user_combo.addItem(user.get('nombre', 'Usuario'), user.get('id_usuario'))
    
    def fill_form(self):
        """Rellena el formulario con los datos de la orden"""
        if not self.order_data:
            return
            
        # Producto
        product_id = self.order_data.get("id_producto")
        if product_id:
            index = self.product_combo.findData(product_id)
            if index >= 0:
                self.product_combo.setCurrentIndex(index)
        
        # Cantidad
        self.quantity_input.setValue(int(self.order_data.get("cantidad", 1)))
        
        # Fechas
        if "fecha_inicio" in self.order_data and self.order_data["fecha_inicio"]:
            start_date = QDate.fromString(self.order_data["fecha_inicio"], "yyyy-MM-dd")
            self.start_date_input.setDate(start_date)
        
        if "fecha_fin" in self.order_data and self.order_data["fecha_fin"]:
            end_date = QDate.fromString(self.order_data["fecha_fin"], "yyyy-MM-dd")
            self.end_date_input.setDate(end_date)
        
        # Estado
        if "estado" in self.order_data and self.edit_mode:
            index = self.status_combo.findData(self.order_data["estado"])
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
        
        # Usuario
        user_id = self.order_data.get("id_usuario")
        if user_id:
            index = self.user_combo.findData(user_id)
            if index >= 0:
                self.user_combo.setCurrentIndex(index)
        
        # Notas
        if "notas" in self.order_data:
            self.notes_input.setPlainText(self.order_data["notas"])
    
    def save_order(self):
        """Valida y guarda la orden"""
        # Obtener datos del formulario
        product_id = self.product_combo.currentData()
        user_id = self.user_combo.currentData()
        cantidad = self.quantity_input.value()
        fecha_inicio = self.start_date_input.date().toString("yyyy-MM-dd")
        fecha_fin = self.end_date_input.date().toString("yyyy-MM-dd") if self.end_date_input.date() > self.start_date_input.date() else None
        notas = self.notes_input.toPlainText()
        
        # Validar campos obligatorios
        if not product_id:
            QMessageBox.warning(self, "Error de validación", "Debe seleccionar un producto")
            return
            
        if cantidad <= 0:
            QMessageBox.warning(self, "Error de validación", "La cantidad debe ser mayor que cero")
            return
            
        if not user_id:
            QMessageBox.warning(self, "Error de validación", "Debe seleccionar un usuario responsable")
            return
        
        # Crear diccionario de datos con formato correcto
        order_data = {
            "id_producto": product_id,
            "cantidad": cantidad,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "id_usuario": user_id,
            "notas": notas
        }
        
        # Si estamos editando, incluir el ID y estado
        if self.edit_mode and self.order_data and "id_orden_produccion" in self.order_data:
            order_data["id_orden_produccion"] = self.order_data["id_orden_produccion"]
            if "estado" in self.order_data:
                order_data["estado"] = self.status_combo.currentData()
        
        # Emitir señal con los datos
        self.order_saved.emit(order_data)
        self.accept()

    def _prepare_order_data(self):
        """Prepara los datos de la orden para enviar al servidor"""
        data = {}
        
        if self.order:
            data['id_orden_produccion'] = self.order.id_orden_produccion
            
        data['id_producto'] = self.producto_combo.currentData()
        data['cantidad'] = self.cantidad_spin.value()
        
        # Formatear fecha_inicio
        fecha_inicio = self.fecha_inicio_edit.date().toPyDate()
        data['fecha_inicio'] = fecha_inicio.strftime('%Y-%m-%d')
        
        # Formatear fecha_fin si está establecida
        if not self.fecha_fin_edit.isNull():
            fecha_fin = self.fecha_fin_edit.date().toPyDate()
            data['fecha_fin'] = fecha_fin.strftime('%Y-%m-%d')
        else:
            data['fecha_fin'] = None
            
        data['estado'] = self.estado_combo.currentData()
        data['id_usuario'] = self.usuario_combo.currentData()
        
        return data
