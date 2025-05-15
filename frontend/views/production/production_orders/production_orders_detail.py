from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QScrollArea, QPushButton, QGroupBox, QGridLayout,
                            QMessageBox, QDialog, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon

class ProductionOrderDetailView(QDialog):
    """Vista detallada de una orden de producción"""
    
    # Señales
    edit_requested = pyqtSignal(dict)
    delete_requested = pyqtSignal(int)
    
    def __init__(self, api_client, order_data, parent=None):
        super().__init__(parent)
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.order_data = order_data
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Configuración de la ventana
        self.setWindowTitle(f"Orden de Producción #{self.order_data.get('id_orden_produccion', '')}")
        self.setMinimumSize(600, 400)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Encabezado
        header_layout = QHBoxLayout()
        
        # Icono y Título
        icon_label = QLabel()
        icon_pixmap = QPixmap("resources/icons/production.png")
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
        
        title_label = QLabel(f"Orden de Producción #{self.order_data.get('id_orden_produccion', '')}")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Botones de acción
        action_layout = QHBoxLayout()
        
        edit_button = QPushButton("Editar")
        edit_button.setIcon(QIcon("resources/icons/edit.png"))
        edit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        delete_button = QPushButton("Eliminar")
        delete_button.setIcon(QIcon("resources/icons/delete.png"))
        delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_button.setStyleSheet("color: #d60000;")
        
        close_button = QPushButton("Cerrar")
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        action_layout.addWidget(edit_button)
        action_layout.addWidget(delete_button)
        action_layout.addStretch()
        action_layout.addWidget(close_button)
        
        # Conectar eventos
        edit_button.clicked.connect(lambda: self.edit_requested.emit(self.order_data))
        delete_button.clicked.connect(self.confirm_delete)
        close_button.clicked.connect(self.close)
        
        # Información de la orden
        info_group = QGroupBox("Información de la Orden")
        info_layout = QGridLayout()
        
        # Producto
        info_layout.addWidget(QLabel("Producto:"), 0, 0)
        producto_nombre = self.order_data.get("producto", {}).get("nombre", "N/A") if isinstance(self.order_data.get("producto"), dict) else "N/A"
        producto_label = QLabel(producto_nombre)
        producto_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(producto_label, 0, 1)
        
        # Cantidad
        info_layout.addWidget(QLabel("Cantidad:"), 1, 0)
        cantidad_label = QLabel(str(self.order_data.get("cantidad", "N/A")))
        cantidad_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(cantidad_label, 1, 1)
        
        # Estado
        info_layout.addWidget(QLabel("Estado:"), 1, 2)
        from models.production_order_model import ProductionOrder
        estado_display = ProductionOrder.ESTADOS.get(self.order_data.get("estado", ""), "Desconocido")
        estado_label = QLabel(estado_display)
        estado_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(estado_label, 1, 3)
        
        # Fechas
        info_layout.addWidget(QLabel("Fecha Inicio:"), 2, 0)
        fecha_inicio_label = QLabel(self.order_data.get("fecha_inicio", "N/A"))
        fecha_inicio_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(fecha_inicio_label, 2, 1)
        
        info_layout.addWidget(QLabel("Fecha Fin:"), 2, 2)
        fecha_fin_label = QLabel(self.order_data.get("fecha_fin", "N/A"))
        fecha_fin_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(fecha_fin_label, 2, 3)
        
        # Responsable
        # Responsable
        info_layout.addWidget(QLabel("Responsable:"), 3, 0)
        usuario_nombre = self.order_data.get("usuario", {}).get("nombre", "N/A") if isinstance(self.order_data.get("usuario"), dict) else "N/A"
        responsable_label = QLabel(usuario_nombre)
        responsable_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(responsable_label, 3, 1)
        
        # Notas
        info_layout.addWidget(QLabel("Notas:"), 4, 0, Qt.AlignmentFlag.AlignTop)
        notas_label = QLabel(self.order_data.get("notas", "Sin notas"))
        notas_label.setWordWrap(True)
        notas_label.setStyleSheet("background-color: #f5f5f5; padding: 10px; border-radius: 5px;")
        info_layout.addWidget(notas_label, 4, 1, 1, 3)
        
        info_group.setLayout(info_layout)
        
        # Agregar widgets al layout principal
        main_layout.addLayout(header_layout)
        main_layout.addWidget(info_group)
        main_layout.addStretch()
        main_layout.addLayout(action_layout)
        
        # Establecer el layout
        self.setLayout(main_layout)
    
    def confirm_delete(self):
        """Solicita confirmación para eliminar la orden"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar la orden #{self.order_data.get('id_orden_produccion')}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Emitir señal con el ID de la orden
            self.delete_requested.emit(self.order_data.get("id_orden_produccion"))
            self.close()