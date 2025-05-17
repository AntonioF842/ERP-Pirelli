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

class ProductDetailView(QDialog):
    """Vista detallada de un producto"""
    
    # Señales
    edit_requested = pyqtSignal(dict)  # Emitida al solicitar edición
    delete_requested = pyqtSignal(int) # Emitida al solicitar eliminación
    
    def __init__(self, api_client, product_data, parent=None):
        super().__init__(parent)
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.product_data = product_data
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setWindowTitle(f"Detalles de Producto: {self.product_data.get('nombre', '')}")
        self.setMinimumSize(600, 500)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Encabezado
        self.setup_header(main_layout)
        
        # Información principal
        self.setup_info_section(main_layout)
        
        # Descripción
        self.setup_description_section(main_layout)
        
        # Botones de acción
        self.setup_action_buttons(main_layout)

    def setup_header(self, parent_layout):
        """Configura el encabezado con icono y título"""
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        # Icono
        icon_label = QLabel()
        icon_pixmap = QPixmap("resources/icons/product_large.png")
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio))
        
        # Título y código
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        
        name_label = QLabel(self.product_data.get('nombre', 'Producto'))
        name_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        code_label = QLabel(f"Código: {self.product_data.get('codigo', 'N/A')}")
        code_label.setFont(QFont("Arial", 10))
        code_label.setStyleSheet(f"color: {Theme.SECONDARY_COLOR};")
        
        title_layout.addWidget(name_label)
        title_layout.addWidget(code_label)
        title_layout.addStretch()
        
        header_layout.addWidget(icon_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        parent_layout.addLayout(header_layout)

    def setup_info_section(self, parent_layout):
        """Configura la sección de información básica"""
        info_group = QGroupBox("Información del Producto")
        info_layout = QGridLayout(info_group)
        info_layout.setVerticalSpacing(10)
        info_layout.setHorizontalSpacing(20)
        
        # Categoría
        info_layout.addWidget(QLabel("Categoría:"), 0, 0)
        categoria_label = QLabel(self.product_data.get('categoria', 'N/A'))
        categoria_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(categoria_label, 0, 1)
        
        # Estado
        info_layout.addWidget(QLabel("Estado:"), 0, 2)
        estado = self.product_data.get('estado', 'activo')
        estado_label = QLabel(estado.capitalize())
        estado_label.setStyleSheet(f"font-weight: bold; color: {self.get_status_color(estado)};")
        info_layout.addWidget(estado_label, 0, 3)
        
        # Precio
        info_layout.addWidget(QLabel("Precio:"), 1, 0)
        precio = float(self.product_data.get('precio', 0))
        precio_label = QLabel(f"${precio:,.2f}")
        precio_label.setStyleSheet("font-weight: bold; color: #d60000;")
        info_layout.addWidget(precio_label, 1, 1)
        
        parent_layout.addWidget(info_group)

    def setup_description_section(self, parent_layout):
        """Configura la sección de descripción"""
        desc_group = QGroupBox("Descripción")
        desc_layout = QVBoxLayout(desc_group)
        
        self.desc_browser = QTextBrowser()
        self.desc_browser.setOpenExternalLinks(True)
        self.desc_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 10px;
            }
        """)
        
        desc_layout.addWidget(self.desc_browser)
        parent_layout.addWidget(desc_group)

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
        self.edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.product_data))
        self.delete_btn.clicked.connect(self.confirm_delete)
        self.close_btn.clicked.connect(self.close)

    def load_data(self):
        """Carga los datos del producto en la vista"""
        descripcion = self.product_data.get('descripcion', 'Sin descripción disponible')
        if not descripcion.strip():
            descripcion = "Sin descripción disponible"
        
        # Formatear descripción como HTML
        html_desc = f"<p style='margin: 5px; line-height: 1.5;'>{descripcion}</p>"
        self.desc_browser.setHtml(html_desc)

    def get_status_color(self, status):
        """Devuelve el color según el estado"""
        status = status.lower()
        if status == "activo":
            return Theme.SUCCESS_COLOR
        elif status == "descontinuado":
            return Theme.DANGER_COLOR
        elif status == "oferta":
            return Theme.INFO_COLOR
        return Theme.PRIMARY_COLOR

    def confirm_delete(self):
        """Confirma la eliminación del producto"""
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro que desea eliminar el producto '{self.product_data.get('nombre')}'?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(self.product_data.get('id_producto'))
            self.close()