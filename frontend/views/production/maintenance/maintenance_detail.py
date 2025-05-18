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

class MaintenanceDetailView(QDialog):
    """Vista detallada de un registro de mantenimiento"""
    
    # Señales
    edit_requested = pyqtSignal(dict)  # Emitida al solicitar edición
    delete_requested = pyqtSignal(int) # Emitida al solicitar eliminación
    
    def __init__(self, api_client, maintenance_data, parent=None):
        super().__init__(parent)
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.maintenance_data = maintenance_data
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setWindowTitle(f"Detalles de Mantenimiento: #{self.maintenance_data.get('id_mantenimiento', '')}")
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
        icon_pixmap = QPixmap("resources/icons/maintenance_large.png")
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio))
        
        # Título y código
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        
        title_label = QLabel(f"Mantenimiento #{self.maintenance_data.get('id_mantenimiento', 'N/A')}")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        type_label = QLabel("Tipo: " + ("Preventivo" if self.maintenance_data.get("tipo") == "preventivo" else "Correctivo"))
        type_label.setFont(QFont("Arial", 10))
        type_label.setStyleSheet(f"color: {Theme.SECONDARY_COLOR};")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(type_label)
        title_layout.addStretch()
        
        header_layout.addWidget(icon_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        parent_layout.addLayout(header_layout)

    def setup_info_section(self, parent_layout):
        """Configura la sección de información básica"""
        info_group = QGroupBox("Información del Mantenimiento")
        info_layout = QGridLayout(info_group)
        info_layout.setVerticalSpacing(10)
        info_layout.setHorizontalSpacing(20)
        
        # Activo
        info_layout.addWidget(QLabel("Activo:"), 0, 0)
        activo_label = QLabel(self.maintenance_data.get('activo_nombre', 'N/A'))
        activo_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(activo_label, 0, 1)
        
        # Tipo
        info_layout.addWidget(QLabel("Tipo:"), 0, 2)
        tipo = self.maintenance_data.get('tipo', 'N/A')
        tipo_label = QLabel(tipo.capitalize())
        tipo_label.setStyleSheet(f"font-weight: bold; color: {self.get_type_color(tipo)};")
        info_layout.addWidget(tipo_label, 0, 3)
        
        # Fecha
        info_layout.addWidget(QLabel("Fecha:"), 1, 0)
        fecha_label = QLabel(self.maintenance_data.get('fecha', 'N/A'))
        fecha_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(fecha_label, 1, 1)
        
        # Técnico
        info_layout.addWidget(QLabel("Técnico:"), 1, 2)
        tecnico_label = QLabel(self.maintenance_data.get('empleado_nombre', 'No asignado'))
        tecnico_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(tecnico_label, 1, 3)
        
        # Costo
        info_layout.addWidget(QLabel("Costo:"), 2, 0)
        costo = float(self.maintenance_data.get('costo', 0))
        costo_label = QLabel(f"${costo:,.2f}")
        costo_label.setStyleSheet("font-weight: bold; color: #d60000;")
        info_layout.addWidget(costo_label, 2, 1)
        
        parent_layout.addWidget(info_group)

    def setup_description_section(self, parent_layout):
        """Configura la sección de descripción"""
        desc_group = QGroupBox("Descripción del Mantenimiento")
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
        self.edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.maintenance_data))
        self.delete_btn.clicked.connect(self.confirm_delete)
        self.close_btn.clicked.connect(self.close)

    def load_data(self):
        """Carga los datos del mantenimiento en la vista"""
        descripcion = self.maintenance_data.get('descripcion', 'Sin descripción disponible')
        if not descripcion.strip():
            descripcion = "Sin descripción disponible"
        
        # Formatear descripción como HTML
        html_desc = f"<p style='margin: 5px; line-height: 1.5;'>{descripcion}</p>"
        self.desc_browser.setHtml(html_desc)

    def get_type_color(self, tipo):
        """Devuelve el color según el tipo de mantenimiento"""
        tipo = tipo.lower()
        if tipo == "preventivo":
            return Theme.SUCCESS_COLOR
        elif tipo == "correctivo":
            return Theme.WARNING_COLOR
        return Theme.PRIMARY_COLOR

    def confirm_delete(self):
        """Confirma la eliminación del registro"""
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro que desea eliminar el registro de mantenimiento #{self.maintenance_data.get('id_mantenimiento')}?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(self.maintenance_data.get('id_mantenimiento'))
            self.close()