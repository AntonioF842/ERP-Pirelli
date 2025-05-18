from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QGridLayout, QTextBrowser,
    QFrame, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon
from utils.theme import Theme
import logging

logger = logging.getLogger(__name__)

class ProductionOrderDetailView(QDialog):
    """Vista detallada de una orden de producción"""
    
    # Señales
    edit_requested = pyqtSignal(dict)
    delete_requested = pyqtSignal(int)
    
    def __init__(self, api_client, order_data, parent=None):
        super().__init__(parent)
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.order_data = order_data
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setWindowTitle(f"Orden de Producción #{self.order_data.get('id_orden_produccion', '')}")
        self.setMinimumSize(600, 500)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Encabezado
        self.setup_header(main_layout)
        
        # Información principal
        self.setup_info_section(main_layout)
        
        # Notas/observaciones
        self.setup_notes_section(main_layout)
        
        # Botones de acción
        self.setup_action_buttons(main_layout)

    def setup_header(self, parent_layout):
        """Configura el encabezado con icono y título"""
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        # Icono
        icon_label = QLabel()
        icon_pixmap = QPixmap("resources/icons/production_large.png")
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio))
        
        # Título y ID
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        
        title_label = QLabel(f"Orden de Producción #{self.order_data.get('id_orden_produccion', '')}")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        status = self.order_data.get("estado", "planificada")
        status_label = QLabel(f"Estado: {self.get_status_display(status)}")
        status_label.setFont(QFont("Arial", 10))
        status_label.setStyleSheet(f"color: {self.get_status_color(status)};")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(status_label)
        title_layout.addStretch()
        
        header_layout.addWidget(icon_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        parent_layout.addLayout(header_layout)

    def setup_info_section(self, parent_layout):
        """Configura la sección de información básica"""
        info_group = QGroupBox("Información de la Orden")
        info_layout = QGridLayout(info_group)
        info_layout.setVerticalSpacing(10)
        info_layout.setHorizontalSpacing(20)
        
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
        
        # Fecha Inicio
        info_layout.addWidget(QLabel("Fecha Inicio:"), 2, 0)
        fecha_inicio_label = QLabel(self.order_data.get("fecha_inicio", "N/A"))
        fecha_inicio_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(fecha_inicio_label, 2, 1)
        
        # Fecha Fin
        info_layout.addWidget(QLabel("Fecha Fin:"), 2, 2)
        fecha_fin_label = QLabel(self.order_data.get("fecha_fin", "N/A"))
        fecha_fin_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(fecha_fin_label, 2, 3)
        
        # Responsable
        info_layout.addWidget(QLabel("Responsable:"), 3, 0)
        usuario_nombre = self.order_data.get("usuario", {}).get("nombre", "N/A") if isinstance(self.order_data.get("usuario"), dict) else "N/A"
        responsable_label = QLabel(usuario_nombre)
        responsable_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(responsable_label, 3, 1)
        
        parent_layout.addWidget(info_group)

    def setup_notes_section(self, parent_layout):
        """Configura la sección de notas/observaciones"""
        notes_group = QGroupBox("Notas y Observaciones")
        notes_layout = QVBoxLayout(notes_group)
        
        self.notes_browser = QTextBrowser()
        self.notes_browser.setOpenExternalLinks(True)
        self.notes_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 10px;
            }
        """)
        
        notes_layout.addWidget(self.notes_browser)
        parent_layout.addWidget(notes_group)

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
        self.edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.order_data))
        self.delete_btn.clicked.connect(self.confirm_delete)
        self.close_btn.clicked.connect(self.close)

    def load_data(self):
        """Carga los datos de la orden en la vista"""
        notas = self.order_data.get("notas", "Sin notas disponibles")
        if not notas.strip():
            notas = "Sin notas disponibles"
        
        # Formatear notas como HTML
        html_notes = f"<p style='margin: 5px; line-height: 1.5;'>{notas}</p>"
        self.notes_browser.setHtml(html_notes)

    def get_status_display(self, status):
        """Devuelve el nombre legible del estado"""
        status_map = {
            "planificada": "Planificada",
            "en_proceso": "En Proceso",
            "completada": "Completada",
            "cancelada": "Cancelada"
        }
        return status_map.get(status, "Desconocido")

    def get_status_color(self, status):
        """Devuelve el color según el estado"""
        status = status.lower()
        if status == "planificada":
            return Theme.INFO_COLOR
        elif status == "en_proceso":
            return Theme.WARNING_COLOR
        elif status == "completada":
            return Theme.SUCCESS_COLOR
        elif status == "cancelada":
            return Theme.DANGER_COLOR
        return Theme.PRIMARY_COLOR

    def confirm_delete(self):
        """Confirma la eliminación de la orden"""
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro que desea eliminar la orden #{self.order_data.get('id_orden_produccion')}?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(self.order_data.get("id_orden_produccion"))
            self.close()