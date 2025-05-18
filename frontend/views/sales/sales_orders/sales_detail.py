from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QGridLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon
from utils.theme import Theme
import logging

logger = logging.getLogger(__name__)

class SalesDetailView(QDialog):
    """Vista detallada de una venta"""
    
    # Señales
    edit_requested = pyqtSignal(dict)  # Emitida al solicitar edición
    delete_requested = pyqtSignal(int) # Emitida al solicitar eliminación
    
    def __init__(self, api_client, sale_id=None, parent=None):
        super().__init__(parent)
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.sale_id = sale_id
        self.sale_data = {}
        self.detalles = []
        
        self.setup_ui()
        if self.sale_id:
            try:
                self.sale_data = self.api_client.get_sale(self.sale_id)
                self.detalles = self.sale_data.get("detalles", [])
                self.load_data()
            except Exception as e:
                self.show_error(str(e))

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setWindowTitle(f"Detalles de Venta #{self.sale_id or ''}")
        self.setMinimumSize(700, 600)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Encabezado
        self.setup_header(main_layout)
        
        # Información principal
        self.setup_info_section(main_layout)
        
        # Tabla de productos
        self.setup_products_table(main_layout)
        
        # Botones de acción
        self.setup_action_buttons(main_layout)

    def setup_header(self, parent_layout):
        """Configura el encabezado con icono y título"""
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        # Icono
        icon_label = QLabel()
        icon_pixmap = QPixmap("resources/icons/sale_large.png")
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio))
        
        # Título y código
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        
        title_label = QLabel(f"Venta #{self.sale_id or 'Nueva'}")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        client_label = QLabel(f"Cliente: {self.sale_data.get('cliente_nombre', 'N/A')}")
        client_label.setFont(QFont("Arial", 10))
        client_label.setStyleSheet(f"color: {Theme.SECONDARY_COLOR};")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(client_label)
        title_layout.addStretch()
        
        header_layout.addWidget(icon_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        parent_layout.addLayout(header_layout)

    def setup_info_section(self, parent_layout):
        """Configura la sección de información básica"""
        info_group = QGroupBox("Información de la Venta")
        info_layout = QGridLayout(info_group)
        info_layout.setVerticalSpacing(10)
        info_layout.setHorizontalSpacing(20)
        
        # Fecha
        info_layout.addWidget(QLabel("Fecha:"), 0, 0)
        self.fecha_label = QLabel(self.sale_data.get('fecha', 'N/A'))
        self.fecha_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(self.fecha_label, 0, 1)
        
        # Estado
        info_layout.addWidget(QLabel("Estado:"), 0, 2)
        estado = self.sale_data.get('estado', 'pendiente')
        self.estado_label = QLabel(estado.capitalize())
        self.estado_label.setStyleSheet(f"font-weight: bold; color: {self.get_status_color(estado)};")
        info_layout.addWidget(self.estado_label, 0, 3)
        
        # Total
        info_layout.addWidget(QLabel("Total:"), 1, 0)
        total = float(self.sale_data.get('total', 0))
        self.total_label = QLabel(f"${total:,.2f}")
        self.total_label.setStyleSheet("font-weight: bold; color: #d60000;")
        info_layout.addWidget(self.total_label, 1, 1)
        
        # Creado por
        info_layout.addWidget(QLabel("Creado por:"), 1, 2)
        self.creador_label = QLabel(self.sale_data.get('usuario_nombre', 'N/A'))
        self.creador_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(self.creador_label, 1, 3)
        
        parent_layout.addWidget(info_group)

    def setup_products_table(self, parent_layout):
        """Configura la tabla de productos vendidos"""
        products_group = QGroupBox("Productos Vendidos")
        products_layout = QVBoxLayout(products_group)
        
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(4)
        self.products_table.setHorizontalHeaderLabels(["Producto", "Cantidad", "P. Unitario", "Subtotal"])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.products_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.products_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.products_table.setAlternatingRowColors(True)
        self.products_table.verticalHeader().setVisible(False)
        
        products_layout.addWidget(self.products_table)
        parent_layout.addWidget(products_group)

    def setup_action_buttons(self, parent_layout):
        """Configura los botones de acción"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.edit_btn = QPushButton("Editar")
        self.edit_btn.setIcon(QIcon("resources/icons/edit.png"))
        self.edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.delete_btn = QPushButton("Eliminar")
        self.delete_btn.setIcon(QIcon("resources/icons/delete.png"))
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setStyleSheet(f"color: {Theme.DANGER_COLOR};")
        
        self.close_btn = QPushButton("Cerrar")
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        parent_layout.addLayout(button_layout)
        
        # Conectar señales
        self.edit_btn.clicked.connect(self.on_edit_requested)
        self.delete_btn.clicked.connect(self.confirm_delete)
        self.close_btn.clicked.connect(self.close)
        
        # Deshabilitar botones según estado
        estado = self.sale_data.get('estado', '').lower()
        if estado in ['completada', 'cancelada']:
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

    def load_data(self):
        """Carga los datos de la venta en la vista"""
        # Actualizar información básica
        self.fecha_label.setText(self.sale_data.get('fecha', 'N/A'))
        
        estado = self.sale_data.get('estado', 'pendiente')
        self.estado_label.setText(estado.capitalize())
        self.estado_label.setStyleSheet(f"font-weight: bold; color: {self.get_status_color(estado)};")
        
        total = float(self.sale_data.get('total', 0))
        self.total_label.setText(f"${total:,.2f}")
        
        self.creador_label.setText(self.sale_data.get('usuario_nombre', 'N/A'))
        
        # Actualizar tabla de productos
        self.products_table.setRowCount(0)
        for idx, item in enumerate(self.detalles):
            self.products_table.insertRow(idx)
            
            # Producto
            self.products_table.setItem(idx, 0, QTableWidgetItem(str(item.get("producto_nombre", ""))))
            
            # Cantidad
            cantidad_item = QTableWidgetItem(str(item.get("cantidad", 0)))
            cantidad_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.products_table.setItem(idx, 1, cantidad_item)
            
            # Precio Unitario
            precio = float(item.get("precio_unitario", 0))
            precio_item = QTableWidgetItem(f"${precio:,.2f}")
            precio_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.products_table.setItem(idx, 2, precio_item)
            
            # Subtotal
            subtotal = float(item.get("subtotal", precio * item.get("cantidad", 0)))
            subtotal_item = QTableWidgetItem(f"${subtotal:,.2f}")
            subtotal_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.products_table.setItem(idx, 3, subtotal_item)

    def get_status_color(self, status):
        """Devuelve el color según el estado"""
        status = status.lower()
        if status == "pendiente":
            return Theme.WARNING_COLOR
        elif status == "completada":
            return Theme.SUCCESS_COLOR
        elif status == "cancelada":
            return Theme.DANGER_COLOR
        return Theme.PRIMARY_COLOR

    def on_edit_requested(self):
        """Emitir señal para editar la venta"""
        self.edit_requested.emit(self.sale_data)

    def confirm_delete(self):
        """Confirma la eliminación de la venta"""
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro que desea eliminar la venta #{self.sale_id}?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(self.sale_id)
            self.close()

    def show_error(self, msg):
        """Muestra un mensaje de error"""
        QMessageBox.critical(self, "Error", str(msg))