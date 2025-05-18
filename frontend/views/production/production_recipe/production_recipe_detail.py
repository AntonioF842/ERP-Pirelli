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

class ProductionRecipeDetailView(QDialog):
    """Vista detallada de una receta de producción"""
    
    # Señales
    edit_requested = pyqtSignal(dict)
    delete_requested = pyqtSignal(int)
    
    def __init__(self, api_client, recipe_data, parent=None):
        super().__init__(parent)
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.recipe_data = recipe_data
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setWindowTitle(f"Receta #{self.recipe_data.get('id_receta', '')}")
        self.setMinimumSize(600, 500)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Encabezado
        self.setup_header(main_layout)
        
        # Información principal
        self.setup_info_section(main_layout)
        
        # Notas/observaciones (si las hubiera)
        self.setup_notes_section(main_layout)
        
        # Botones de acción
        self.setup_action_buttons(main_layout)

    def setup_header(self, parent_layout):
        """Configura el encabezado con icono y título"""
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        # Icono
        icon_label = QLabel()
        icon_pixmap = QPixmap("resources/icons/recipe_large.png")
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio))
        
        # Título y ID
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        
        title_label = QLabel(f"Receta #{self.recipe_data.get('id_receta', '')}")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        subtitle_label = QLabel("Detalles de la receta de producción")
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setStyleSheet(f"color: {Theme.SECONDARY_COLOR};")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        title_layout.addStretch()
        
        header_layout.addWidget(icon_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        parent_layout.addLayout(header_layout)

    def setup_info_section(self, parent_layout):
        """Configura la sección de información básica"""
        info_group = QGroupBox("Información de la Receta")
        info_layout = QGridLayout(info_group)
        info_layout.setVerticalSpacing(10)
        info_layout.setHorizontalSpacing(20)
        
        # Producto
        info_layout.addWidget(QLabel("Producto:"), 0, 0)
        producto_nombre = self.recipe_data.get("producto_nombre", "N/A")
        producto_label = QLabel(producto_nombre)
        producto_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(producto_label, 0, 1)
        
        # Material
        info_layout.addWidget(QLabel("Material:"), 1, 0)
        material_nombre = self.recipe_data.get("material_nombre", "N/A")
        material_label = QLabel(material_nombre)
        material_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(material_label, 1, 1)
        
        # Cantidad
        info_layout.addWidget(QLabel("Cantidad:"), 2, 0)
        cantidad = float(self.recipe_data.get("cantidad", 0))
        cantidad_label = QLabel(f"{cantidad:.2f}")
        cantidad_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(cantidad_label, 2, 1)
        
        parent_layout.addWidget(info_group)

    def setup_notes_section(self, parent_layout):
        """Configura la sección de notas (puede extenderse para incluir notas reales)"""
        notes_group = QGroupBox("Detalles Adicionales")
        notes_layout = QVBoxLayout(notes_group)
        
        notes_browser = QTextBrowser()
        notes_browser.setOpenExternalLinks(True)
        notes_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 10px;
            }
        """)
        notes_browser.setHtml("<p style='margin: 5px; line-height: 1.5;'>No hay detalles adicionales registrados para esta receta.</p>")
        
        notes_layout.addWidget(notes_browser)
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
        self.edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.recipe_data))
        self.delete_btn.clicked.connect(self.confirm_delete)
        self.close_btn.clicked.connect(self.close)

    def load_data(self):
        """Carga los datos de la receta en la vista"""
        # Puede extenderse para cargar datos adicionales si es necesario
        pass

    def confirm_delete(self):
        """Confirma la eliminación de la receta"""
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro que desea eliminar la receta #{self.recipe_data.get('id_receta')}?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(self.recipe_data.get("id_receta"))
            self.close()